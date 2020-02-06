
from flask import Blueprint, request

from pplans.warranty import gen_warranty, get_warranties


warranties_api = Blueprint('warranties', __name__, url_prefix='/warranties')

@warranties_api.route('/', methods=['GET', 'POST'])
def warranties():

    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        pass

