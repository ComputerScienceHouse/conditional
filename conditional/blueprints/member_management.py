import csv
import io
import re

from datetime import datetime

import structlog

from flask import Blueprint, request, jsonify, abort, make_response

from conditional import app

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
from conditional.blueprints.intro_evals import display_intro_evals

from conditional.util.ldap import ldap_is_eval_director
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
from conditional.util.ldap import _ldap_is_member_of_group as ldap_is_member_of_group

from conditional.util.flask import render_template
from conditional.models.models import attendance_enum
from conditional.util.member import get_members_info, get_onfloor_members

from conditional import db, start_of_year

logger = structlog.get_logger()

member_management_bp = Blueprint('member_management_bp', __name__)


@member_management_bp.route('/manage')
def display_member_management():
    log = logger.new(request=request)
    log.info('Display Member Management')

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account) and not ldap_is_financial_director(account):
        return "must be eval director", 403

    member_list = get_members_info()
    onfloor_list = get_onfloor_members()

    co_op_list = [(ldap_get_member(member.uid).displayName, member.semester, member.uid) \
        for member in CurrentCoops.query.filter(
            CurrentCoops.date_created > start_of_year(),
            CurrentCoops.semester != "Neither")]

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
        accept_dues_until = settings.accept_dues_until
    else:
        lockdown = False
        intro_form = False
        accept_dues_until = datetime.now()

    return render_template(request, "member_management.html",
                           username=username,
                           active=member_list,
                           num_current=len(member_list),
                           num_active=len(ldap_get_active_members()),
                           num_fresh=len(freshmen_list),
                           num_onfloor=len(onfloor_list),
                           freshmen=freshmen_list,
                           co_op=co_op_list,
                           site_lockdown=lockdown,
                           accept_dues_until=accept_dues_until,
                           intro_form=intro_form)


@member_management_bp.route('/manage/settings', methods=['PUT'])
def member_management_eval():
    log = logger.new(request=request)

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    post_data = request.get_json()

    if 'siteLockdown' in post_data:
        log.info('Changed Site Lockdown: {}'.format(post_data['siteLockdown']))
        EvalSettings.query.update(
            {
                'site_lockdown': post_data['siteLockdown']
            })

    if 'introForm' in post_data:
        log.info('Changed Intro Form: {}'.format(post_data['introForm']))
        EvalSettings.query.update(
            {
                'intro_form_active': post_data['introForm']
            })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/accept_dues_until', methods=['PUT'])
def member_management_financial():
    log = logger.new(request=request)

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_financial_director(account):
        return "must be financial director", 403

    post_data = request.get_json()

    if 'acceptDuesUntil' in post_data:
        date = datetime.strptime(post_data['acceptDuesUntil'], "%Y-%m-%d")
        log.info('Changed Dues Accepted Until: {}'.format(date))
        EvalSettings.query.update(
            {
                'accept_dues_until': date
            })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/user', methods=['POST'])
def member_management_adduser():
    log = logger.new(request=request)


    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    post_data = request.get_json()

    name = post_data['name']
    onfloor_status = post_data['onfloor']
    room_number = post_data['roomNumber']
    log.info('Create Freshman Account for {}'.format(name))

    # empty room numbers should be NULL
    if room_number == "":
        room_number = None

    db.session.add(FreshmanAccount(name, onfloor_status, room_number))
    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/user/upload', methods=['POST'])
def member_management_uploaduser():
    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)
    log = logger.new(request=request)

    if not ldap_is_eval_director(account):
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

            log.info('Create Freshman Account for {} via CSV Upload'.format(name))
            db.session.add(FreshmanAccount(name, onfloor_status, room_number))

        db.session.flush()
        db.session.commit()
        return jsonify({"success": True}), 200
    except csv.Error:
        return "file could not be processed", 400


@member_management_bp.route('/manage/user/<uid>', methods=['POST'])
def member_management_edituser(uid):

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account) and not ldap_is_financial_director(account):
        return "must be eval director", 403

    if not uid.isdigit():
        edit_uid(uid, request)
    else:
        edit_fid(uid, request)

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


def edit_uid(uid, flask_request):
    log = logger.new(request=flask_request)
    post_data = flask_request.get_json()
    account = ldap_get_member(uid)
    active_member = post_data['activeMember']

    username = flask_request.headers.get('x-webauth-user')
    current_account = ldap_get_member(username)
    if ldap_is_eval_director(current_account):
        room_number = post_data['roomNumber']
        onfloor_status = post_data['onfloorStatus']
        housing_points = post_data['housingPoints']
        log.info('Edit {} - Room: {} On-Floor: {} Points: {}'.format(
            uid,
            post_data['roomNumber'],
            post_data['onfloorStatus'],
            post_data['housingPoints']))

        ldap_set_roomnumber(account, room_number)
        if onfloor_status:
            # If a OnFloorStatusAssigned object exists, don't make another
            if not ldap_is_member_of_group(account, "onfloor"):
                db.session.add(OnFloorStatusAssigned(uid, datetime.now()))
                ldap_add_member_to_group(account, "onfloor")
        else:
            for ofs in OnFloorStatusAssigned.query.filter(OnFloorStatusAssigned.uid == uid):
                db.session.delete(ofs)
            db.session.flush()
            db.session.commit()

            if ldap_is_member_of_group(account, "onfloor"):
                ldap_remove_member_from_group(account, "onfloor")
        ldap_set_housingpoints(account, housing_points)

    # Only update if there's a diff
    log.info('Set {} Active: {}'.format(uid, active_member))
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
    log = logger.new(request=flask_request)
    post_data = flask_request.get_json()
    log.info('Edit freshman-{} - Room: {} On-Floor: {} Eval: {} SigMiss: {}'.format(
        uid,
        post_data['roomNumber'],
        post_data['onfloorStatus'],
        post_data['evalDate'],
        post_data['sigMissed']))

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
    log = logger.new(request=request)
    log.info('Get {}\'s Information'.format(uid))

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account) and not ldap_is_financial_director(account):
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

    if ldap_is_eval_director(ldap_get_member(username)):
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
def member_management_deleteuser(fid):
    log = logger.new(request=request)
    log.info('Delete freshman-{}'.format(fid))

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    if not fid.isdigit():
        return "can only delete freshman accounts", 400

    log.info('backend', action="delete freshman account %s" % fid)

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
    log = logger.new(request=request)

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    post_data = request.get_json()

    fid = post_data['fid']
    uid = post_data['uid']
    signatures_missed = post_data['sigsMissed']

    log.info('Upgrade freshman-{} to Account: {}'.format(fid, uid))

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
            log.info('Duplicate house meeting attendance! fid: {}, uid: {}, id: {}'.format(
                fid,
                uid,
                fhm.meeting_id))
        db.session.delete(fhm)

    new_account = ldap_get_member(uid)
    if acct.onfloor_status:
        db.session.add(OnFloorStatusAssigned(uid, datetime.now()))
        ldap_set_onfloor(new_account)

    if acct.room_number:
        ldap_set_roomnumber(new_account, acct.room_number)

    db.session.delete(acct)

    db.session.flush()
    db.session.commit()

    clear_members_cache()

    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/make_user_active', methods=['POST'])
def member_management_make_user_active():
    log = logger.new(request=request)

    uid = request.headers.get('x-webauth-user')
    account = ldap_get_member(uid)

    if not ldap_is_current_student(account) or ldap_is_active(account):
        return "must be current student and not active", 403

    ldap_set_active(account)
    log.info("Make user {} active".format(uid))

    clear_members_cache()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/intro_project', methods=['GET'])
def introductory_project():
    log = logger.new(request=request)
    log.info('Display Freshmen Project Management')

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    return render_template(request,
                           'introductory_project.html',
                           username=username,
                           intro_members=display_intro_evals(internal=True))


@member_management_bp.route('/manage/intro_project', methods=['POST'])
def introductory_project_submit():
    log = logger.new(request=request)

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
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

        log.info('Freshmen Project {} for {}'.format(intro_member['status'], intro_member['uid']))

        FreshmanEvalData.query.filter(FreshmanEvalData.uid == intro_member['uid']).update({
            'freshman_project': intro_member['status']
        })

    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200

@member_management_bp.route('/member/<uid>', methods=['GET'])
def get_member(uid):
    log = logger.new(request=request)
    log.info('Get {}\'s Information'.format(uid))

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    member = ldap_get_member(uid)
    account_dict = {
        "uid": member.uid,
        "name": member.cn,
        "display": member.displayName
    }

    return jsonify(account_dict), 200

@member_management_bp.route('/manage/active', methods=['DELETE'])
def clear_active_members():
    log = logger.new(request=request)

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403
    # Get the active group.
    members = ldap_get_active_members()

    # Clear the active group.
    for account in members:
        if account.uid != username:
            log.info('Remove {} from Active Status'.format(account.uid))
            ldap_set_inactive(account)
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/export_active_list', methods=['GET'])
def export_active_list():
    sio = io.StringIO()
    csvw = csv.writer(sio)

    active_list = [["Full Name", "RIT Username", "Amount to Charge"]]
    for member in ldap_get_active_members():
        full_name = member.cn
        rit_username = re.search(".*uid=(\\w*)", member.ritDn).group(1)
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
def remove_current_student(uid):
    log = logger.new(request=request)


    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    member = ldap_get_member(uid)
    if request.method == 'DELETE':
        log.info('Remove {} from Current Student'.format(uid))
        ldap_set_non_current_student(member)
    elif request.method == 'POST':
        log.info('Add {} to Current Students'.format(uid))
        ldap_set_current_student(member)
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/new', methods=['GET'])
def new_year():
    log = logger.new(request=request)
    log.info('Display New Year Page')

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    current_students = ldap_get_current_students()


    return render_template(request,
                           'new_year.html',
                           username=username,
                           current_students=current_students)
