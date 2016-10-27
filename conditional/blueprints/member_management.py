import csv
import io
import uuid

from datetime import datetime
from functools import lru_cache

import structlog

from flask import Blueprint, request, jsonify, abort

from conditional.models.models import FreshmanAccount
from conditional.models.models import FreshmanEvalData
from conditional.models.models import FreshmanCommitteeAttendance
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import FreshmanSeminarAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import FreshmanHouseMeetingAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import HouseMeeting
from conditional.models.models import EvalSettings
from conditional.models.models import OnFloorStatusAssigned
from conditional.models.models import SpringEval

from conditional.blueprints.cache_management import clear_active_members_cache
from conditional.blueprints.cache_management import clear_onfloor_members_cache
from conditional.blueprints.intro_evals import display_intro_evals

from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_is_financial_director
from conditional.util.ldap import ldap_set_roomnumber
from conditional.util.ldap import ldap_set_active
from conditional.util.ldap import ldap_set_inactive
from conditional.util.ldap import ldap_set_housingpoints
from conditional.util.ldap import ldap_get_room_number
from conditional.util.ldap import ldap_get_housing_points
from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_name
from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_onfloor
from conditional.util.ldap import _ldap_add_member_to_group as ldap_add_member_to_group
from conditional.util.ldap import _ldap_remove_member_from_group as ldap_remove_member_from_group
from conditional.util.ldap import _ldap_is_member_of_group as ldap_is_member_of_group

from conditional.util.flask import render_template
from conditional.models.models import attendance_enum

from conditional import db

logger = structlog.get_logger()

member_management_bp = Blueprint('member_management_bp', __name__)


@lru_cache(maxsize=1024)
def get_members_info():
    members = [m['uid'] for m in ldap_get_current_students()]
    member_list = []
    number_onfloor = 0

    for member_uid in members:
        uid = member_uid[0].decode('utf-8')
        name = ldap_get_name(uid)
        active = ldap_is_active(uid)
        onfloor = ldap_is_onfloor(uid)
        room_number = ldap_get_room_number(uid)
        room = room_number if room_number != "N/A" else ""
        hp = ldap_get_housing_points(uid)
        member_list.append({
            "uid": uid,
            "name": name,
            "active": active,
            "onfloor": onfloor,
            "room": room,
            "hp": hp
        })

        if onfloor:
            number_onfloor += 1

    return member_list, number_onfloor


@member_management_bp.route('/manage')
def display_member_management():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display member management')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and not ldap_is_financial_director(user_name):
        return "must be eval director", 403

    member_list, onfloor_number = get_members_info()

    freshmen = FreshmanAccount.query
    freshmen_list = []

    for freshman_user in freshmen:
        freshmen_list.append({
            "id": freshman_user.id,
            "name": freshman_user.name,
            "onfloor": freshman_user.onfloor_status,
            "room": "" if freshman_user.room_number is None else freshman_user.room_number,
            "eval_date": freshman_user.eval_date
        })

    settings = EvalSettings.query.first()
    if settings:
        lockdown = settings.site_lockdown
        intro_form = settings.intro_form_active
    else:
        lockdown = False
        intro_form = False

    return render_template(request, "member_management.html",
                           username=user_name,
                           active=member_list,
                           num_current=len(member_list),
                           num_active=len(ldap_get_active_members()),
                           num_fresh=len(freshmen_list),
                           num_onfloor=onfloor_number,
                           freshmen=freshmen_list,
                           site_lockdown=lockdown,
                           intro_form=intro_form)


@member_management_bp.route('/manage/settings', methods=['PUT'])
def member_management_eval():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit site settings')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name):
        return "must be eval director", 403

    post_data = request.get_json()

    if 'siteLockdown' in post_data:
        logger.info('backend', action="changed site lockdown setting to %s" % post_data['siteLockdown'])
        EvalSettings.query.update(
            {
                'site_lockdown': post_data['siteLockdown']
            })

    if 'introForm' in post_data:
        logger.info('backend', action="changed intro form setting to %s" % post_data['introForm'])
        EvalSettings.query.update(
            {
                'intro_form_active': post_data['introForm']
            })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/user', methods=['POST'])
def member_management_adduser():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='add fid user')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name):
        return "must be eval director", 403

    post_data = request.get_json()

    name = post_data['name']
    onfloor_status = post_data['onfloor']
    room_number = post_data['roomNumber']

    # empty room numbers should be NULL
    if room_number == "":
        room_number = None

    logger.info('backend', action="add f_%s as onfloor: %s with room_number: %s" % (name, onfloor_status, room_number))
    db.session.add(FreshmanAccount(name, onfloor_status, room_number))
    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/user/upload', methods=['POST'])
def member_management_uploaduser():
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

            db.session.add(FreshmanAccount(name, onfloor_status, room_number))

        db.session.flush()
        db.session.commit()
        return jsonify({"success": True}), 200
    except csv.Error:
        return "file could not be processed", 400


@member_management_bp.route('/manage/user/<uid>', methods=['POST'])
def member_management_edituser(uid):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='edit uid user')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and not ldap_is_financial_director(user_name):
        return "must be eval director", 403

    post_data = request.get_json()

    if not uid.isdigit():
        edit_uid(uid, user_name, post_data)
    else:
        edit_fid(uid, post_data)

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


def edit_uid(uid, user_name, post_data):
    active_member = post_data['activeMember']

    if ldap_is_eval_director(user_name):
        logger.info('backend', action="edit %s room: %s onfloor: %s housepts %s" %
                                      (uid, post_data['roomNumber'], post_data['onfloorStatus'],
                                       post_data['housingPoints']))
        room_number = post_data['roomNumber']
        onfloor_status = post_data['onfloorStatus']
        housing_points = post_data['housingPoints']

        ldap_set_roomnumber(uid, room_number)
        if onfloor_status:
            # If a OnFloorStatusAssigned object exists, don't make another
            if not ldap_is_member_of_group(uid, "onfloor"):
                db.session.add(OnFloorStatusAssigned(uid, datetime.now()))
                ldap_add_member_to_group(uid, "onfloor")
        else:
            for ofs in OnFloorStatusAssigned.query.filter(OnFloorStatusAssigned.uid == uid):
                db.session.delete(ofs)
            db.session.flush()
            db.session.commit()

            if ldap_is_member_of_group(uid, "onfloor"):
                ldap_remove_member_from_group(uid, "onfloor")
        ldap_set_housingpoints(uid, housing_points)

    # Only update if there's a diff
    logger.info('backend', action="edit %s active: %s" % (uid, active_member))
    if ldap_is_active(uid) != active_member:
        if active_member:
            ldap_set_active(uid)
        else:
            ldap_set_inactive(uid)

        if active_member:
            db.session.add(SpringEval(uid))
        else:
            SpringEval.query.filter(
                SpringEval.uid == uid and
                SpringEval.active).update(
                {
                    'active': False
                })
        clear_active_members_cache()


def edit_fid(uid, post_data):
    logger.info('backend', action="edit freshman account %s room: %s onfloor: %s eval_date: %s sig_missed %s" %
                                  (uid, post_data['roomNumber'], post_data['onfloorStatus'],
                                   post_data['evalDate'], post_data['sigMissed']))

    name = post_data['name']

    if post_data['roomNumber'] == "":
        room_number = None
    else:
        room_number = post_data['roomNumber']

    onfloor_status = post_data['onfloorStatus']
    eval_date = post_data['evalDate']

    if post_data['sigMissed'] == "":
        sig_missed = None
    else:
        sig_missed = post_data['sigMissed']

    FreshmanAccount.query.filter(FreshmanAccount.id == uid).update({
        'name': name,
        'eval_date': datetime.strptime(eval_date, "%Y-%m-%d"),
        'onfloor_status': onfloor_status,
        'room_number': room_number,
        'signatures_missed': sig_missed
    })


@member_management_bp.route('/manage/user/<uid>', methods=['GET'])
def member_management_getuserinfo(uid):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve user info')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and not ldap_is_financial_director(user_name):
        return "must be eval or financial director", 403

    acct = None
    if uid.isnumeric():
        acct = FreshmanAccount.query.filter(
            FreshmanAccount.id == uid).first()

    # missed hm
    def get_hm_date(hm_id):
        return HouseMeeting.query.filter(
            HouseMeeting.id == hm_id). \
            first().date.strftime("%Y-%m-%d")

    # if fid
    if acct:
        missed_hm = [
            {
                'date': get_hm_date(hma.meeting_id),
                'id': hma.meeting_id,
                'excuse': hma.excuse,
                'status': hma.attendance_status
            } for hma in FreshmanHouseMeetingAttendance.query.filter(
                FreshmanHouseMeetingAttendance.fid == acct.id and
                (FreshmanHouseMeetingAttendance.attendance_status != attendance_enum.Attended))]

        hms_missed = []
        for hm in missed_hm:
            if hm['status'] != "Attended":
                hms_missed.append(hm)

        return jsonify(
            {
                'id': acct.id,
                'name': acct.name,
                'eval_date': acct.eval_date.strftime("%Y-%m-%d"),
                'missed_hm': hms_missed,
                'onfloor_status': acct.onfloor_status,
                'room_number': acct.room_number,
                'sig_missed': acct.signatures_missed
            }), 200

    if ldap_is_eval_director(user_name):
        missed_hm = [
            {
                'date': get_hm_date(hma.meeting_id),
                'id': hma.meeting_id,
                'excuse': hma.excuse,
                'status': hma.attendance_status
            } for hma in MemberHouseMeetingAttendance.query.filter(
                MemberHouseMeetingAttendance.uid == uid and
                (MemberHouseMeetingAttendance.attendance_status != attendance_enum.Attended))]

        hms_missed = []
        for hm in missed_hm:
            if hm['status'] != "Attended":
                hms_missed.append(hm)
        return jsonify(
            {
                'name': ldap_get_name(uid),
                'room_number': ldap_get_room_number(uid),
                'onfloor_status': ldap_is_onfloor(uid),
                'housing_points': ldap_get_housing_points(uid),
                'active_member': ldap_is_active(uid),
                'missed_hm': hms_missed,
                'user': 'eval'
            }), 200
    else:
        return jsonify(
            {
                'name': ldap_get_name(uid),
                'active_member': ldap_is_active(uid),
                'user': 'financial'
            }), 200


@member_management_bp.route('/manage/user/<fid>', methods=['DELETE'])
def member_management_deleteuser(fid):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='edit fid user')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name):
        return "must be eval director", 403

    if not fid.isdigit():
        return "can only delete freshman accounts", 400

    logger.info('backend', action="delete freshman account %s" % (fid))

    for fca in FreshmanCommitteeAttendance.query.filter(FreshmanCommitteeAttendance.fid == fid):
        db.session.delete(fca)

    for fts in FreshmanSeminarAttendance.query.filter(FreshmanSeminarAttendance.fid == fid):
        db.session.delete(fts)

    for fhm in FreshmanHouseMeetingAttendance.query.filter(FreshmanHouseMeetingAttendance.fid == fid):
        db.session.delete(fhm)

    FreshmanAccount.query.filter(FreshmanAccount.id == fid).delete()

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


# TODO FIXME XXX Maybe change this to an endpoint where it can be called by our
# user creation script. There's no reason that the evals director should ever
# manually need to do this
@member_management_bp.route('/manage/upgrade_user', methods=['POST'])
def member_management_upgrade_user():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='convert fid to uid entry')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name):
        return "must be eval director", 403

    post_data = request.get_json()

    fid = post_data['fid']
    uid = post_data['uid']
    signatures_missed = post_data['sigsMissed']

    logger.info('backend', action="upgrade freshman-%s to %s sigsMissed: %s" %
                                  (fid, uid, signatures_missed))
    acct = FreshmanAccount.query.filter(
        FreshmanAccount.id == fid).first()

    new_acct = FreshmanEvalData(uid, signatures_missed)
    new_acct.eval_date = acct.eval_date

    db.session.add(new_acct)
    for fca in FreshmanCommitteeAttendance.query.filter(FreshmanCommitteeAttendance.fid == fid):
        db.session.add(MemberCommitteeAttendance(uid, fca.meeting_id))
        db.session.delete(fca)

    for fts in FreshmanSeminarAttendance.query.filter(FreshmanSeminarAttendance.fid == fid):
        db.session.add(MemberSeminarAttendance(uid, fts.seminar_id))
        db.session.delete(fts)

    for fhm in FreshmanHouseMeetingAttendance.query.filter(FreshmanHouseMeetingAttendance.fid == fid):
        # Don't duplicate HM attendance records
        mhm = MemberHouseMeetingAttendance.query.filter(
            MemberHouseMeetingAttendance.meeting_id == fhm.meeting_id).first()
        if mhm is None:
            db.session.add(MemberHouseMeetingAttendance(
                uid, fhm.meeting_id, fhm.excuse, fhm.attendance_status))
        else:
            logger.info('backend', action="duplicate house meeting attendance! fid: %s, uid: %s, id: %s" %
                                          (fid, uid, fhm.meeting_id))
        db.session.delete(fhm)

    if acct.onfloor_status:
        db.session.add(OnFloorStatusAssigned(uid, datetime.now()))

    if acct.room_number:
        ldap_set_roomnumber(uid, acct.room_number)

    db.session.delete(acct)

    db.session.flush()
    db.session.commit()

    clear_onfloor_members_cache()

    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/intro_project', methods=['GET'])
def introductory_project():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='show introductory project management')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name):
        return "must be eval director", 403

    return render_template(request,
                           'introductory_project.html',
                           username=user_name,
                           intro_members=display_intro_evals(internal=True))


@member_management_bp.route('/manage/intro_project', methods=['POST'])
def introductory_project_submit():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit introductory project results')

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name):
        return "must be eval director", 403

    post_data = request.get_json()

    if not isinstance(post_data, list):
        abort(400)

    for intro_member in post_data:
        if not isinstance(intro_member, dict):
            abort(400)

        if 'uid' not in intro_member or 'status' not in intro_member:
            abort(400)

        if intro_member['status'] not in ['Passed', 'Pending', 'Failed']:
            abort(400)

        log.info('debug', action='setting status "' + intro_member['status'] + '" for ' + intro_member['uid'])

        FreshmanEvalData.query.filter(FreshmanEvalData.uid == intro_member['uid']).update({
            'freshman_project': intro_member['status']
        })

    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200
