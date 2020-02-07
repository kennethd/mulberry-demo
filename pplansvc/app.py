#!/usr/bin/env python3
from pplans.flask.app import configured_app, parse_args

args = parse_args()
app = configured_app('pplansvc', args.dsn, config_module=args.config,
                     debug=args.debug, testing=args.testing)
if args.https:
    app.run(port=args.port, ssl_context=(args.ssl_crt, args.ssl_key))
else:
    app.run(port=args.port)

