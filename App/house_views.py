
import os
from flask import Blueprint, render_template, jsonify, session, request

from App.models import User, House, Area, Facility, HouseImage
from utils import status_code

from utils.settings import UPLOAD_DIRS

house_bluprint = Blueprint('house', __name__)


@house_bluprint.route('/myhouse/', methods=['GET'])
def myhouse():
    return render_template('myhouse.html')


@house_bluprint.route('/auth_myhouse/', methods=['GET'])
def auth_myhouse():
    user = User.query.get(session['user_id'])
    if user.id_card:
        houses = House.query.filter(House.user_id==user.id).order_by(House.id.desc())
        hlist_list = []
        for house in houses:
            hlist_list.append(house.to_dict())
        return jsonify(hlist_list=hlist_list, code=status_code.OK)
    else:
        return jsonify(status_code.MYHOUSE_USER_IS_NOT_AUTH)


@house_bluprint.route('/newhouse/', methods=['GET'])
def newhouse():
    return render_template('newhouse.html')


@house_bluprint.route('/area_facility/', methods=['GET'])
def area_facility():

    areas = Area.query.all()
    area_list = [area.to_dict() for area in areas]

    facilitys = Facility.query.all()
    facility_list = [facility.to_dict() for facility in facilitys]

    return jsonify(area_list=area_list, facility_list=facility_list)


@house_bluprint.route('/newhouse/', methods=['POST'])
def user_newhouse():

    house_dict = request.form.to_dict()
    facility_ids = request.form.getlist('facility')

    house = House()
    house.user_id = session['user_id']
    house.title = house_dict.get('title')
    house.price = house_dict.get('price')
    house.area_id = house_dict.get('area_id')
    house.address = house_dict.get('address')
    house.root_count = house_dict.get('root_count')
    house.acreage = house_dict.get('acreage')
    house.unit = house_dict.get('unit')
    house.capacity = house_dict.get('capacity')
    house.beds = house_dict.get('beds')
    house.deposit = house_dict.get('deposit')
    house.min_days = house_dict.get('min_days')
    house.max_days = house_dict.get('max_days')

    if facility_ids:
        facilitys = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        house.facilities = facilitys
    try:
        house.add_update()
    except:
        return jsonify(status_code.DATABASE_ERROR)
    return jsonify(code=status_code.OK, house_id=house.id)


@house_bluprint.route('/images/', methods=['POST'])
def newhouse_images():

    images = request.files.get('house_image')
    house_id = request.form.get('house_id')

    # 保存成功
    url = os.path.join(UPLOAD_DIRS, images.filename)
    images.save(url)

    image_url = os.path.join(os.path.join('/static', 'upload'), images.filename)

    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = image_url
    try:
        house_image.add_update()
    except:
        return jsonify(status_code.DATABASE_ERROR)

    house = House.query.get(house_id)

    if not house.index_image_url:
        house.index_image_url = image_url
        try:
            house.add_update()
        except:
            return jsonify(status_code.DATABASE_ERROR)

    return jsonify(code=status_code.OK, image_url=image_url)


@house_bluprint.route('/detail/', methods=['GET'])
def detail():
    return render_template('detail.html')


@house_bluprint.route('/detail/<int:id>/', methods=['GET'])
def house_detail(id):

    house = House.query.get(id)

    facility_list = house.facilities
    facility_dict_list = [facility.to_dict() for facility in facility_list]

    booking = 1
    if 'user_id' in session:
        house.user_id = session['user_id']
        booking = 0

    return jsonify(house=house.to_full_dict(),
                   facility_list=facility_dict_list,
                   booking=booking,
                   code=status_code.OK)


@house_bluprint.route('/booking/', methods=['GET'])
def booking():
    return render_template('booking.html')
