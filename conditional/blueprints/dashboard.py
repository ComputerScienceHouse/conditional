from flask import Blueprint
from flask import render_template
from flask import request
from util.ldap import ldap_get_room_number, ldap_is_active, ldap_is_onfloor, \
                      ldap_get_housing_points
from db.models import CommitteeMeeting, MajorProject, MemberCommitteeAttendance
dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard/')
def display_dashboard():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    data = {}
    data['username'] = user_name
    # Member Status
    data['active'] = ldap_is_active(user_name)
    # On-Floor Status
    data['onfloor'] = ldap_is_onfloor(user_name)
    # Voting Status
    data['voting'] = True # FIXME: unimplemented

    freshman = {}

    freshman['status'] = "Pending"
    # number of committee meetings attended
    freshman['committee_meetings'] = 11

    # technical seminar total
    freshman['ts_total'] = 42
    freshman['ts_string'] = "Seminar #1\nSeminar #2"

    freshman['hm_missed'] = 0

    freshman['social_events'] = "Welcome Back, First Marks"

    freshman['general_comments'] = "Please accept me as a member kthnxbai."

    freshman['eval_date'] = "Oct 31, 2015"

    data['freshman'] = freshman

    spring = {}
    spring['mp_status'] = "Failed"

    c_meetings = [m.meeting_id for m in
        MemberCommitteeAttendance.query.filter(
            MemberCommitteeAttendance.uid == user_name
        )]
    spring['committee_meetings'] = len(c_meetings)
    spring['hm_missed'] = 26
    spring['general_comments'] = "I should win, please don't kick me out"

    data['spring'] = spring
    housing = {}
    housing['points'] = ldap_get_housing_points(user_name)
    housing['room'] = ldap_get_room_number(user_name)
    housing['future_room'] = "NRH3102"
    housing['queue_pos'] = 2
    housing['queue_len'] = 9

    data['housing'] = housing

    data['major_projects'] = [
            {
                'name': p.name,
                'status': p.status,
                'description': p.description
            } for p in
        MajorProject.query.filter(MajorProject.uid == user_name)]

    data['major_projects_count'] = len(data['major_projects'])

    conditionals = [{'description':'redo freshman project','deadline':'next year'}]
    data['conditionals'] = conditionals
    data['conditionals_len'] = len(conditionals)

    attendance = [{'type':'House Meeting', 'datetime': 'christmass'}]
    print(c_meetings)
    attendance.extend([
        {
            'type': m.committee,
            'datetime': m.timestamp
        } for m in CommitteeMeeting.query.filter(
                CommitteeMeeting.id.in_(c_meetings)
            )])

    data['attendance'] = attendance
    data['attendance_len'] = len(attendance)

    return render_template('dashboard.html', **data)
