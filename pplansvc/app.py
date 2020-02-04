#!/usr/bin/env python3
import os

from pplans.flask.app import configured_app, parse_args

args = parse_args()
app = configured_app('pplansvc', args.config, debug=args.debug)
if args.https:
    app.run(port=args.port, ssl_context=(args.ssl_crt, args.ssl_key))
else:
    app.run(port=args.port)

