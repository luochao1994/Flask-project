
from datetime import datetime

from flask import Blueprint, request, session, jsonify, render_template

from App.models import Order, House

from utils import status_code

order_blueprint = Blueprint('order', __name__)


@order_blueprint.route('/', methods=['POST'])
def order():

    order_dict = request.form

    house_id = order_dict.get('house_id')
    start_time = datetime.strptime(order_dict.get('start_time'), '%Y-%m-%d')
    end_time = datetime.strptime(order_dict.get('end_time'), '%Y-%m-%d')

    if not all([house_id, start_time, end_time]):
        return jsonify(status_code.PARAMS_ERROR)

    if start_time > end_time:
        return jsonify(status_code.ORDER_START_TIME_GT_END_TIME)

    house = House.query.get(house_id)

    order = Order()
    order.user_id = session['user_id']
    order.house_id = house_id
    order.begin_date = start_time
    order.end_date = end_time
    order.house_price = house.price
    order.days = (end_time - start_time).days + 1
    order.amount = order.days * order.house_price

    try:
        order.add_update()
        return jsonify(code=status_code.OK)
    except:
        return jsonify(status_code.DATABASE_ERROR)


@order_blueprint.route('/order/', methods=['GET'])
def orders():

    return render_template('orders.html')
