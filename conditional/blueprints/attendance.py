from datetime import datetime

import structlog
from flask import Blueprint, jsonify, redirect, request

from conditional import db, start_of_year, auth
from conditional.models.models import CommitteeMeeting
from conditional.models.models import CurrentCoops
from conditional.models.models import FreshmanAccount
from conditional.models.models import FreshmanCommitteeAttendance
from conditional.models.models import FreshmanHouseMeetingAttendance
from conditional.models.models import FreshmanSeminarAttendance
from conditional.models.models import HouseMeeting
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import TechnicalSeminar
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_is_eboard
from conditional.util.ldap import ldap_is_eval_director

logger = structlog.get_logger()

attendance_bp = Blueprint('attendance_bp', __name__)


@attendance_bp.route('/attendance/ts_members')
@auth.oidc_auth
@get_user
def get_all_members(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Retrieve Technical Seminar Attendance List')

    members = ldap_get_current_students()

    named_members = [
        {
            'display': f.name,
            'value': f.id,
            'freshman': True
        } for f in FreshmanAccount.query.filter(
            FreshmanAccount.eval_date > datetime.now())]

    for account in members:
        named_members.append(
            {
                'display': account.displayName,
                'value': account.uid,
                'freshman': False
            })

    return jsonify({'members': named_members}), 200


@attendance_bp.route('/attendance/hm_members')
@auth.oidc_auth
@get_user
def get_non_alumni_non_coop(internal=False, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Retrieve House Meeting Attendance List')

    # Get all active members as a base house meeting attendance.
    active_members = ldap_get_active_members()

    if datetime.today() < datetime(start_of_year().year, 12, 31):
        semester = 'Fall'
    else:
        semester = 'Spring'

    coop_members = [u.uid for u in CurrentCoops.query.filter(
        CurrentCoops.date_created > start_of_year(),
        CurrentCoops.semester == semester).all()]

    eligible_members = [
        {
            'display': f.name,
            'value': f.id,
            'freshman': True
        } for f in FreshmanAccount.query.filter(
            FreshmanAccount.eval_date > datetime.now())]

    for account in active_members:
        if account.uid in coop_members:
            # Members who are on co-op don't need to go to house meeting.
            continue

        eligible_members.append(
            {
                'display': account.displayName,
                'value': account.uid,
                'freshman': False
            })

    if internal:
        return eligible_members

    return jsonify({'members': eligible_members}), 200


@attendance_bp.route('/attendance/cm_members')
@auth.oidc_auth
@get_user
def get_non_alumni(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Retrieve Committee Meeting Attendance List')

    current_students = ldap_get_current_students()

    eligible_members = [
        {
            'display': f.name,
            'value': f.id,
            'freshman': True
        } for f in FreshmanAccount.query.filter(
            FreshmanAccount.eval_date > datetime.now())]

    for account in current_students:
        eligible_members.append(
            {
                'display': account.displayName,
                'value': account.uid,
                'freshman': False
            })

    return jsonify({'members': eligible_members}), 200


@attendance_bp.route('/attendance_cm')
@auth.oidc_auth
@get_user
def display_attendance_cm(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Committee Meeting Attendance Page')

    return render_template('attendance_cm.html',
                           username=user_dict['username'],
                           date=datetime.now().strftime("%Y-%m-%d"))


@attendance_bp.route('/attendance_ts')
@auth.oidc_auth
@get_user
def display_attendance_ts(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Technical Seminar Attendance Page')

    return render_template('attendance_ts.html',
                           username=user_dict['username'],
                           date=datetime.now().strftime("%Y-%m-%d"))


@attendance_bp.route('/attendance_hm')
@auth.oidc_auth
@get_user
def display_attendance_hm(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display House Meeting Attendance Page')

    if not ldap_is_eval_director(user_dict['account']):
        return redirect("/dashboard")

    return render_template('attendance_hm.html',
                           username=user_dict['username'],
                           date=datetime.now().strftime("%Y-%m-%d"),
                           members=get_non_alumni_non_coop(internal=True))


@attendance_bp.route('/attendance/submit/cm', methods=['POST'])
@auth.oidc_auth
@get_user
def submit_committee_attendance(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    approved = ldap_is_eboard(user_dict['account'])
    post_data = request.get_json()

    committee = post_data['committee']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']
    timestamp = post_data['timestamp']

    log.info('Submit {} Meeting Attendance'.format(committee))

    timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    meeting = CommitteeMeeting(committee, timestamp, approved)

    db.session.add(meeting)
    db.session.flush()
    db.session.refresh(meeting)

    for m in m_attendees:
        log.info('Gave Attendance to {} for {}'.format(m, committee))
        db.session.add(MemberCommitteeAttendance(m, meeting.id))

    for f in f_attendees:
        log.info('Gave Attendance to freshman-{} for {}'.format(f, committee))
        db.session.add(FreshmanCommitteeAttendance(f, meeting.id))

    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/submit/ts', methods=['POST'])
@auth.oidc_auth
@get_user
def submit_seminar_attendance(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Submit Technical Seminar Attendance')

    approved = ldap_is_eboard(user_dict['account'])

    post_data = request.get_json()

    seminar_name = post_data['name']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']
    timestamp = post_data['timestamp']

    timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    seminar = TechnicalSeminar(seminar_name, timestamp, approved)

    db.session.add(seminar)
    db.session.flush()
    db.session.refresh(seminar)

    for m in m_attendees:
        log.info('Gave Attendance to {} for {}'.format(m, seminar_name))
        db.session.add(MemberSeminarAttendance(m, seminar.id))

    for f in f_attendees:
        log.info('Gave Attendance to freshman-{} for {}'.format(f, seminar_name))
        db.session.add(FreshmanSeminarAttendance(f, seminar.id))

    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/submit/hm', methods=['POST'])
@auth.oidc_auth
@get_user
def submit_house_attendance(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Submit House Meeting Attendance')

    # status: Attended | Excused | Absent

    if not ldap_is_eval_director(user_dict['account']):
        return "must be evals", 403

    post_data = request.get_json()

    timestamp = datetime.strptime(post_data['timestamp'], "%Y-%m-%d")

    meeting = HouseMeeting(timestamp)

    db.session.add(meeting)
    db.session.flush()
    db.session.refresh(meeting)

    if "members" in post_data:
        for m in post_data['members']:
            log.info('Marked {} {} for House Meeting on {}'.format(
                m['uid'],
                m['status'],
                timestamp.strftime("%Y-%m-%d")))
            db.session.add(MemberHouseMeetingAttendance(
                m['uid'],
                meeting.id,
                None,
                m['status']))

    if "freshmen" in post_data:
        for f in post_data['freshmen']:
            log.info('Marked freshman-{} {} for House Meeting on {}'.format(
                f['id'],
                f['status'],
                timestamp.strftime("%Y-%m-%d")))
            db.session.add(FreshmanHouseMeetingAttendance(
                f['id'],
                meeting.id,
                None,
                f['status']))

    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/alter/hm/<uid>/<hid>', methods=['GET'])
@auth.oidc_auth
@get_user
def alter_house_attendance(uid, hid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be evals", 403

    if not uid.isdigit():
        log.info('Mark {} Present for House Meeting ID: {}'.format(uid, hid))
        member_meeting = MemberHouseMeetingAttendance.query.filter(
            MemberHouseMeetingAttendance.uid == uid,
            MemberHouseMeetingAttendance.meeting_id == hid
        ).first()
        member_meeting.attendance_status = "Attended"
        db.session.commit()
        return jsonify({"success": True}), 200

    log.info('Mark freshman-{} Present for House Meeting ID: {}'.format(uid, hid))
    freshman_meeting = FreshmanHouseMeetingAttendance.query.filter(
        FreshmanHouseMeetingAttendance.fid == uid,
        FreshmanHouseMeetingAttendance.meeting_id == hid
    ).first()

    freshman_meeting.attendance_status = "Attended"
    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/alter/hm/<uid>/<hid>', methods=['POST'])
@auth.oidc_auth
@get_user
def alter_house_excuse(uid, hid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    post_data = request.get_json()
    hm_status = post_data['status']
    hm_excuse = post_data['excuse']

    if not uid.isdigit():
        log.info('Mark {} as {} for HM ID: {}'.format(uid, hm_status, hid))
        MemberHouseMeetingAttendance.query.filter(
            MemberHouseMeetingAttendance.uid == uid,
            MemberHouseMeetingAttendance.meeting_id == hid
        ).update({
            'excuse': hm_excuse,
            'attendance_status': hm_status
        })
    else:
        log.info('Mark {} as {} for HM ID: {}'.format(uid, hm_status, hid))
        FreshmanHouseMeetingAttendance.query.filter(
            FreshmanHouseMeetingAttendance.fid == uid,
            FreshmanHouseMeetingAttendance.meeting_id == hid
        ).update({
            'excuse': hm_excuse,
            'attendance_status': hm_status
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/history', methods=['GET'])
@auth.oidc_auth
@get_user
def attendance_history(user_dict=None):

    def get_meeting_attendees(meeting_id):
        attendees = [ldap_get_member(a.uid).displayName for a in
                     MemberCommitteeAttendance.query.filter(
                     MemberCommitteeAttendance.meeting_id == meeting_id).all()]

        for freshman in [a.fid for a in
                         FreshmanCommitteeAttendance.query.filter(
                         FreshmanCommitteeAttendance.meeting_id == meeting_id).all()]:
            attendees.append(FreshmanAccount.query.filter(
                             FreshmanAccount.id == freshman).first().name)
        return attendees

    def get_seminar_attendees(meeting_id):
        attendees = [ldap_get_member(a.uid).displayName for a in
                     MemberSeminarAttendance.query.filter(
                     MemberSeminarAttendance.seminar_id == meeting_id).all()]

        for freshman in [a.fid for a in
                         FreshmanSeminarAttendance.query.filter(
                         FreshmanSeminarAttendance.seminar_id == meeting_id).all()]:
            attendees.append(FreshmanAccount.query.filter(
                             FreshmanAccount.id == freshman).first().name)
        return attendees

    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eboard(user_dict['account']):
        return jsonify({"success": False, "error": "Not EBoard"}), 403


    page = request.args.get('page', 1)
    log.info('View Past Attendance Submitions')
    offset = 0 if int(page) == 1 else ((int(page)-1)*10)
    limit = int(page)*10
    all_cm = [{"id": m.id,
               "name": m.committee,
               "dt_obj": m.timestamp,
               "date": m.timestamp.strftime("%a %m/%d/%Y"),
               "attendees": get_meeting_attendees(m.id),
               "type": "cm"
               } for m in CommitteeMeeting.query.filter(
                   CommitteeMeeting.timestamp > start_of_year(),
                   CommitteeMeeting.approved).all()]
    all_ts = [{"id": m.id,
               "name": m.name,
               "dt_obj": m.timestamp,
               "date": m.timestamp.strftime("%a %m/%d/%Y"),
               "attendees": get_seminar_attendees(m.id),
               "type": "ts"
               } for m in TechnicalSeminar.query.filter(
                   TechnicalSeminar.timestamp > start_of_year(),
                   TechnicalSeminar.approved).all()]
    pend_cm = [{"id": m.id,
                "name": m.committee,
                "dt_obj": m.timestamp,
                "date": m.timestamp.strftime("%a %m/%d/%Y"),
                "attendees": get_meeting_attendees(m.id)
               } for m in CommitteeMeeting.query.filter(
                   CommitteeMeeting.timestamp > start_of_year(),
                   CommitteeMeeting.approved == False).all()] # pylint: disable=singleton-comparison
    pend_ts = [{"id": m.id,
                "name": m.name,
                "dt_obj": m.timestamp,
                "date": m.timestamp.strftime("%a %m/%d/%Y"),
                "attendees": get_seminar_attendees(m.id)
               } for m in TechnicalSeminar.query.filter(
                   TechnicalSeminar.timestamp > start_of_year(),
                   TechnicalSeminar.approved == False).all()] # pylint: disable=singleton-comparison
    all_meetings = sorted((all_cm + all_ts), key=lambda k: k['dt_obj'], reverse=True)[offset:limit]
    if len(all_cm) % 10 != 0:
        total_pages = (int(len(all_cm) / 10) + 1)
    else:
        total_pages = (int(len(all_cm) / 10))
    return render_template('attendance_history.html',
                           username=user_dict['username'],
                           history=all_meetings,
                           pending_cm=pend_cm,
                           pending_ts=pend_ts,
                           num_pages=total_pages,
                           current_page=int(page))


@attendance_bp.route('/attendance/alter/cm/<cid>', methods=['POST'])
@auth.oidc_auth
@get_user
def alter_committee_attendance(cid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Edit Committee Meeting Attendance')

    if not ldap_is_eboard(user_dict['account']):
        return jsonify({"success": False, "error": "Not EBoard"}), 403

    post_data = request.get_json()
    meeting_id = cid
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']

    FreshmanCommitteeAttendance.query.filter(
        FreshmanCommitteeAttendance.meeting_id == meeting_id).delete()

    MemberCommitteeAttendance.query.filter(
        MemberCommitteeAttendance.meeting_id == meeting_id).delete()

    for m in m_attendees:
        db.session.add(MemberCommitteeAttendance(m, meeting_id))

    for f in f_attendees:
        db.session.add(FreshmanCommitteeAttendance(f, meeting_id))

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/alter/ts/<sid>', methods=['POST'])
@auth.oidc_auth
@get_user
def alter_seminar_attendance(sid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Edit Technical Seminar Attendance')

    if not ldap_is_eboard(user_dict['account']):
        return jsonify({"success": False, "error": "Not EBoard"}), 403

    post_data = request.get_json()
    meeting_id = sid
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']

    FreshmanSeminarAttendance.query.filter(
        FreshmanSeminarAttendance.seminar_id == meeting_id).delete()

    MemberSeminarAttendance.query.filter(
        MemberSeminarAttendance.seminar_id == meeting_id).delete()

    for m in m_attendees:
        db.session.add(MemberSeminarAttendance(m, meeting_id))

    for f in f_attendees:
        db.session.add(FreshmanSeminarAttendance(f, meeting_id))

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/ts/<sid>', methods=['GET', 'DELETE'])
@auth.oidc_auth
@get_user
def get_cm_attendees(sid, user_dict=None):
    if request.method == 'GET':
        attendees = [{"value": a.uid,
                      "display": ldap_get_member(a.uid).displayName
                     } for a in
                     MemberSeminarAttendance.query.filter(
                     MemberSeminarAttendance.seminar_id == sid).all()]

        for freshman in [{"value": a.fid,
                          "display": FreshmanAccount.query.filter(FreshmanAccount.id == a.fid).first().name
                         } for a in FreshmanSeminarAttendance.query.filter(
                         FreshmanSeminarAttendance.seminar_id == sid).all()]:
            attendees.append(freshman)
        return jsonify({"attendees": attendees}), 200

    else:
        log = logger.new(request=request, auth_dict=user_dict)
        log.info('Delete Technical Seminar {}'.format(sid))

        if not ldap_is_eboard(user_dict['account']):
            return jsonify({"success": False, "error": "Not EBoard"}), 403

        FreshmanSeminarAttendance.query.filter(
            FreshmanSeminarAttendance.seminar_id == sid).delete()
        MemberSeminarAttendance.query.filter(
            MemberSeminarAttendance.seminar_id == sid).delete()
        TechnicalSeminar.query.filter(
            TechnicalSeminar.id == sid).delete()

        db.session.flush()
        db.session.commit()

        return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/cm/<cid>', methods=['GET', 'DELETE'])
@auth.oidc_auth
@get_user
def get_ts_attendees(cid, user_dict=None):
    if request.method == 'GET':
        attendees = [{"value": a.uid,
                      "display": ldap_get_member(a.uid).displayName
                     } for a in
                     MemberCommitteeAttendance.query.filter(
                     MemberCommitteeAttendance.meeting_id == cid).all()]

        for freshman in [{"value": a.fid,
                          "display": FreshmanAccount.query.filter(FreshmanAccount.id == a.fid).first().name
                         } for a in FreshmanCommitteeAttendance.query.filter(
                         FreshmanCommitteeAttendance.meeting_id == cid).all()]:
            attendees.append(freshman)
        return jsonify({"attendees": attendees}), 200

    else:
        log = logger.new(request=request, auth_dict=user_dict)
        log.info('Delete Committee Meeting {}'.format(cid))

        if not ldap_is_eboard(user_dict['account']):
            return jsonify({"success": False, "error": "Not EBoard"}), 403

        FreshmanCommitteeAttendance.query.filter(
            FreshmanCommitteeAttendance.meeting_id == cid).delete()
        MemberCommitteeAttendance.query.filter(
            MemberCommitteeAttendance.meeting_id == cid).delete()
        CommitteeMeeting.query.filter(
            CommitteeMeeting.id == cid).delete()

        db.session.flush()
        db.session.commit()

        return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/cm/<cid>/approve', methods=['POST'])
@auth.oidc_auth
@get_user
def approve_cm(cid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Approve Committee Meeting {} Attendance'.format(cid))

    if not ldap_is_eboard(user_dict['account']):
        return jsonify({"success": False, "error": "Not EBoard"}), 403

    CommitteeMeeting.query.filter(
        CommitteeMeeting.id == cid).first().approved = True
    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/ts/<sid>/approve', methods=['POST'])
@auth.oidc_auth
@get_user
def approve_ts(sid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Approve Technical Seminar {} Attendance'.format(sid))

    if not ldap_is_eboard(user_dict['account']):
        return jsonify({"success": False, "error": "Not EBoard"}), 403

    TechnicalSeminar.query.filter(
        TechnicalSeminar.id == sid).first().approved = True
    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200
