import csv
import io
from datetime import datetime
from distutils.util import strtobool  # pylint: disable=no-name-in-module,import-error,deprecated-module

import structlog
from flask import Blueprint, request, jsonify, make_response

from conditional import app, get_user, auth, db, start_of_year

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
from conditional.models.models import CurrentCoops

from conditional.blueprints.cache_management import clear_members_cache

from conditional.util.ldap import ldap_is_eval_director, ldap_is_bad_standing
from conditional.util.ldap import ldap_is_financial_director
from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_onfloor
from conditional.util.ldap import ldap_is_current_student
from conditional.util.ldap import ldap_set_roomnumber
from conditional.util.ldap import ldap_set_active
from conditional.util.ldap import ldap_set_inactive
from conditional.util.ldap import ldap_set_onfloor
from conditional.util.ldap import ldap_set_housingpoints
from conditional.util.ldap import ldap_set_current_student
from conditional.util.ldap import ldap_set_non_current_student
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import _ldap_add_member_to_group as ldap_add_member_to_group
from conditional.util.ldap import _ldap_remove_member_from_group as ldap_remove_member_from_group

from conditional.util.member import get_members_info_active_and_onfloor

from conditional.util.flask import render_template
from conditional.models.models import attendance_enum

logger = structlog.get_logger()

member_management_bp = Blueprint('member_management_bp', __name__)


@member_management_bp.route('/manage')
@auth.oidc_auth("default")
@get_user
def display_member_management(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Member Management')

    if not ldap_is_eval_director(user_dict['account']) and not ldap_is_financial_director(user_dict['account']):
        return "must be eval director", 403

    member_list, active_members, onfloor_members = get_members_info_active_and_onfloor()

    freshmen = FreshmanAccount.query
    freshmen_list = []

    for freshman_user in freshmen:  # pylint: disable=not-an-iterable
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
        accept_dues_until = settings.accept_dues_until
    else:
        lockdown = False
        intro_form = False
        accept_dues_until = datetime.now()

    return render_template("member_management.html",
                           username=user_dict['username'],
                           active=member_list,
                           num_current=len(member_list),
                           num_active=len(active_members),
                           num_fresh=len(freshmen_list),
                           num_onfloor=len(onfloor_members),
                           freshmen=freshmen_list,
                           site_lockdown=lockdown,
                           accept_dues_until=accept_dues_until,
                           intro_form=intro_form)


@member_management_bp.route('/manage/settings', methods=['PUT'])
@auth.oidc_auth("default")
@get_user
def member_management_eval(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    post_data = request.get_json()

    if 'siteLockdown' in post_data:
        log.info(f'Changed Site Lockdown: {post_data['siteLockdown']}')
        EvalSettings.query.update(
            {
                'site_lockdown': post_data['siteLockdown']
            })

    if 'introForm' in post_data:
        log.info(f'Changed Intro Form: {post_data['introForm']}')
        EvalSettings.query.update(
            {
                'intro_form_active': post_data['introForm']
            })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/accept_dues_until', methods=['PUT'])
@auth.oidc_auth("default")
@get_user
def member_management_financial(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_financial_director(user_dict['account']):
        return "must be financial director", 403

    post_data = request.get_json()

    if 'acceptDuesUntil' in post_data:
        date = datetime.strptime(post_data['acceptDuesUntil'], "%Y-%m-%d")
        log.info(f'Changed Dues Accepted Until: {date}')
        EvalSettings.query.update(
            {
                'accept_dues_until': date
            })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/user', methods=['POST'])
@auth.oidc_auth("default")
@get_user
def member_management_adduser(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    post_data = request.get_json()

    name = post_data['name']
    onfloor_status = post_data['onfloor']
    room_number = post_data['roomNumber']
    log.info(f'Create Freshman Account for {name}')

    # empty room numbers should be NULL
    if room_number == "":
        room_number = None

    db.session.add(FreshmanAccount(name, onfloor_status, room_number))
    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/user/upload', methods=['POST'])
@auth.oidc_auth("default")
@get_user
def member_management_uploaduser(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    f = request.files['file']
    if not f:
        return "No file", 400

    try:
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)

        for new_user in csv_input:
            name = new_user[0]
            onfloor_status = strtobool(new_user[1])

            if new_user[2]:
                room_number = new_user[2]
            else:
                room_number = None

            if new_user[3]:
                rit_username = new_user[3]
            else:
                rit_username = None

            log.info(f'Create Freshman Account for {name} via CSV Upload')
            db.session.add(FreshmanAccount(name, onfloor_status, room_number, None, rit_username))

        db.session.flush()
        db.session.commit()
        return jsonify({"success": True}), 200
    except csv.Error:
        return "file could not be processed", 400


@member_management_bp.route('/manage/user/<uid>', methods=['POST'])
@auth.oidc_auth("default")
@get_user
def member_management_edituser(uid, user_dict=None):
    if not ldap_is_eval_director(user_dict['account']) and not ldap_is_financial_director(user_dict['account']):
        return "must be eval director", 403

    if not uid.isdigit():
        edit_uid(uid, request, user_dict['username'])
    else:
        edit_fid(uid, request)

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


def edit_uid(uid, flask_request, username):
    log = logger.new(request=flask_request, auth_dict={'username': username})
    post_data = flask_request.get_json()
    account = ldap_get_member(uid)
    active_member = post_data['activeMember']

    current_account = ldap_get_member(username)
    if ldap_is_eval_director(current_account):
        room_number = post_data['roomNumber']
        onfloor_status = post_data['onfloorStatus']
        housing_points = post_data['housingPoints']
        log.info(f'Edit {uid} - Room: {post_data['roomNumber']} On-Floor: {post_data['onfloorStatus']} Points: {post_data['housingPoints']}') #pylint: disable=line-too-long

        ldap_set_roomnumber(account, room_number)
        if onfloor_status:
            # If a OnFloorStatusAssigned object exists, don't make another
            if not ldap_is_onfloor(account):
                db.session.add(OnFloorStatusAssigned(uid, datetime.now()))
                ldap_add_member_to_group(account, "onfloor")
        else:
            for ofs in OnFloorStatusAssigned.query.filter(OnFloorStatusAssigned.uid == uid):
                db.session.delete(ofs)
            db.session.flush()
            db.session.commit()

            if ldap_is_onfloor(account):
                ldap_remove_member_from_group(account, "onfloor")
        ldap_set_housingpoints(account, housing_points)

    # Only update if there's a diff
    log.info(f'Set {uid} Active: {active_member}')
    if ldap_is_active(account) != active_member:
        if active_member:
            ldap_set_active(account)
        else:
            ldap_set_inactive(account)

        if active_member:
            db.session.add(SpringEval(uid))
        else:
            SpringEval.query.filter(
                SpringEval.uid == uid and
                SpringEval.active).update(
                {
                    'active': False
                })
        clear_members_cache()


def edit_fid(uid, flask_request):
    log = logger.new(request=flask_request, auth_dict={'username': uid})
    post_data = flask_request.get_json()

    log.info(f'Edit freshman-{uid} - Room: {post_data['roomNumber']} On-Floor: {post_data['onfloorStatus']} Eval: {post_data['evalDate']} SigMiss: {post_data['sigMissed']}') #pylint: disable=line-too-long


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
@auth.oidc_auth("default")
@get_user
def member_management_getuserinfo(uid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info(f'Get {uid}\'s Information')

    if not ldap_is_eval_director(user_dict['account']) and not ldap_is_financial_director(user_dict['account']):
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

    account = ldap_get_member(uid)

    if ldap_is_eval_director(ldap_get_member(user_dict['username'])):
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
                'name': account.cn,
                'room_number': account.roomNumber,
                'onfloor_status': ldap_is_onfloor(account),
                'housing_points': account.housingPoints,
                'active_member': ldap_is_active(account),
                'missed_hm': hms_missed,
                'user': 'eval'
            }), 200

    return jsonify(
        {
            'name': account.cn,
            'active_member': ldap_is_active(account),
            'user': 'financial'
        }), 200


@member_management_bp.route('/manage/user/<fid>', methods=['DELETE'])
@auth.oidc_auth("default")
@get_user
def member_management_deleteuser(fid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info(f'Delete freshman-{fid}')

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    if not fid.isdigit():
        return "can only delete freshman accounts", 400

    log.info('backend', action=f"delete freshman account {fid}")

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
@auth.oidc_auth("default")
@get_user
def member_management_upgrade_user(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    post_data = request.get_json()

    fid = post_data['fid']
    uid = post_data['uid']
    signatures_missed = post_data['sigsMissed']

    log.info(f'Upgrade freshman-{fid} to Account: {uid}')

    acct = FreshmanAccount.query.filter(
        FreshmanAccount.id == fid).first()

    new_acct = FreshmanEvalData(uid, signatures_missed)
    new_acct.eval_date = acct.eval_date

    db.session.add(new_acct)
    for fca in FreshmanCommitteeAttendance.query.filter(FreshmanCommitteeAttendance.fid == fid):
        db.session.add(MemberCommitteeAttendance(uid, fca.meeting_id))

    for fts in FreshmanSeminarAttendance.query.filter(FreshmanSeminarAttendance.fid == fid):
        db.session.add(MemberSeminarAttendance(uid, fts.seminar_id))

    for fhm in FreshmanHouseMeetingAttendance.query.filter(FreshmanHouseMeetingAttendance.fid == fid):
        # Don't duplicate HM attendance records
        mhm = MemberHouseMeetingAttendance.query.filter(
            MemberHouseMeetingAttendance.meeting_id == fhm.meeting_id,
            MemberHouseMeetingAttendance.uid == uid).first()
        if mhm is None:
            db.session.add(MemberHouseMeetingAttendance(
                uid, fhm.meeting_id, fhm.excuse, fhm.attendance_status))
        else:
            log.info(f'Duplicate house meeting attendance! fid: {fid}, uid: {uid}, id: {fhm.meeting_id}')

    new_account = ldap_get_member(uid)
    if acct.onfloor_status:
        db.session.add(OnFloorStatusAssigned(uid, datetime.now()))
        ldap_set_onfloor(new_account)

    if acct.room_number:
        ldap_set_roomnumber(new_account, acct.room_number)

    db.session.flush()
    db.session.commit()

    db.session.delete(acct)

    db.session.flush()
    db.session.commit()

    clear_members_cache()

    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/make_user_active', methods=['POST'])
@auth.oidc_auth("default")
@get_user
def member_management_make_user_active(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_current_student(user_dict['account']) \
            or ldap_is_active(user_dict['account']) \
            or ldap_is_bad_standing(user_dict['account']):
        return "must be current student, not in bad standing and not active", 403

    ldap_set_active(user_dict['account'])
    log.info(f"Make user {user_dict['username']} active")

    clear_members_cache()
    return jsonify({"success": True}), 200


@member_management_bp.route('/member/<uid>', methods=['GET'])
@auth.oidc_auth("default")
@get_user
def get_member(uid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info(f'Get {uid}\'s Information')

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    member = ldap_get_member(uid)
    account_dict = {
        "uid": member.uid,
        "name": member.cn,
        "display": member.displayName
    }

    return jsonify(account_dict), 200


@member_management_bp.route('/manage/active', methods=['DELETE'])
@auth.oidc_auth("default")
@get_user
def clear_active_members(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403
    # Get the active group.
    members = ldap_get_active_members()

    # Clear the active group.
    for account in members:
        if account.uid != user_dict['username']:
            log.info(f'Remove {account.uid} from Active Status')
            ldap_set_inactive(account)
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/export_active_list', methods=['GET'])
def export_active_list():
    sio = io.StringIO()
    csvw = csv.writer(sio)

    active_list = [["Full Name", "RIT Username", "Amount to Charge"]]
    for member in ldap_get_active_members():
        full_name = member.cn
        # XXX[ljm] this should be renamed in LDAP/IPA schema to be ritUid
        rit_username = member.ritDn
        will_coop = CurrentCoops.query.filter(
            CurrentCoops.date_created > start_of_year(),
            CurrentCoops.uid == member.uid).first()
        dues_per_semester = app.config['DUES_PER_SEMESTER']
        if will_coop:
            dues = dues_per_semester
        else:
            dues = 2 * dues_per_semester
        active_list.append([full_name, rit_username, dues])

    csvw.writerows(active_list)
    output = make_response(sio.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=csh_active_list.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@member_management_bp.route('/manage/current/<uid>', methods=['POST', 'DELETE'])
@auth.oidc_auth("default")
@get_user
def remove_current_student(uid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    member = ldap_get_member(uid)
    if request.method == 'DELETE':
        log.info(f'Remove {uid} from Current Student')
        ldap_set_non_current_student(member)
    elif request.method == 'POST':
        log.info(f'Add {uid} to Current Students')
        ldap_set_current_student(member)
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/new', methods=['GET'])
@auth.oidc_auth("default")
@get_user
def new_year(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display New Year Page')

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    current_students = ldap_get_current_students()

    return render_template('new_year.html',
                           username=user_dict['username'],
                           current_students=current_students)
