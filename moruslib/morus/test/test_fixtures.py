import os
import sys

from morus.testing.base import MorusTestCase
from morus.testing.fixtures import mkportslockdir, mock_stderr, mock_stdout, unused_port


class TestTestingFixtures(MorusTestCase):

    def test_mkportslockdir(self):
        lockdir = mkportslockdir()
        self.assertTrue(os.path.isdir(lockdir))
        self.assertTrue(os.access(lockdir, os.R_OK))
        self.assertTrue(os.access(lockdir, os.W_OK))
        self.assertTrue(os.access(lockdir, os.X_OK))


    def test_unused_port(self):
        lockdir = mkportslockdir()
        lockfile_path = ''
        with unused_port(lockdir) as p:
            lockfile_path = os.path.join(lockdir, str(p))
            self.assertTrue(os.path.exists(lockfile_path))
        self.assertFalse(os.path.exists(lockfile_path))

    def test_mock_stderr(self):
        with mock_stderr() as _stderr:
            print("Test STDERR", file=sys.stderr)
            self.assertEqual(_stderr.getvalue().strip(), "Test STDERR")

    def test_mock_stdout(self):
        with mock_stdout() as _stdout:
            print("Test STDOUT")
            self.assertEqual(_stdout.getvalue().strip(), "Test STDOUT")

