"""
Related groups of API endpoints are implemented as Flask Blueprints

Blueprints take advantage of OO inheritance to derive new versions from old,
and app mountpoints (url_prefix) to support multiple versions simultaneously

Flask "views" should only be concerned about unpacking requests, delegating
all business logic to a library function, and formatting the library output
into a response
"""
from flask import Blueprint, jsonify, request

from morus.logging import getLogger
from pplans.warranty import (
    WarrantyRuntimeError,
    get_constraints,
    warranty,
    get_warranties,
)


log = getLogger(__name__)

warranties_api = Blueprint('warranties', __name__, url_prefix='/warranties')

@warranties_api.route('/', methods=['GET', 'POST'])
def warranties():

    if request.method == 'GET':
        log.debug(request.args)
        item_sku = request.args.get("item_sku")
        item_type = request.args.get("item_type")
        item_uuid = request.args.get("item_uuid")
        store_uuid = request.args.get("store_uuid")
        try:
            result = get_warranties(store_uuid=store_uuid, item_uuid=item_uuid,
                                    item_type=item_type, item_sku=item_sku)
        except WarrantyRuntimeError as ex:
            result = {"status": str(ex)}
        return jsonify(result)

    elif request.method == 'POST':
        log.debug(request.form)
        item_cost = request.form.get("item_cost")
        item_sku = request.form.get("item_sku")
        item_title = request.form.get("item_title")
        item_type = request.form.get("item_type")
        store_uuid = request.form.get("store_uuid")
        try:
            result = warranty(item_cost, item_sku, item_title, item_type, store_uuid)
        except WarrantyRuntimeError as ex:
            result = {"status": str(ex)}
        return jsonify(result)

@warranties_api.route('/constraints', methods=['GET'])
def constraints():

    if request.method == 'GET':
        log.debug(request.args)
        item_type = request.args.get("item_type")
        item_cost = request.args.get("item_cost")
        try:
            result = get_constraints(item_type, item_cost)
        except WarrantyRuntimeError as ex:
            result = {"status": str(ex)}
        return jsonify(result)

