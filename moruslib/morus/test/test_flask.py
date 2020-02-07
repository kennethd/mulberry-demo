import io
import os
import sys
from unittest import mock

from flask import jsonify

from morus.flask.app import ConfiguredAppArgParser, parse_args, configured_app
from morus.flask.decorators import require_https
from morus.testing.fixtures import mock_stderr, unused_port
from morus.testing.base import MorusTestCase


class TestFlaskTestCase(MorusTestCase):

    def setUp(self):
        self.app = configured_app("testapp")
        self.client = self.app.test_client()

    def test_configured_app_arg_parser(self):
        # make assertions about ArgumentParser itself

        # don't write confusing errors to terminal output
        with mock_stderr() as _stderr:

            # missing required --port
            with mock.patch('sys.exit') as mock_exit:
                ConfiguredAppArgParser.parse_args()
                self.assertTrue(mock_exit.called)
                expect = "required: --port"
                self.assertTrue(expect in _stderr.getvalue().strip())


    def test_parse_args(self):
        pass

    def test_configured_app(self):
        pass


    def test_require_https(self):

        @self.app.route('/https-only')
        @require_https
        def https_only():
            return jsonify({"https-required": True})

        response = self.client.get('/https-only', base_url='https://localhost')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/https-only', base_url='http://localhost')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://localhost/https-only')

