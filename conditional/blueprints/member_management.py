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
from db.models import HouseMeeting
from db.models import EvalSettings
from db.models import OnFloorStatusAssigned
from db.models import SpringEval

from util.ldap import ldap_is_eval_director
from util.ldap import ldap_is_financial_director
from util.ldap import ldap_set_roomnumber
from util.ldap import ldap_set_active
from util.ldap import ldap_set_housingpoints
from util.ldap import ldap_get_room_number
from util.ldap import ldap_get_housing_points
from util.ldap import ldap_get_active_members
from util.ldap import ldap_get_current_students
from util.ldap import ldap_get_name
from util.ldap import ldap_is_active
from util.ldap import ldap_is_onfloor
from util.flask import render_template

import structlog
import uuid
import csv
import io

logger = structlog.get_logger()

member_management_bp = Blueprint('member_management_bp', __name__)

@member_management_bp.route('/manage')
def display_member_management():
    log = logger.new(request_id=str(uuid.uuid4()))
    log.info('frontend', action='display member management')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and not ldap_is_financial_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403
        
    members = [m['uid'] for m in ldap_get_current_students()]
    member_list = []
    
    for member_uid in members:
        uid = member_uid[0].decode('utf-8')
        name = ldap_get_name(uid)
        active = ldap_is_active(uid)
        onfloor = ldap_is_onfloor(uid)
        room_number = ldap_get_room_number(uid)
        room = room_number if room_number != "N/A" else ""
        hp = ldap_get_housing_points(uid)
        member_list.append({
            "name": name,
            "active": active,
            "onfloor": onfloor,
            "room": room,
            "hp": hp
        })
        
    freshmen = FreshmanAccount.query
    freshmen_list = []
    
    for freshman_user in freshmen:
        name = freshman_user.name
        onfloor = freshman_user.onfloor_status
        room = freshman_user.room_number
        freshmen_list.append({
            "name": name,
            "onfloor": onfloor,
            "room": room
        })
        
    settings = EvalSettings.query.first()
    return render_template(request, "member_management.html",
            username=user_name,
            active=member_list,
            freshmen=freshmen_list,
            site_lockdown=settings.site_lockdown)

@member_management_bp.route('/manage/settings', methods=['POST'])
def member_management_eval():
    log = logger.new(request_id=str(uuid.uuid4()))
    log.info('api', action='submit site-settings')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    if 'housing' in post_data:
        EvalSettings.query.update(
            {
                'housing_form_active': post_data['housing']
            })

    if 'intro' in post_data:
        EvalSettings.query.update(
            {
                'intro_form_active': post_data['intro']
            })

    if 'site_lockdown' in post_data:
        EvalSettings.query.update(
            {
                'site_lockdown': post_data['site_lockdown']
            })

    from db.database import db_session
    db_session.flush()
    db_session.commit()
    return jsonify({"success": True}), 200

@member_management_bp.route('/manage/adduser', methods=['POST'])
def member_management_adduser():
    log = logger.new(request_id=str(uuid.uuid4()))
    log.info('api', action='add fid user')

    from database import db_session

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    name = post_data['name']
    onfloor_status = post_data['onfloor']

    db_session.add(FreshmanAccount(name, onfloor_status))
    db_session.flush()
    db_session.commit()
    return jsonify({"success": True}), 200
    
    
@member_management_bp.route('/manage/uploaduser', methods=['POST'])
def member_management_uploaduser():
    from db.database import db_session
    
    user_name = request.headers.get('x-webauth-user')
    
    if not ldap_is_eval_director(user_name):
        return "must be eval director", 403
        
    f = request.files['file']
    if not f:
        return "No file", 400
    
    try:
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
    
        for new_user in csv_input:
            name = new_user[0]
            onfloor_status = new_user[1]
            
            if new_user[2]:
                room_number = new_user[2]
            else:
                room_number = None
            
            db_session.add(FreshmanAccount(name, onfloor_status, room_number))
            
        db_session.flush()
        db_session.commit()
        return jsonify({"success": True}), 200
    except:
        return "file could not be processed", 400

@member_management_bp.route('/manage/edituser', methods=['POST'])
def member_management_edituser():
    log = logger.new(request_id=str(uuid.uuid4()))
    log.info('api', action='edit uid user')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and not ldap_is_financial_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    uid = post_data['uid']
    active_member = post_data['active_member']

    if ldap_is_eval_director(user_name):
        room_number = post_data['room_number']
        onfloor_status = post_data['onfloor_status']
        housing_points = post_data['housing_points']

        ldap_set_roomnumber(uid, room_number)
        #TODO FIXME ADD USER TO ONFLOOR GROUP
        ldap_set_housingpoints(uid, housing_points)

    # Only update if there's a diff
    if ldap_is_active(uid) != active_member:
        ldap_set_active(uid, active_member)

        from db.database import db_session
        if active_member:
            db_session.add(SpringEval(uid))
        else:
            SpringEval.query.filter(
                SpringEval.uid == uid and
                SpringEval.active).update(
                {
                    'active': False
                })
        db_session.flush()
        db_session.commit()

    return jsonify({"success": True}), 200

@member_management_bp.route('/manage/getuserinfo', methods=['POST'])
def member_management_getuserinfo():
    log = logger.new(request_id=str(uuid.uuid4()))
    log.info('api', action='retreive user info')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and not ldap_is_financial_director(user_name) and user_name != 'loothelion':
        return "must be eval or financial director", 403

    post_data = request.get_json()

    uid = post_data['uid']

    acct = FreshmanAccount.query.filter(
            FreshmanAccount.id == uid).first()

    # if fid
    if acct:
        return jsonify(
            {
                'user': 'fid'
            })

    if ldap_is_eval_director(user_name):

        # missed hm
        def get_hm_date(hm_id):
            return HouseMeeting.query.filter(
                HouseMeeting.id == hm_id).\
                first().date.strftime("%Y-%m-%d")

        missed_hm = [
            {
                'date': get_hm_date(hma.meeting_id),
                'id': hma.meeting_id,
                'excuse': hma.excuse,
                'status': hma.attendance_status
            } for hma in MemberHouseMeetingAttendance.query.filter(
                MemberHouseMeetingAttendance.uid == uid and
                (MemberHouseMeetingAttendance.attendance_status != attendance_enum.Attenaded))]

        hms_missed = []
        for hm in missed_hm:
            if hm['status'] != "Attended":
                hms_missed.append(hm)
        return jsonify(
            {
                'room_number': ldap_get_room_number(uid),
                'onfloor_status': ldap_is_onfloor(uid),
                'housing_points': ldap_get_housing_points(uid),
                'active_member': ldap_is_active(uid),
                'missed_hm': hms_missed,
                'user': 'eval'
            })
    else:
        return jsonify(
            {
                'active_member': ldap_is_active(uid),
                'user': 'financial'
            })

@member_management_bp.route('/manage/edit_hm_excuse', methods=['POST'])
def member_management_edit_hm_excuse():
    log = logger.new(request_id=str(uuid.uuid4()))
    log.info('api', action='edit house meeting excuse')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    hm_id = post_data['id']
    hm_status = post_data['status']
    hm_excuse = post_data['excuse']

    MemberHouseMeetingAttendance.query.filter(
        MemberHouseMeetingAttendance.id == hm_id).update(
        {
            'excuse': hm_excuse,
            'attendance_status': hm_status
        })

    from db.database import db_session
    db_session.flush()
    db_session.commit()
    return jsonify({"success": True}), 200


# TODO FIXME XXX Maybe change this to an endpoint where it can be called by our
# user creation script. There's no reason that the evals director should ever
# manually need to do this
@member_management_bp.route('/manage/upgrade_user', methods=['POST'])
def member_management_upgrade_user():
    log = logger.new(request_id=str(uuid.uuid4()))
    log.info('api', action='convert fid to uid entry')

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

    new_acct = FreshmanEvalData(uid, signatures_missed)
    new_acct.eval_date = acct.eval_date

    db_session.add(new_acct)
    for fca in FreshmanCommitteeAttendance.query.filter(
        FreshmanCommitteeAttendance.fid == fid):
        db_session.add(MemberCommitteeAttendance(uid, fca.meeting_id))
        # XXX this might fail horribly #yoloswag
        db_session.delete(fca)

    for fts in FreshmanSeminarAttendance.query.filter(
        FreshmanSeminarAttendance.fid == fid):
        db_session.add(MemberSeminarAttendance(uid, fca.seminar_id))
        # XXX this might fail horribly #yoloswag
        db_session.delete(fts)

    for fhm in FreshmanHouseMeetingAttendance.query.filter(
        FreshmanHouseMeetingAttendance.fid == fid):
        db_session.add(MemberHouseMeetingAttendance(
            uid, fhm.meeting_id, fhm.excuse, fhm.status))
        # XXX this might fail horribly #yoloswag
        db_session.delete(fhm)

    if acct.onfloor_status:
        db_session.add(OnFloorStatusAssigned(uid, datetime.now()))
        
    if acct.room_number:
        ldap_set_roomnumber(uid, room_number)

    # XXX this might fail horribly #yoloswag
    db_session.delete(acct)

    db_session.flush()
    db_session.commit()
    return jsonify({"success": True}), 200
