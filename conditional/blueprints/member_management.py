from flask import Blueprint
from flask import request
from flask import jsonify

from db.models import FreshmanAccount
from db.models import FreshmanEvalData
from db.models import FreshmanCommitteeAttendance
from db.models import MemberCommitteeAttendance
from db.models import FreshmanSeminarAttendance
from db.models import MemberSeminarAttendance
from db.models import FreshmanHouseMeetingAttendance
from db.models import MemberHouseMeetingAttendance
from db.models import EvalSettings
from db.models import OnFloorStatusAssigned

from util.ldap import ldap_is_eval_director
from util.ldap import ldap_set_roomnumber
from util.ldap import ldap_set_active
from util.ldap import ldap_set_housingpoints
from util.ldap import ldap_get_room_number
from util.ldap import ldap_get_housing_points
from util.ldap import ldap_is_active
from util.ldap import ldap_is_onfloor
from util.flask import render_template
member_management_bp = Blueprint('member_management_bp', __name__)

@member_management_bp.route('/manage')
def display_member_management():
    return ""

@member_management_bp.route('/manage/eval', methods=['POST'])
def member_management_eval():
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()
    housing_form_active = post_data['housing']
    intro_form_active = post_data['intro']
    site_lockdown = post_data['lockdown']

    EvalSettings.query.first().update(
        {
            'housing_form_active': housing_form_active,
            'intro_form_active': intro_form_active,
            'site_lockdown': site_lockdown
        })

    from db.database import db_session
    db_session.flush()
    db_session.commit()
    return ""

@member_management_bp.route('/manage/adduser', methods=['POST'])
def member_management_adduser():
    from db.database import db_session

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    name = post_data['name']
    onfloor_status = post_data['onfloor']

    db_session.add(FreshmanAccount(name, onfloor_status))
    db_session.flush()
    db_session.commit()
    return ""

@member_management_bp.route('/manage/edituser', methods=['POST'])
def member_management_edituser():

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    uid = post_data['uid']
    room_number = post_data['room_number']
    onfloor_status = post_data['onfloor_status']
    housing_points = post_data['housing_points']
    active_member = post_data['active_member']

    ldap_set_roomnumber(uid, room_number)
    #TODO FIXME ADD USER TO ONFLOOR GROUP
    ldap_set_housingpoints(uid, housing_points)
    ldap_set_active(uid, active_member)

    return "ok", 200

@member_management_bp.route('/manage/getuserinfo', methods=['POST'])
def member_management_getuserinfo():
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    uid = post_data['uid']

    return jsonify(
        {
            'room_number': ldap_get_room_number(uid),
            'onfloor_status': ldap_is_onfloor(uid),
            'housing_points': ldap_get_housing_points(uid),
            'active_member': ldap_is_active(uid)
        })
# TODO FIXME XXX Maybe change this to an endpoint where it can be called by our
# user creation script. There's no reason that the evals director should ever
# manually need to do this
@member_management_bp.route('/manage/upgrade_user', methods=['POST'])
def member_management_upgrade_user():
    from db.database import db_session

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    fid = post_data['fid']
    uid = post_data['uid']
    signatures_missed = post_data['sigsMissed']

    acct = FreshmanAccount.query.filter(
            FreshmanAccount.id == fid).first()

    db_session.add(FreshmanEvalData(uid, signatures_missed))

    for fca in FreshmanCommitteeAttendance.query.filter(
        FreshmanCommitteeAttendance.fid == fid):
        db_session.add(MemberCommitteeAttendance(uid, fca.meeting_id))
        # TODO FIXME Do we need to also remove FID stuff?

    for fts in FreshmanSeminarAttendance.query.filter(
        FreshmanSeminarAttendance.fid == fid):
        db_session.add(MemberSeminarAttendance(uid, fca.seminar_id))

    for fhm in FreshmanHouseMeetingAttendance.query.filter(
        FreshmanHouseMeetingAttendance.fid == fid):
        db_session.add(MemberHouseMeetingAttendance(
            uid, fhm.meeting_id, fhm.excuse, fhm.status))

    db_session.add(OnFloorStatusAssigned(uid, datetime.now()))
    db_session.flush()
    db_session.commit()
