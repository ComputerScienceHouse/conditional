import structlog
from flask import Blueprint, request

from conditional import start_of_year, auth
from conditional.models.models import Conditional
from conditional.models.models import HouseMeeting
from conditional.models.models import MajorProject
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import SpringEval
from conditional.util.auth import get_username
from conditional.util.flask import render_template
from conditional.util.housing import get_queue_position
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_current_student
from conditional.util.ldap import ldap_is_intromember
from conditional.util.ldap import ldap_is_onfloor
from conditional.util.member import get_freshman_data, get_voting_members, get_cm, get_hm, req_cm

logger = structlog.get_logger()

dashboard_bp = Blueprint('dashboard_bp', __name__)


@dashboard_bp.route('/dashboard/')
@auth.oidc_auth
@get_username
def display_dashboard(username=None):
    log = logger.new(request=request)
    log.info('display dashboard')

    # Get the list of voting members.
    can_vote = get_voting_members()

    member = ldap_get_member(username)
    data = dict()
    data['username'] = member.uid
    data['name'] = member.cn
    data['active'] = ldap_is_active(member)
    data['onfloor'] = ldap_is_onfloor(member)
    data['voting'] = bool(member.uid in can_vote)
    data['student'] = ldap_is_current_student(member)

    data['voting_count'] = {"Voting Members": len(can_vote),
                            "Active Members": len(ldap_get_active_members())}
    # freshman shit
    if ldap_is_intromember(member):
        data['freshman'] = get_freshman_data(member.uid)
    else:
        data['freshman'] = False

    spring = {}
    c_meetings = get_cm(member)
    spring['committee_meetings'] = len(c_meetings)
    spring['req_meetings'] = req_cm(member)
    h_meetings = [(m.meeting_id, m.attendance_status) for m in get_hm(member)]
    spring['hm_missed'] = len([h for h in h_meetings if h[1] == "Absent"])
    eval_entry = SpringEval.query.filter(SpringEval.uid == member.uid,
                                         SpringEval.date_created > start_of_year(),
                                         SpringEval.active == True).first()  # pylint: disable=singleton-comparison
    if eval_entry is not None:
        spring['status'] = eval_entry.status
    else:
        spring['status'] = None

    data['spring'] = spring

    # only show housing if member has onfloor status
    if ldap_is_onfloor(member):
        housing = dict()
        housing['points'] = member.housingPoints
        housing['room'] = member.roomNumber
        housing['queue_pos'] = get_queue_position(member.uid)
    else:
        housing = None

    data['housing'] = housing

    data['major_projects'] = [
        {
            'id': p.id,
            'name': p.name,
            'status': p.status,
            'description': p.description
        } for p in
        MajorProject.query.filter(MajorProject.uid == member.uid,
                                  MajorProject.date > start_of_year())]

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
            'description': c.description,
            'status': c.status
        } for c in
        Conditional.query.filter(
            Conditional.uid == member.uid,
            Conditional.date_due > start_of_year())]
    data['conditionals'] = conditionals
    data['conditionals_len'] = len(conditionals)

    hm_attendance = [
        {
            'reason': m.excuse,
            'datetime': m.date
        } for m in
        MemberHouseMeetingAttendance.query.outerjoin(
            HouseMeeting,
            MemberHouseMeetingAttendance.meeting_id == HouseMeeting.id).with_entities(
            MemberHouseMeetingAttendance.excuse,
            HouseMeeting.date).filter(
            MemberHouseMeetingAttendance.uid == member.uid,
            MemberHouseMeetingAttendance.attendance_status == "Absent",
            HouseMeeting.date > start_of_year())]

    data['cm_attendance'] = c_meetings
    data['cm_attendance_len'] = len(c_meetings)
    data['hm_attendance'] = hm_attendance
    data['hm_attendance_len'] = len(hm_attendance)

    return render_template('dashboard.html', **data)
