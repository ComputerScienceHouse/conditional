from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request

from util.ldap import ldap_get_non_alumni_members
from util.ldap import ldap_get_name
from util.ldap import ldap_get_current_students
from util.ldap import ldap_is_eboard
from util.ldap import ldap_is_eval_director

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
def get_non_alumni_non_coop():
    non_alumni_members = ldap_get_current_students()
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

    return jsonify({'members': named_members}), 200


@attendance_bp.route('/attendance/cm_members')
def get_non_alumni():
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

    user_name = request.headers.get('x-webauth-user')
    if not ldap_is_eboard(user_name) and user_name != 'loothelion':
        return redirect("/dashboard")


    return render_template(request,
                           'attendance_cm.html',
                           username = user_name)

@attendance_bp.route('/attendance_ts')
def display_attendance_ts():

    user_name = request.headers.get('x-webauth-user')
    if not ldap_is_eboard(user_name) and user_name != 'loothelion':
        return redirect("/dashboard")


    return render_template(request,
                           'attendance_ts.html',
                           username = user_name)

@attendance_bp.route('/attendance/submit/cm', methods=['POST'])
def submit_committee_attendance():
    from db.database import db_session

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eboard(user_name) and user_name != 'loothelion':
        return "must be eboard", 403

    post_data = request.get_json()

    committee = post_data['committee']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']

    meeting = CommitteeMeeting(committee, datetime.now())

    db_session.add(meeting)
    db_session.flush()
    db_session.refresh(meeting)

    for m in m_attendees:
        db_session.add(MemberCommitteeAttendance(m, meeting.id))

    for f in f_attendees:
        db_session.add(FreshmanCommitteeAttendance(f, meeting.id))

    db_session.commit()
    return jsonify({"success": True}), 200

@attendance_bp.route('/attendance/submit/ts', methods=['POST'])
def submit_seminar_attendance():
    from db.database import db_session

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eboard(user_name) and user_name != 'loothelion':
        return "must be eboard", 403

    post_data = request.get_json()

    print(post_data)

    seminar_name = post_data['name']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']

    seminar = TechnicalSeminar(seminar_name)

    db_session.add(seminar)
    db_session.flush()
    db_session.refresh(seminar)

    for m in m_attendees:
        db_session.add(MemberSeminarAttendance(m, seminar.id))

    for f in f_attendees:
        db_session.add(FreshmanSeminarAttendance(f, seminar.id))

    db_session.commit()
    return jsonify({"success": True}), 200

@attendance_bp.route('/attendance/submit/hm', methods=['POST'])
def submit_house_attendance():
    from db.database import db_session

    # status: Attended | Excused | Absent

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be evals", 403

    post_data = request.get_json()

    timestamp = post_data['timestamp']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']

    meeting = HouseMeeting(datetime.strptime(timestamp, "%A %d. %B %Y"))

    db_session.add(meeting)
    db_session.flush()
    db_session.refresh(meeting)

    for m in m_attendees:
        db_session.add(MemberHouseMeetingAttendance(
                        m['uid'],
                        meeting.id,
                        m['excuse'],
                        m['status']))

    for f in f_attendees:
        db_session.add(FreshmanHouseMeetingAttendance(
                        f['id'],
                        meeting.id,
                        f['excuse'],
                        f['status']))

    db_session.commit()
    return jsonify({"success": True}), 200
