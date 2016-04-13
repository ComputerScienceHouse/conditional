from flask import Blueprint
from flask import request

from util.ldap import ldap_get_room_number
from util.ldap import ldap_is_active
from util.ldap import ldap_is_onfloor
from util.ldap import ldap_get_housing_points
from util.ldap import ldap_is_intromember

from db.models import FreshmanEvalData
from db.models import MemberCommitteeAttendance
from db.models import MemberSeminarAttendance
from db.models import TechnicalSeminar
from db.models import MemberHouseMeetingAttendance
from db.models import MajorProject
from db.models import Conditional
from db.models import HouseMeeting
from db.models import CommitteeMeeting

from util.housing import get_queue_length, get_queue_position
from util.flask import render_template
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

    # freshman shit
    if ldap_is_intromember(user_name) or user_name == 'loothelion':
        freshman = {}
        freshman_data = FreshmanEvalData.query.filter(FreshmanEvalData.uid == user_name).first()

        freshman['status'] = freshman_data.freshman_eval_result
        # number of committee meetings attended
        c_meetings = [m.meeting_id for m in
            MemberCommitteeAttendance.query.filter(
                MemberCommitteeAttendance.uid == user_name
            )]
        freshman['committee_meetings'] = len(c_meetings)
        # technical seminar total
        t_seminars = [s.seminar_id for s in
            MemberSeminarAttendance.query.filter(
                MemberSeminarAttendance.uid == user_name
            )]
        freshman['ts_total'] = len(t_seminars)
        attendance = [m.name for m in TechnicalSeminar.query.filter(
                    TechnicalSeminar.id.in_(t_seminars)
                )]

        freshman['ts_list'] = attendance

        h_meetings = [(m.meeting_id, m.attendance_status) for m in
            MemberHouseMeetingAttendance.query.filter(
                MemberHouseMeetingAttendance.uid == user_name
            )]
        freshman['hm_missed'] = len([h for h in h_meetings if h[1] == "Absent"])
        freshman['social_events'] = freshman_data.social_events
        freshman['general_comments'] = freshman_data.other_notes
        freshman['fresh_proj'] = freshman_data.freshman_project
        freshman['sig_missed'] = freshman_data.signatures_missed
        freshman['eval_date'] = freshman_data.eval_date

        data['freshman'] = freshman
    else:
        data['freshman'] = False

    spring = {}
    c_meetings = [m.meeting_id for m in
        MemberCommitteeAttendance.query.filter(
            MemberCommitteeAttendance.uid == user_name
        )]
    spring['committee_meetings'] = len(c_meetings)
    h_meetings = [(m.meeting_id, m.attendance_status) for m in
        MemberHouseMeetingAttendance.query.filter(
            MemberHouseMeetingAttendance.uid == user_name
        )]
    spring['hm_missed'] = len([h for h in h_meetings if h[1] == "Absent"])
    h_meetings = [h[0] for h in h_meetings if h[1] != "Absent"]

    data['spring'] = spring

    housing = False

    # only show housing if member has onfloor status
    if ldap_is_onfloor(user_name):
        housing = {}
        housing['points'] = ldap_get_housing_points(user_name)
        housing['room'] = ldap_get_room_number(user_name)
        if housing['room'] == "N/A":
            housing['queue_pos'] = get_queue_position(user_name)
        else:
            housing['queue_pos'] = "On Floor"
        housing['queue_len'] = get_queue_length()

    data['housing'] = housing

    data['major_projects'] = [
            {
                'name': p.name,
                'status': p.status,
                'description': p.description
            } for p in
        MajorProject.query.filter(MajorProject.uid == user_name)]

    data['major_projects_count'] = len(data['major_projects'])

    spring['mp_status'] = "Failed"
    for mp in data['major_projects']:
        if mp['status'] == "Pending":
            spring['mp_status'] = 'Pending'
            continue
        if mp['status'] == "Passed":
            spring['mp_status'] = 'Passed'
            break

    conditionals = [
            {
                'date_created': c.date_created,
                'date_due': c.date_due,
                'description': c.description
            } for c in
        Conditional.query.filter(Conditional.uid == user_name)]
    data['conditionals'] = conditionals
    data['conditionals_len'] = len(conditionals)

    # TODO FIXME Create two seperate dropdown panels for
    # house and committee attendance
    attendance = [
        {
            'type': "House Meeting",
            'datetime': m.date
        } for m in HouseMeeting.query.filter(
                HouseMeeting.id.in_(h_meetings)
            )]
    attendance.extend([
        {
            'type': m.committee,
            'datetime': m.timestamp
        } for m in CommitteeMeeting.query.filter(
                CommitteeMeeting.id.in_(c_meetings)
            )])

    data['attendance'] = attendance
    data['attendance_len'] = len(attendance)

    return render_template(request, 'dashboard.html', **data)
