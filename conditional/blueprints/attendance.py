from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request

from util.ldap import ldap_get_non_alumni_members
from util.ldap import ldap_get_name
from util.ldap import ldap_get_current_students
from util.ldap import ldap_is_eboard
from util.ldap import ldap_is_eval_director
from util.ldap import ldap_get_active_members

from db.models import CurrentCoops
from db.models import CommitteeMeeting
from db.models import FreshmanCommitteeAttendance
from db.models import MemberCommitteeAttendance
from db.models import TechnicalSeminar
from db.models import FreshmanSeminarAttendance
from db.models import MemberSeminarAttendance
from db.models import HouseMeeting
from db.models import FreshmanHouseMeetingAttendance
from db.models import MemberHouseMeetingAttendance
from db.models import FreshmanAccount
from datetime import datetime

from util.flask import render_template

import structlog
import uuid

logger = structlog.get_logger()

attendance_bp = Blueprint('attendance_bp', __name__)

def get_name(m):
    first = None
    if 'givenName' in m:
        first = m['givenName'][0].decode('utf-8')
    else:
        first = ""
    last = None
    if 'sn' in m:
        last = m['sn'][0].decode('utf-8')
    else:
        last = ""
    return "{first} {last}".format(first=first, last=last)

@attendance_bp.route('/attendance/ts_members')
def get_all_members():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve techincal seminar attendance list')

    members = ldap_get_current_students()

    named_members = [
        {
            'display': f.name,
            'value': f.id,
            'freshman': True
        } for f in FreshmanAccount.query.filter(
            FreshmanAccount.eval_date > datetime.now())]

    for m in members:
        uid = m['uid'][0].decode('utf-8')
        name = "{name} ({uid})".format(name=get_name(m), uid=uid)

        named_members.append(
            {
                'display': name,
                'value': uid,
                'freshman': False
            })

    return jsonify({'members': named_members}), 200

@attendance_bp.route('/attendance/hm_members')
def get_non_alumni_non_coop(internal=False):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve house meeting attendance list')

    # Only Members Who Have Paid Dues Are Required to
    # go to house meetings
    non_alumni_members = ldap_get_active_members()
    coop_members = [u.username for u in CurrentCoops.query.all()]

    named_members = [
        {
            'display': f.name,
            'value': f.id,
            'freshman': True
        } for f in FreshmanAccount.query.filter(
            FreshmanAccount.eval_date > datetime.now())]

    for m in non_alumni_members:
        uid = m['uid'][0].decode('utf-8')

        if uid in coop_members:
            continue
        name = "{name} ({uid})".format(name=get_name(m), uid=uid)

        named_members.append(
            {
                'display': name,
                'value': uid,
                'freshman': False
            })

    if internal:
        return named_members
    else:
        return jsonify({'members': named_members}), 200


@attendance_bp.route('/attendance/cm_members')
def get_non_alumni():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve committee meeting attendance list')

    non_alumni_members = ldap_get_current_students()

    named_members = [
        {
            'display': f.name,
            'value': f.id,
            'freshman': True
        } for f in FreshmanAccount.query.filter(
            FreshmanAccount.eval_date > datetime.now())]
    for m in non_alumni_members:
        uid = m['uid'][0].decode('utf-8')
        name = "{name} ({uid})".format(name=get_name(m), uid=uid)

        named_members.append(
            {
                'display': name,
                'value': uid,
                'freshman': False
            })

    return jsonify({'members': named_members}), 200

@attendance_bp.route('/attendance_cm')
def display_attendance_cm():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('frontend', action='display committee meeting attendance page')

    user_name = request.headers.get('x-webauth-user')
    if not ldap_is_eboard(user_name):
        return redirect("/dashboard")


    return render_template(request,
                           'attendance_cm.html',
                           username = user_name,
                           date = datetime.utcnow().strftime("%Y-%m-%d"))

@attendance_bp.route('/attendance_ts')
def display_attendance_ts():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('frontend', action='display technical seminar attendance page')

    user_name = request.headers.get('x-webauth-user')
    if not ldap_is_eboard(user_name):
        return redirect("/dashboard")


    return render_template(request,
                           'attendance_ts.html',
                           username = user_name,
                           date = datetime.utcnow().strftime("%Y-%m-%d"))

@attendance_bp.route('/attendance_hm')
def display_attendance_hm():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('frontend', action='display house meeting attendance page')

    user_name = request.headers.get('x-webauth-user')
    if not ldap_is_eval_director(user_name):
        return redirect("/dashboard")

    return render_template(request,
                           'attendance_hm.html',
                           username = user_name,
                           date = datetime.utcnow().strftime("%Y-%m-%d"),
                           members = get_non_alumni_non_coop(internal=True))

@attendance_bp.route('/attendance/submit/cm', methods=['POST'])
def submit_committee_attendance():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('api', action='submit committee meeting attendance')

    from db.database import db_session

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eboard(user_name):
        return "must be eboard", 403

    post_data = request.get_json()

    committee = post_data['committee']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']
    timestamp = post_data['timestamp']

    timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    meeting = CommitteeMeeting(committee, timestamp)

    db_session.add(meeting)
    db_session.flush()
    db_session.refresh(meeting)

    for m in m_attendees:
        logger.info('backend',
            action=("gave attendance to %s for %s" % (m, committee))
        )
        db_session.add(MemberCommitteeAttendance(m, meeting.id))

    for f in f_attendees:
        logger.info('backend',
            action=("gave attendance to freshman-%s for %s" % (f, committee))
        )
        db_session.add(FreshmanCommitteeAttendance(f, meeting.id))

    db_session.commit()
    return jsonify({"success": True}), 200

@attendance_bp.route('/attendance/submit/ts', methods=['POST'])
def submit_seminar_attendance():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('api', action='submit technical seminar attendance')

    from db.database import db_session

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eboard(user_name):
        return "must be eboard", 403

    post_data = request.get_json()

    seminar_name = post_data['name']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']
    timestamp = post_data['timestamp']

    timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    seminar = TechnicalSeminar(seminar_name, timestamp)

    db_session.add(seminar)
    db_session.flush()
    db_session.refresh(seminar)

    for m in m_attendees:
        logger.info('backend',
            action=("gave attendance to %s for %s" % (m, seminar_name))
        )
        db_session.add(MemberSeminarAttendance(m, seminar.id))

    for f in f_attendees:
        logger.info('backend',
            action=("gave attendance to freshman-%s for %s" % (f, seminar_name))
        )
        db_session.add(FreshmanSeminarAttendance(f, seminar.id))

    db_session.commit()
    return jsonify({"success": True}), 200

@attendance_bp.route('/attendance/submit/hm', methods=['POST'])
def submit_house_attendance():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('api', action='submit house meeting attendance')

    from db.database import db_session

    # status: Attended | Excused | Absent

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name):
        return "must be evals", 403

    post_data = request.get_json()

    timestamp = datetime.strptime(post_data['timestamp'], "%Y-%m-%d")

    meeting = HouseMeeting(timestamp)

    db_session.add(meeting)
    db_session.flush()
    db_session.refresh(meeting)

    for m in m_attendees:
        logger.info('backend',
            action=("gave %s (%s) to %s for %s" % (m['status'] m['uid'], timestamp.strftime("%Y-%m-%d")))
        )
        db_session.add(MemberHouseMeetingAttendance(
                        m['uid'],
                        meeting.id,
                        None,
                        m['status']))

    for f in f_attendees:
        logger.info('backend',
            action=("gave %s (%s) to freshman-%s for %s" % (f['status'], f['id'], timestamp.strftime("%Y-%m-%d")))
        )
        db_session.add(FreshmanHouseMeetingAttendance(
                        f['id'],
                        meeting.id,
                        None,
                        f['status']))

    db_session.commit()
    return jsonify({"success": True}), 200
