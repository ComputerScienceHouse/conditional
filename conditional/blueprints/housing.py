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
from conditional.util.ldap import ldap_set_active

from conditional.util.flask import render_template

from conditional import db


logger = structlog.get_logger()

housing_bp = Blueprint('housing_bp', __name__)


@housing_bp.route('/housing')
def display_housing():
    log = logger.new(request=request)
    log.info('Display Housing Board')

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
    log = logger.new(request=request)


    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    post_data = request.get_json()
    uid = post_data.get('uid', False)

    if uid:
        if post_data.get('inQueue', False):
            log.info('Add {} to Housing Queue'.format(uid))
            queue_obj = InHousingQueue(uid=uid)
            db.session.add(queue_obj)
        else:
            log.info('Remove {} from Housing Queue'.format(uid))
            InHousingQueue.query.filter_by(uid=uid).delete()

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@housing_bp.route('/housing/update/<rmnumber>', methods=['POST'])
def change_room_numbers(rmnumber):
    log = logger.new(request=request)

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)
    update = request.get_json()

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    # Get the current list of people living on-floor.
    current_students = ldap_get_current_students()

    # Set the new room number for each person in the list.

    for occupant in update["occupants"]:
        if occupant != "":
            account = ldap_get_member(occupant)
            account.roomNumber = rmnumber
            log.info('{} assigned to room {}'.format(occupant, rmnumber))
            ldap_set_active(account)
            log.info('{} marked as active because of room assignment'.format(occupant))
    # Delete any old occupants that are no longer in room.
        for old_occupant in [account for account in current_students
                             if ldap_get_roomnumber(account) == str(rmnumber)
                             and account.uid not in update["occupants"]]:
            log.info('{} removed from room {}'.format(old_occupant.uid, old_occupant.roomNumber))
            old_occupant.roomNumber = None

    return jsonify({"success": True}), 200


@housing_bp.route('/housing/room/<rmnumber>', methods=['GET'])
def get_occupants(rmnumber):

    # Get the current list of people living on-floor.
    current_students = ldap_get_current_students()

    # Find the current occupants of the specified room.
    occupants = [account.uid for account in current_students
                 if ldap_get_roomnumber(account) == str(rmnumber)]
    return jsonify({"room": rmnumber, "occupants": occupants}), 200


@housing_bp.route('/housing', methods=['DELETE'])
def clear_all_rooms():
    log = logger.new(request=request)

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403
    # Get list of current students.
    current_students = ldap_get_current_students()

    # Find the current occupants and clear them.
    for occupant in current_students:
        log.info('{} removed from room {}'.format(occupant.uid, occupant.roomNumber))
        occupant.roomNumber = None
    return jsonify({"success": True}), 200
