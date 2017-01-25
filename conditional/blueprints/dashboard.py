import uuid
import structlog

from flask import Blueprint, request

from conditional.util.ldap import ldap_is_onfloor
from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_intromember
from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_get_active_members

from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MajorProject
from conditional.models.models import Conditional
from conditional.models.models import HouseMeeting
from conditional.models.models import SpringEval
from conditional.models.models import CommitteeMeeting

from conditional.util.housing import get_queue_position
from conditional.util.flask import render_template
from conditional.util.member import get_freshman_data, get_voting_members

logger = structlog.get_logger()

dashboard_bp = Blueprint('dashboard_bp', __name__)


@dashboard_bp.route('/dashboard/')
def display_dashboard():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display dashboard')

    # Get username from headers.
    username = request.headers.get('x-webauth-user')

    # Get the list of voting members.
    can_vote = get_voting_members()

    member = ldap_get_member(username)
    data = dict()
    data['username'] = member.uid
    data['name'] = member.cn
    data['active'] = ldap_is_active(member)
    data['onfloor'] = ldap_is_onfloor(member)
    data['voting'] = bool(member.uid in can_vote)

    data['voting_count'] = {"Voting Members": len(can_vote),
                            "Active Members": len(ldap_get_active_members())}
    # freshman shit
    if ldap_is_intromember(member):
        data['freshman'] = get_freshman_data(member.uid)
    else:
        data['freshman'] = False

    spring = {}
    c_meetings = [m.meeting_id for m in
                  MemberCommitteeAttendance.query.filter(
                      MemberCommitteeAttendance.uid == member.uid
                  ) if CommitteeMeeting.query.filter(
                      CommitteeMeeting.id == m.meeting_id).first().approved]
    spring['committee_meetings'] = len(c_meetings)
    h_meetings = [(m.meeting_id, m.attendance_status) for m in
                  MemberHouseMeetingAttendance.query.filter(
                      MemberHouseMeetingAttendance.uid == member.uid)]
    spring['hm_missed'] = len([h for h in h_meetings if h[1] == "Absent"])
    eval_entry = SpringEval.query.filter(SpringEval.uid == member.uid
                                         and SpringEval.active).first()
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
        MajorProject.query.filter(MajorProject.uid == member.uid)]

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
        Conditional.query.filter(Conditional.uid == member.uid)]
    data['conditionals'] = conditionals
    data['conditionals_len'] = len(conditionals)

    cm_attendance = [
        {
            'type': m.committee,
            'datetime': m.timestamp.date()
        } for m in CommitteeMeeting.query.filter(
            CommitteeMeeting.id.in_(c_meetings)
        )]

    hm_attendance = [
        {
            'reason': m.excuse,
            'datetime': HouseMeeting.query.filter(
                HouseMeeting.id == m.meeting_id).first().date
        } for m in
        MemberHouseMeetingAttendance.query.filter(
            MemberHouseMeetingAttendance.uid == member.uid
        ).filter(MemberHouseMeetingAttendance.attendance_status == "Absent")]

    data['cm_attendance'] = cm_attendance
    data['cm_attendance_len'] = len(cm_attendance)
    data['hm_attendance'] = hm_attendance
    data['hm_attendance_len'] = len(hm_attendance)

    return render_template(request, 'dashboard.html', **data)
