import argparse
import logging
import os
import tempfile

from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.profiler import ProfilerMiddleware


log = logging.getLogger(__name__)


ConfiguredAppArgParser = argparse.ArgumentParser(description="Argument parser for configured_app")
ConfiguredAppArgParser.add_argument("--config", help="config module (as python path)")
ConfiguredAppArgParser.add_argument("--port", type=int, required=True, help="port number")
ConfiguredAppArgParser.add_argument("--debug", action="store_true", default=False, help="put app into debug mode")
# create key+crt: https://devcenter.heroku.com/articles/ssl-certificate-self
ConfiguredAppArgParser.add_argument("--https", action="store_true", default=False, help="listen via https")
ConfiguredAppArgParser.add_argument("--ssl-key", default="")
ConfiguredAppArgParser.add_argument("--ssl-crt", default="")
# options to enable Flask extensions
ConfiguredAppArgParser.add_argument("--profile", action="store_true", default=False)
ConfiguredAppArgParser.add_argument("--proxy-fix", action="store_true", default=False)
# add support for Flask() kwargs
ConfiguredAppArgParser.add_argument("--static-folder", default="")
ConfiguredAppArgParser.add_argument("--static-url-path", default="")
ConfiguredAppArgParser.add_argument("--static-host", default="")
ConfiguredAppArgParser.add_argument("--template-folder", default="")


def parse_args(parser=ConfiguredAppArgParser):
    (known_args, unknown_args) = parser.parse_known_args()
    log.debug("parse_args: {} known_args: {}".format(parser, known_args))
    log.debug("parse_args: {} ignoring unknown_args: {}".format(parser, unknown_args))
    return known_args


def configured_app(import_name, debug=False, config_module=None, profile=False,
                   proxy_fix=False, **flask_kwargs):
    """instantiate a Flask app

    for details see https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask

     * import_name: the name of your app package
     * debug: put flask app into debug mode
     * config_module: python module path to load config from
     * profile: bool. activate flask.contrib.profiler.ProfilerMiddleware
     * proxy_fix: bool. activate werkzeug.contrib.fixers.ProxyFix

    Environment variables supported:

    FLASKAPP_CONFIG envvar module, values will override those in config_module
    """
    app = Flask(import_name, **flask_kwargs)
    app.secret_key = os.urandom(24)
    # stop noisy warnings
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.debug = debug
    if app.debug:
        app.config['SQLALCHEMY_ECHO'] = True

    if config_module:
        app.config.from_object(config_module)
    if os.getenv("FLASKAPP_CONFIG", False):
        # do not fail silently if configured file cannot be loaded
        app.config.from_envvar("FLASKAPP_CONFIG", silent=False)

    # enable profiling?
    if profile:
        pstat_dir = tempfile.mkdtemp()
        log.debug("PROFILER writing pstat files to {}".format(pstat_dir))
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir=pstat_dir)

    @app.route('/')
    def index():
        return jsonify({"{}-server".format(import_name): "ok"})

    return app

