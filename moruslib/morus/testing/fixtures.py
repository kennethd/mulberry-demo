
import contextlib
import errno
import io
import os
import socket
import sys
import tempfile


def mkportslockdir():
    """create /tmp/ports-lock in a consistent way

    we want to share port-locks directory across multiple processes for
    CI server, potentially multiple users if CI server runs each process
    as owner & multiple services are testing simultaneously"""
    lockdir = os.path.sep.join([tempfile.gettempdir(), 'port-locks'])
    try:
        os.mkdir(lockdir)
        os.chmod(lockdir, 0o777)
    except OSError as ex:
        if ex.errno == errno.EEXIST:
            pass
    return lockdir


@contextlib.contextmanager
def mock_stderr():
    """monkeypatches sys.stderr for duration of context"""
    orig_stderr = sys.stderr
    mock_stderr = io.StringIO()
    try:
        sys.stderr = mock_stderr
        yield sys.stderr
    finally:
        sys.stderr = orig_stderr


@contextlib.contextmanager
def mock_stdout():
    """monkeypatches sys.stdout for duration of context"""
    orig_stdout = sys.stdout
    mock_stdout = io.StringIO()
    try:
        sys.stdout = mock_stdout
        yield sys.stdout
    finally:
        sys.stdout = orig_stdout


@contextlib.contextmanager
def unused_port(lockdir=None):
    """binds to an unused port and returns port number

    closes socket again before returning port number (so caller can use it),
    creating possibility of conflict.  To prevent this, an exclusive lock will
    be obtained to reserve the port in lockdir

    >>> lockdir = mkportslockdir()
    >>> lockfile_path = ''
    >>> with unused_port(lockdir) as p:
    ...     lockfile_path = os.path.join(lockdir, str(p))
    ...     print(lockfile_path, file=sys.stderr, end=' ')
    ...     assert os.path.exists(lockfile_path)
    >>> assert lockfile_path != ''
    >>> assert not os.path.exists(lockfile_path)
    >>> # assert lock is exclusive
    >>> with unused_port(lockdir) as p:
    ...     lockfile_path = os.path.sep.join([lockdir, str(p)])
    ...     assert os.path.exists(lockfile_path)
    ...     f = open(lockfile_path, 'x')
    Traceback (most recent call last):
      ...
    RuntimeError: generator didn't stop after throw()
    >>> # generator didn't stop after throw() happens if generator catches
    >>> # error raised in context; here we intentionally raised the very
    >>> # exception our contextmanager relies on
    """
    if not lockdir:
        lockdir = mkportslockdir()
    try:
        os.mkdir(lockdir)
    except OSError as ex:
        if ex.errno == errno.EEXIST:
            pass

    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # bind w/port 0 will choose random unused port
            s.bind(('localhost', 0))
            addr, port = s.getsockname()
            lockfile_path = os.path.sep.join([lockdir, str(port)])
            try:
                # 'x' mode is new in python 3.3 =~ exclusive open (fail if exists)
                with open(lockfile_path, 'x') as lock:
                    # close socket & yield reserved port number to caller
                    s.close()
                    yield port
            except ValueError as ex:
                # ValueError: mode string must begin with one of 'r', 'w', 'a'
                # or 'U', not 'x'
                import fcntl
                with open(lockfile_path, 'w') as lock:
                    # raises IOError if unable to obtain lock
                    fcntl.lockf(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
                    # close socket & yield reserved port number to caller
                    s.close()
                    yield port
            else:
                # make sure socket gets closed 
                s.close()
            finally:
                # close socket & remove lock
                os.remove(lockfile_path)
            break
        except OSError as ex:
            if ex.errno == errno.EEXIST:
                # if lockfile exists, try again
                print("Lock exists {} {}".format(ex.errno, ex.filename))
                if ex.filename == lockfile_path:
                    s.close()
                    continue

