from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from util.ldap import ldap_get_all_members, ldap_get_non_alumni_members, ldap_get_name, ldap_get_current_students

from db.models import CurrentCoops
from db.models import CommitteeMeeting
from db.models import FreshmanCommitteeAttendance
from db.models import MemberCommitteeAttendance
from datetime import datetime

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
    import db.models as models

    members = ldap_get_current_students()

    named_members = [
        {
            'display': f.name,
            'value': f.id,
            'freshman': True
        } for f in models.FreshmanAccount.query.filter(
        models.FreshmanAccount.eval_date > datetime.now())]

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
    import db.models as models
    non_alumni_members = ldap_get_current_students()
    coop_members = [u.username for u in CurrentCoops.query.all()]

    named_members = [
        {
            'display': f.name,
            'value': f.id,
            'freshman': True
        } for f in models.FreshmanAccount.query.filter(
        models.FreshmanAccount.eval_date > datetime.now())]

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
    import db.models as models
    non_alumni_members = ldap_get_current_students()

    named_members = [
        {
            'display': f.name,
            'value': f.id,
            'freshman': True
        } for f in models.FreshmanAccount.query.filter(
        models.FreshmanAccount.eval_date > datetime.now())]
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

@attendance_bp.route('/attendance/')
def display_attendance():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    #TODO FIXME ADD CONTENT
    return "", 200
    # return names in 'first last (username)' format

@attendance_bp.route('/attendance/submit/cm', methods=['POST'])
def submit_committee_attendance():
    from db.database import db_session

    user_name = request.headers.get('x-webauth-user')

    post_data = request.get_json()

    committee = post_data['committee']
    timestamp = post_data['timestamp']
    m_attendees = post_data['members']
    f_attendees = post_data['freshmen']

    meeting = CommitteeMeeting(committee,
        datetime.strptime(timestamp, "%A %d. %B %Y"))

    db_session.add(meeting)
    db_session.flush()
    db_session.refresh(meeting)

    for m in m_attendees:
        db_session.add(MemberCommitteeAttendance(m, meeting.id))

    for f in f_attendees:
        db_session.add(FreshmanCommitteeAttendance(f, meeting.id))

    db_session.commit()
    return '', 200

@attendance_bp.route('/attendance/submit/hm', methods=['POST'])
def submit_house_attendance():
    from db.database import db_session

    # status: Attended | Excused | Absent

    user_name = request.headers.get('x-webauth-user')

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
    return '', 200
