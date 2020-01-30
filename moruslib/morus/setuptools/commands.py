
import io
import logging
import os
import shlex
import subprocess
import sys

import psycopg2
import psycopg2.extensions

from setuptools import Command
from setuptools.command.test import test as TestCommand


log = logging.getLogger(__name__)


# for demo, just support pg env vars for config
# https://www.postgresql.org/docs/9.3/libpq-envars.html
PGHOST = os.getenv("PGHOSTADDR") or os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5432")
PGUSER = os.getenv("PGUSER", "postgres")
PSQL_CMD_PFX = ["psql", "--no-password", "--tuples-only", "-d", "postgres", "-c"]

PSQL_QUERY_LIST_DBS = "SELECT datname FROM pg_database ORDER BY datname DESC;"
PSQL_QUERY_LIST_USERS = """
    SELECT
        u.usename AS "User name",
        u.usesysid AS "User ID",
        CASE
            WHEN u.usesuper AND u.usecreatedb THEN CAST('superuser, create database' AS pg_catalog.text)
            WHEN u.usesuper THEN CAST('superuser' AS pg_catalog.text)
            WHEN u.usecreatedb THEN CAST('create database' AS pg_catalog.text)
            ELSE CAST('' AS pg_catalog.text)
        END AS "Attributes"
    FROM pg_catalog.pg_user u
    ORDER BY 1;
    """


def _sudo_cmd(cmd, runas="root", stdout=sys.stdout, stderr=sys.stderr):
    """execute cmd as `runas` user

    cmd is list of shell command tokens

    cmd's STDOUT & STDERR will be written to args passed in here

    returns cmd's returncode, or None if cmd fails to complete
    """
    log.debug("_sudo_cmd: [{}] {}".format(runas, cmd))
    cmd = " ".join(cmd)
    sudo_cmd = ["sudo", "su", "-", runas, "--command", cmd]
    log.debug("_sudo_cmd: {}".format(sudo_cmd))
    proc = subprocess.Popen(sudo_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    ret_code = None
    try:
        (proc_stdout, proc_stderr) = proc.communicate()
        ret_code = proc.returncode
        log.debug("Command returned {}".format(ret_code))
        print(proc_stdout.decode("utf8"), file=stdout)
        print(proc_stderr.decode("utf8"), file=stderr)
    except subprocess.CalledProcessError as ex:
        log.warn("Command failed: {}".format(sudo_cmd))
    return ret_code


class SudoCommand(Command):
    """AbstractBaseClass which you may subclass to execute commands as another user.

    Your run() method should call self.sudo_cmd(cmd), where `cmd` is a
    list of strings (tokens that make up the shell command to be run)

    `--runas` user defaults to "root"
    """

    user_options = [("runas=", None, "User to run process as (default root)")]

    def initialize_options(self):
        self.runas = None

    def finalize_options(self):
        if not self.runas:
            self.runas = "root"

    def sudo_cmd(self, cmd, stdout=sys.stdout, stderr=sys.stderr):
        return _sudo_cmd(cmd, self.runas, stdout=stdout, stderr=stderr)


class SudoPsqlCliCommand(SudoCommand):

    user_options = [
        ("host=", None, "Host of postgresql server (default {})".format(PGHOST)),
        ("port=", None, "Port of postgresql server (default {})".format(PGPORT)),
    ]

    def initialize_options(self):
        super(SudoPsqlCliCommand, self).initialize_options()
        self.host = None
        self.port = None

    def finalize_options(self):
        # do not call super(); do not default runas=root
        if not self.host:
            self.host = PGHOST
        if not self.port:
            self.port = PGPORT
        if not self.runas:
            self.runas = PGUSER

    def run_query(self, query, runas=PGUSER):
        cmd = ["psql", "-d", "postgres", "-c", shlex.quote(query)]
        ret_code = self.sudo_cmd(cmd, runas=runas)
        return ret_code


class ManageDbCommand(SudoPsqlCliCommand):

    user_options = SudoPsqlCliCommand.user_options + [
        ("dbname=", None, "Name of database")
    ]

    def initialize_options(self):
        super(ManageDbCommand, self).initialize_options()
        self.dbname = None

    def finalize_options(self):
        super(ManageDbCommand, self).finalize_options()
        if not self.dbname:
            raise ValueError("dbname is required")


class ManageUserCommand(SudoPsqlCliCommand):

    user_options = SudoPsqlCliCommand.user_options + [
        ("dbuser=", None, "Name of database user")
    ]

    def initialize_options(self):
        super(ManageUserCommand, self).initialize_options()
        self.dbuser = None

    def finalize_options(self):
        super(ManageUserCommand, self).finalize_options()
        if not self.dbuser:
            raise ValueError("dbuser is required")


class CreateDbCommand(ManageDbCommand):
    description = "create a database"

    user_options = ManageDbCommand.user_options + [
        ("owner=", None, "database owner (default {})".format(PGUSER))
    ]

    def initialize_options(self):
        super(CreateDbCommand, self).initialize_options()
        self.owner = None

    def run(self):
        query = ["CREATE", "DATABASE", self.dbname, "ENCODING", "'UTF8'"]
        if self.owner:
            query = query + ["OWNER", self.owner]
        query = " ".join(query)
        cmd = ["psql", "-d", "postgres", "-c", shlex.quote(query)]
        self.sudo_cmd(cmd)


class CreateUserCommand(ManageUserCommand):
    description = "create a database user"

    user_options = ManageUserCommand.user_options + [
        ("dbpass=", None, "Password for dbuser")
    ]

    def initialize_options(self):
        super(CreateUserCommand, self).initialize_options()
        self.dbpass = None

    def finalize_options(self):
        super(CreateUserCommand, self).finalize_options()
        if not self.dbpass:
            raise ValueError("dbpass is required")

    def run(self):
        query = " ".join(
            [
                "CREATE USER",
                self.dbuser,
                "WITH ENCRYPTED PASSWORD",
                "'{}'".format(self.dbpass),
                "CREATEDB",
                "NOCREATEROLE",
                "NOSUPERUSER",
            ]
        )
        cmd = ["psql", "-d", "postgres", "-c", shlex.quote(query)]
        self.sudo_cmd(cmd)


class DropDbCommand(ManageDbCommand):
    description = "drop a database"

    def run(self):
        query = " ".join(["DROP", "DATABASE", self.dbname])
        cmd = ["psql", "-d", "postgres", "-c", shlex.quote(query)]
        self.sudo_cmd(cmd)


class DropUserCommand(ManageUserCommand):
    description = "drop a database user"

    def run(self):
        query = " ".join(["DROP", "USER", self.dbuser])
        cmd = ["psql", "-d", "postgres", "-c", shlex.quote(query)]
        self.sudo_cmd(cmd)


class ListDbsCommand(SudoPsqlCliCommand):
    description = "print list of databases on command line"

    def run(self):
        cmd = ["psql", "-d", "postgres", "-c", shlex.quote(PSQL_QUERY_LIST_DBS)]
        self.sudo_cmd(cmd)


class ListUsersCommand(SudoPsqlCliCommand):
    description = "print list of database users on command line"

    def run(self):
        cmd = ["psql", "-d", "postgres", "-c", shlex.quote(PSQL_QUERY_LIST_USERS)]
        self.sudo_cmd(cmd)


class TestSudoCommand(SudoCommand):
    description = "test that we are are running as root by trying to list /root"

    def run(self):
        self.sudo_cmd(["echo", "Hello"])
        self.sudo_cmd(["whoami"])
        self.sudo_cmd(["ls", "-lh", "/root"])


class PsqlCommand(Command):
    user_options = [
        ("scheme=", None, "DSN scheme (default postgresql)"),
        ("user=", None, "database username (default testuser)"),
        ("pass=", None, "database password (default testpass)"),
        ("host=", None, "database hostname (default {})".format(PGHOST)),
        ("port=", None, "database port (default {})".format(PGPORT)),
        ("dbname=", None, "database name (default test_audit)"),
    ]

    def initialize_options(self):
        self.dsn = None
        # default values match ./ocrolus_models/tests/testing.ini
        # TODO: allow overriding with --config option & parse file
        self.scheme = "postgresql"
        self.user = "audituser"
        self.pwd = "auditpass"
        self.host = PGHOST
        self.port = PGPORT
        self.dbname = "test_audit"

    def finalize_options(self):
        if not self.dsn:
            self.dsn = "{}://{}:{}@{}:{}/{}".format(
                self.scheme, self.user, self.pwd, self.host, self.port, self.dbname
            )
        log.debug("Configured to connect to {}".format(self.dsn))

    def _psycopg2_query(self, query):
        """executes query & returns list of rows"""
        result = None
        conn = psycopg2.connect(self.dsn)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            cur = conn.cursor()
            try:
                cur.execute(query)
                result = cur.fetchall()
            finally:
                cur.close()
        finally:
            conn.close()
        return result

    def _sudo_psql_query(self, query):
        """runs query via `psql`, via sudo"""
        log.debug("{}._sudo_psql_query {}".format(self.__class__.__name__, query))
        ret_val = None
        cmd = PSQL_CMD_PFX + [shlex.quote(query)]
        with io.StringIO() as ioout, io.StringIO() as ioerr:
            try:
                result = _sudo_cmd(cmd, runas=PGUSER, stdout=ioout, stderr=ioerr)
            except Exception as ex:
                sys.exit("unable to run query as {}: {}".format(PGUSER, ex))
            ret_val = (result, ioout.getvalue(), ioerr.getvalue())
        return ret_val

    def run_query(self, query):
        log.debug("run_query: {}".format(query))
        result = self._psycopg2_query(query)
        log.debug("psycopg2 query result: {}".format(result))
        return result


class ListDbsPsqlCommand(PsqlCommand):
    description = "print list of databases on command line"

    def run(self):
        result = self.run_query(PSQL_QUERY_LIST_DBS)
        print(result)


class ListUsersPsqlCommand(PsqlCommand):
    description = "print list of database users on command line"

    def run(self):
        result = self.run_query(PSQL_QUERY_LIST_USERS)
        print(result)


class EnvTestCommand(PsqlCommand):
    """script ends with non-zero exit code on failure"""

    description = "Test local environment is set up correctly"

    def _check_psql(self):
        log.debug("{} check_psql".format(self.__class__.__name__))

        try:
            subprocess.check_call(["which", "psql"])
        except subprocess.CalledProcessError:
            sys.exit("psql not found. is postgresql-client installed?")

        try:
            subprocess.check_call(["which", "pgbench"])
        except subprocess.CalledProcessError:
            sys.exit("pgbench not found. is postgresql server installed?")

    def _check_pguser_access(self):
        log.debug("{} check_pguser_access".format(self.__class__.__name__))
        (ret_code, stdout, stderr) = self._sudo_psql_query("SELECT VERSION();")
        log.debug(
            "return={} stdout=[{}] stderr=[{}]".format(
                ret_code, stdout.strip(), stderr.strip()
            )
        )
        if "PostgreSQL" not in stdout:
            sys.exit("{} user unable to SELECT VERSION()".format(PGUSER))

    def _check_user(self):
        log.debug("{} Checking user: {}".format(self.__class__.__name__, self.user))
        query = "SELECT * FROM pg_user WHERE usename='{}'".format(self.user)
        (result, stdout, stderr) = self._sudo_psql_query(query)
        if self.user not in stdout:
            sys.exit("user {} not found".format(self.user))

    def _check_db(self):
        log.debug("{} check_db {}".format(self.__class__.__name__, self.dbname))
        query = "select * from pg_database where datname = '{}';".format(self.dbname)
        (result, stdout, stderr) = self._sudo_psql_query(query)
        if self.dbname not in stdout:
            sys.exit("db {} not found".format(self.dbname))

    def _check_run_query(self):
        log.debug(
            "{} Checking run_query: {} @ {}".format(
                self.__class__.__name__, self.user, self.dbname
            )
        )
        query = "SELECT 1 FROM pg_roles WHERE rolname='{}'".format(self.user)
        try:
            result = self.run_query(query)
        except psycopg2.OperationalError as ex:
            auth_err = "password authentication failed for user"
            if auth_err in str(ex):
                errstr = " ".join(
                    [
                        "Could not auth user {}.".format(self.user),
                        "See `python setup.py listusers` and `python setup.py createuser`",
                    ]
                )
                log.error(errstr)

        if not result:
            sys.exit(
                "Could not query {} as user {} at {}".format(
                    self.dbname, self.user, self.dsn
                )
            )

    def _check_dsn(self):
        log.debug("{} check_query".format(self.__class__.__name__))
        cmd = ["psql", self.dsn, "--command", "SELECT VERSION();"]
        try:
            version = subprocess.check_output(cmd).decode("utf8")
            log.debug("DSN Connection Successful: version is {}".format(version))
        except subprocess.CalledProcessError as ex:
            sys.exit("check_query Failed: {}".format(ex))

    def run(self):
        self._check_psql()
        self._check_pguser_access()
        self._check_user()
        self._check_db()
        self._check_dsn()


# https://fgimian.github.io/blog/2014/04/27/running-nose-tests-with-plugins-using-the-setuptools-test-command/
class NoseTestCommand(TestCommand):
    """custom nosetests runner to force nose into verbose mode"""

    # TODO: append options from command line
    nose_opts = [
        "--verbose",
        "--nocapture",
        "--with-doctest",
    ]

    def finalize_options(self):
        super(NoseTestCommand, self).finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import nose

        nose.run_exit(argv=["nosetests"] + self.nose_opts)


COMMANDS = {
    "createdb": CreateDbCommand,
    "createuser": CreateUserCommand,
    "dropdb": DropDbCommand,
    "dropuser": DropUserCommand,
    "envtest": EnvTestCommand,
    "listdbs": ListDbsCommand,
    "listusers": ListUsersCommand,
    "psqldbs": ListDbsPsqlCommand,
    "psqlusers": ListUsersPsqlCommand,
    "test": NoseTestCommand,
    "testsudo": TestSudoCommand,
}

