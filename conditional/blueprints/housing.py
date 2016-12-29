import uuid
import structlog

from flask import Blueprint, request, jsonify

from conditional.models.models import FreshmanAccount
from conditional.models.models import InHousingQueue
from conditional.util.housing import get_housing_queue
from conditional.util.ldap import ldap_get_onfloor_members
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_get_roomnumber
from conditional.util.ldap import ldap_get_current_students

from conditional.util.flask import render_template

from conditional import db


logger = structlog.get_logger()

housing_bp = Blueprint('housing_bp', __name__)


@housing_bp.route('/housing')
def display_housing():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display housing')

    # get user data
    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

    housing = {}
    onfloors = [account for account in ldap_get_onfloor_members()]
    onfloor_freshmen = FreshmanAccount.query.filter(
        FreshmanAccount.room_number is not None
    )

    room_list = set()

    for member in onfloors:
        room = ldap_get_roomnumber(member)
        if room in housing and room is not None:
            housing[room].append(member.cn)
            room_list.add(room)
        elif room is not None:
            housing[room] = [member.cn]
            room_list.add(room)

    for f in onfloor_freshmen:
        name = f.name
        room = f.room_number
        if room in housing and room is not None:
            housing[room].append(name)
            room_list.add(room)
        elif room is not None:
            housing[room] = [name]
            room_list.add(room)

    # return names in 'first last (username)' format
    return render_template(request,
                           'housing.html',
                           username=user_name,
                           queue=get_housing_queue(ldap_is_eval_director(account)),
                           housing=housing,
                           room_list=sorted(list(room_list)))


@housing_bp.route('/housing/in_queue', methods=['PUT'])
def change_queue_state():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='add or remove member from housing queue')

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    post_data = request.get_json()
    uid = post_data.get('uid', False)

    if uid:
        if post_data.get('inQueue', False):
            queue_obj = InHousingQueue(uid=uid)
            db.session.add(queue_obj)
        else:
            InHousingQueue.query.filter_by(uid=uid).delete()

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200

@housing_bp.route('/housing/update', methods=['PUT'])
def change_room_numbers():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='mass housing update')

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)
    update_list = request.get_json()

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    # Get the current list of people living on-floor.
    current_students = ldap_get_current_students()

    # Set the new room number for each person in the list.
    for room in update_list:
        for occupant in room["occupants"]:
            account = ldap_get_member(occupant)
            account.roomNumber = str(room["room_number"])
    # Delete any old occupants that are no longer in room.
        for old_occupant in [account for account in current_students
                             if ldap_get_roomnumber(account) == str(room["room_number"])
                             and account.uid not in room["occupants"]]:
            old_occupant.roomNumber = None

    return jsonify({"success": True}), 200
