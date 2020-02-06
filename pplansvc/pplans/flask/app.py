import logging
import os

from morus.flask.app import (
    ConfiguredAppArgParser,
    configured_app as morus_app,
    parse_args as morus_arg_parser
)

from pplans.flask.blueprints import warranties_api
from pplans.models import db
from pplans.warranty import create_demo_data


log = logging.getLogger(__name__)

# example of extending argparser for specific service
ConfiguredAppArgParser.add_argument("--dsn", required=True, help="DSN string")

def parse_args(parser=ConfiguredAppArgParser):
    args = morus_arg_parser(parser=parser)
    log.debug("parse_args: {}".format(args))
    return args

# decorate morus_app to init db & register blueprint(s)
def configured_app(import_name, dsn, debug=False, config_module=None,
                   profile=False, proxy_fix=False):
    app = morus_app(import_name, debug=debug, config_module=config_module,
                    profile=profile, proxy_fix=proxy_fix)
    app.config["SQLALCHEMY_DATABASE_URI"] = dsn
    app.register_blueprint(warranties_api)
    # allow remainder of code to assume single app context is pushed
    app.app_context().push()
    db.init_app(app)
    log.debug("configured_app: {}".format(app))
    # for demo purposes..
    db.drop_all()
    db.create_all()
    create_demo_data()
    return app

