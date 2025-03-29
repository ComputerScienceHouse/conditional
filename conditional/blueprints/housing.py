import structlog
from flask import Blueprint, request, jsonify

from conditional import db, auth
from conditional.models.models import FreshmanAccount
from conditional.models.models import InHousingQueue
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.housing import get_housing_queue
from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_get_onfloor_members
from conditional.util.ldap import ldap_get_roomnumber
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_set_active

logger = structlog.get_logger()

housing_bp = Blueprint('housing_bp', __name__)


@housing_bp.route('/housing')
@auth.oidc_auth("default")
@get_user
def display_housing(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Housing Board')

    housing = {}
    onfloors = ldap_get_onfloor_members()
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
    return render_template('housing.html',
                           username=user_dict['username'],
                           queue=get_housing_queue(ldap_is_eval_director(user_dict['account'])),
                           housing=housing,
                           room_list=sorted(list(room_list)))


@housing_bp.route('/housing/in_queue', methods=['PUT'])
@auth.oidc_auth("default")
@get_user
def change_queue_state(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    post_data = request.get_json()
    uid = post_data.get('uid', False)

    if uid:
        if post_data.get('inQueue', False):
            log.info(f'Add {uid} to Housing Queue')
            queue_obj = InHousingQueue(uid=uid)
            db.session.add(queue_obj)
        else:
            log.info(f'Remove {uid} from Housing Queue')
            InHousingQueue.query.filter_by(uid=uid).delete()

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@housing_bp.route('/housing/update/<rmnumber>', methods=['POST'])
@auth.oidc_auth("default")
@get_user
def change_room_numbers(rmnumber, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    update = request.get_json()

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    # Get the current list of people living on-floor.
    current_students = ldap_get_current_students()

    # Set the new room number for each person in the list.

    for occupant in update["occupants"]:
        if occupant != "":
            account = ldap_get_member(occupant)
            account.roomNumber = rmnumber
            log.info(f'{occupant} assigned to room {rmnumber}')
            ldap_set_active(account)
            log.info(f'{occupant} marked as active because of room assignment')
    # Delete any old occupants that are no longer in room.
        for old_occupant in [account for account in current_students
                             if ldap_get_roomnumber(account) == str(rmnumber)
                             and account.uid not in update["occupants"]]:
            log.info(f'{old_occupant.uid} removed from room {old_occupant.roomNumber}')
            old_occupant.roomNumber = None

    return jsonify({"success": True}), 200


@housing_bp.route('/housing/room/<rmnumber>', methods=['GET'])
@auth.oidc_auth("default")
def get_occupants(rmnumber):

    # Get the current list of people living on-floor.
    current_students = ldap_get_current_students()

    # Find the current occupants of the specified room.
    occupants = [account.uid for account in current_students
                 if ldap_get_roomnumber(account) == str(rmnumber)]
    return jsonify({"room": rmnumber, "occupants": occupants}), 200


@housing_bp.route('/housing', methods=['DELETE'])
@auth.oidc_auth("default")
@get_user
def clear_all_rooms(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403
    # Get list of current students.
    current_students = ldap_get_current_students()

    # Find the current occupants and clear them.
    for occupant in current_students:
        log.info(f'{occupant.uid} removed from room {occupant.roomNumber}')
        occupant.roomNumber = None
    return jsonify({"success": True}), 200
