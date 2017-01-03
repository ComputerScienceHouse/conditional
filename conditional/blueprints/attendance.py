from datetime import datetime

import uuid
import structlog

from flask import Blueprint, jsonify, redirect, request

from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_is_eboard
from conditional.util.ldap import ldap_get_member

from conditional.models.models import CurrentCoops
from conditional.models.models import CommitteeMeeting
from conditional.models.models import FreshmanCommitteeAttendance
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import TechnicalSeminar
from conditional.models.models import FreshmanSeminarAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import HouseMeeting
from conditional.models.models import FreshmanHouseMeetingAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import FreshmanAccount

from conditional.util.flask import render_template

from conditional import db

logger = structlog.get_logger()

attendance_bp = Blueprint('attendance_bp', __name__)


@attendance_bp.route('/attendance/ts_members')
def get_all_members():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve technical seminar attendance list')

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
def get_non_alumni_non_coop(internal=False):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve house meeting attendance list')

    # Get all active members as a base house meeting attendance.
    active_members = ldap_get_active_members()
    coop_members = [u.uid for u in CurrentCoops.query.all()]

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
            pass

        eligible_members.append(
            {
                'display': account.displayName,
                'value': account.uid,
                'freshman': False
            })

    if internal:
        return eligible_members
    else:
        return jsonify({'members': eligible_members}), 200


@attendance_bp.route('/attendance/cm_members')
def get_non_alumni():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve committee meeting attendance list')

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
def display_attendance_cm():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display committee meeting attendance page')

    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)
    if not ldap_is_eboard(account):
        return redirect("/dashboard")

    return render_template(request,
                           'attendance_cm.html',
                           username=user_name,
                           date=datetime.now().strftime("%Y-%m-%d"))


@attendance_bp.route('/attendance_ts')
def display_attendance_ts():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display technical seminar attendance page')

    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)
    if not ldap_is_eboard(account):
        return redirect("/dashboard")

    return render_template(request,
                           'attendance_ts.html',
                           username=user_name,
                           date=datetime.now().strftime("%Y-%m-%d"))


@attendance_bp.route('/attendance_hm')
def display_attendance_hm():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display house meeting attendance page')

    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)
    if not ldap_is_eval_director(account):
        return redirect("/dashboard")

    return render_template(request,
                           'attendance_hm.html',
                           username=user_name,
                           date=datetime.now().strftime("%Y-%m-%d"),
                           members=get_non_alumni_non_coop(internal=True))


@attendance_bp.route('/attendance/submit/cm', methods=['POST'])
def submit_committee_attendance():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit committee meeting attendance')

    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)
    if not ldap_is_eboard(account):
        return "must be eboard", 403

    post_data = request.get_json()

    committee = post_data['committee']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']
    timestamp = post_data['timestamp']

    timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    meeting = CommitteeMeeting(committee, timestamp)

    db.session.add(meeting)
    db.session.flush()
    db.session.refresh(meeting)

    for m in m_attendees:
        logger.info('backend',
                    action=("gave attendance to %s for %s" % (m, committee))
                    )
        db.session.add(MemberCommitteeAttendance(m, meeting.id))

    for f in f_attendees:
        logger.info('backend',
                    action=("gave attendance to freshman-%s for %s" % (f, committee))
                    )
        db.session.add(FreshmanCommitteeAttendance(f, meeting.id))

    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/submit/ts', methods=['POST'])
def submit_seminar_attendance():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4())
                     )
    log.info('api', action='submit technical seminar attendance')

    user_name = request.headers.get('x-webauth-user')

    account = ldap_get_member(user_name)
    if not ldap_is_eboard(account):
        return "must be eboard", 403

    post_data = request.get_json()

    seminar_name = post_data['name']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']
    timestamp = post_data['timestamp']

    timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    seminar = TechnicalSeminar(seminar_name, timestamp)

    db.session.add(seminar)
    db.session.flush()
    db.session.refresh(seminar)

    for m in m_attendees:
        logger.info('backend',
                    action=("gave attendance to %s for %s" % (m, seminar_name))
                    )
        db.session.add(MemberSeminarAttendance(m, seminar.id))

    for f in f_attendees:
        logger.info('backend',
                    action=("gave attendance to freshman-%s for %s" % (f, seminar_name))
                    )
        db.session.add(FreshmanSeminarAttendance(f, seminar.id))

    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/submit/hm', methods=['POST'])
def submit_house_attendance():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit house meeting attendance')

    # status: Attended | Excused | Absent

    user_name = request.headers.get('x-webauth-user')

    account = ldap_get_member(user_name)
    if not ldap_is_eval_director(account):
        return "must be evals", 403

    post_data = request.get_json()

    timestamp = datetime.strptime(post_data['timestamp'], "%Y-%m-%d")

    meeting = HouseMeeting(timestamp)

    db.session.add(meeting)
    db.session.flush()
    db.session.refresh(meeting)

    if "members" in post_data:
        for m in post_data['members']:
            logger.info('backend',
                        action=(
                            "gave %s to %s for %s house meeting" % (
                                m['status'], m['uid'], timestamp.strftime("%Y-%m-%d")))
                        )
            db.session.add(MemberHouseMeetingAttendance(
                m['uid'],
                meeting.id,
                None,
                m['status']))

    if "freshmen" in post_data:
        for f in post_data['freshmen']:
            logger.info('backend',
                        action=("gave %s to freshman-%s for %s house meeting" % (
                            f['status'], f['id'], timestamp.strftime("%Y-%m-%d")))
                        )
            db.session.add(FreshmanHouseMeetingAttendance(
                f['id'],
                meeting.id,
                None,
                f['status']))

    db.session.commit()
    return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/alter/hm/<uid>/<hid>', methods=['GET'])
def alter_house_attendance(uid, hid):
    user_name = request.headers.get('x-webauth-user')

    account = ldap_get_member(user_name)
    if not ldap_is_eval_director(account):
        return "must be evals", 403

    if not uid.isdigit():
        member_meeting = MemberHouseMeetingAttendance.query.filter(
            MemberHouseMeetingAttendance.uid == uid,
            MemberHouseMeetingAttendance.meeting_id == hid
        ).first()
        member_meeting.attendance_status = "Attended"
        db.session.commit()
        return jsonify({"success": True}), 200
    else:
        freshman_meeting = FreshmanHouseMeetingAttendance.query.filter(
            FreshmanHouseMeetingAttendance.fid == uid,
            FreshmanHouseMeetingAttendance.meeting_id == hid
        ).first()

        freshman_meeting.attendance_status = "Attended"
        db.session.commit()
        return jsonify({"success": True}), 200


@attendance_bp.route('/attendance/alter/hm/<uid>/<hid>', methods=['POST'])
def alter_house_excuse(uid, hid):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='edit house meeting excuse')

    user_name = request.headers.get('x-webauth-user')

    account = ldap_get_member(user_name)
    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    post_data = request.get_json()
    hm_status = post_data['status']
    hm_excuse = post_data['excuse']

    logger.info('backend', action="edit hm %s status: %s excuse: %s" %
                                  (hid, hm_status, hm_excuse))

    if not uid.isdigit():
        MemberHouseMeetingAttendance.query.filter(
            MemberHouseMeetingAttendance.uid == uid,
            MemberHouseMeetingAttendance.meeting_id == hid
        ).update({
            'excuse': hm_excuse,
            'attendance_status': hm_status
        })
    else:
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


@attendance_bp.route('/attendance/history/<page>', methods=['GET'])
def attendance_history(page):


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

    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))

    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)
    if not ldap_is_eboard(account):
        return "must be eboard", 403

    if request.method == 'GET':
        log.info('api', action='view past attendance submitions')
        offset = 0 if int(page) == 1 else ((int(page)-1)*10)
        limit = int(page)*10
        c_meetings = [{"id": m.id,
                       "directorship": m.committee,
                       "date": m.timestamp.strftime("%a %m/%d/%Y"),
                       "attendees": get_meeting_attendees(m.id)
                      } for m in CommitteeMeeting.query.limit(limit).offset(offset)]
        all_cm = [{"meeting_id": m.id,
                   "directorship": m.committee,
                   "date": m.timestamp.strftime("%a %m/%d/%Y"),
                   "attendees": get_meeting_attendees(m.id)
                   } for m in CommitteeMeeting.query.all()]
        if len(all_cm) % 10 != 0:
            total_pages = (int(len(all_cm) / 10) + 1)
        else:
            total_pages = (int(len(all_cm) / 10))
        return render_template(request,
                           'attendance_history.html',
                           username=user_name,
                           history=c_meetings,
                           num_pages=total_pages,
                           current_page=int(page))

@attendance_bp.route('/attendance/alter/cm/<cid>', methods=['POST'])
def alter_committee_attendance(cid):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='edit committee meeting attendance')

    user_name = request.headers.get('x-webauth-user')

    account = ldap_get_member(user_name)
    if not ldap_is_eboard(account):
        return "must be eboard", 403

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

@attendance_bp.route('/attendance/cm/<cid>', methods=['GET'])
def get_cm_attendees(cid):

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
