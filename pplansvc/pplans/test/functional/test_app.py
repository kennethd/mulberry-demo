"""
functional tests test the app interface

database models & requests to external resources should be mocked
"""
import os

from morus.testing.base import MorusTestCase

from pplans.flask.app import DEFAULT_DSN, configured_app

class TestPplansvcApp(MorusTestCase):

    def setUp(self):
        self.dsn = os.environ.get("PPLANSVC_TEST_DSN", DEFAULT_DSN)
        self.app = configured_app('pplansvc', self.dsn)

    def test_heartbeat(self):
        client = self.app.test_client()
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        expect = b'{"pplansvc-server":"ok"}\n'
        self.assertEqual(resp.data, expect)

    def test_warranty(self):
        client = self.app.test_client()
        resp = client.get("/warranties/")
        # no search criteria returns 200 with status message
        self.assertEqual(resp.status_code, 200)
        expect = b'{"status":"Filter criteria is required"}\n'
        self.assertEqual(resp.data, expect)

