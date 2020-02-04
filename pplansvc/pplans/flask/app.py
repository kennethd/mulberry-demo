
from morus.flask.app import (
    ConfiguredAppArgParser,
    configured_app as morus_app,
    parse_args as morus_arg_parser
)

from pplans.flask.blueprints import warranties_api
from pplans.models import db


ConfiguredAppArgParser.add_argument("--dsn", required=True, help="DSN string")

def parse_args(parser=ConfiguredAppArgParser):
    return morus_arg_parser(parser=parser)


# decorate morus_app to init db & register blueprint(s)
def configured_app(import_name, debug=False, config_module=None, profile=False,
                   proxy_fix=False, **flask_kwargs):
    app = morus_app(import_name, debug=debug, config_module=config_module,
                    profile=profile, proxy_fix=proxy_fix, **flask_kwargs)
    app.register_blueprint(warranties_api)
    db.init_app(app)
    return app

