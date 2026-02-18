from conditional.util.user_dict import user_dict_is_active, user_dict_is_bad_standing, user_dict_is_intromember, user_dict_is_onfloor
import structlog
from flask import Blueprint, request

from conditional import start_of_year, auth
from conditional.models.models import Conditional
from conditional.models.models import HouseMeeting
from conditional.models.models import MajorProject
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import TechnicalSeminar
from conditional.models.models import SpringEval
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.housing import get_queue_position
from conditional.util.ldap import ldap_get_active_members, ldap_is_bad_standing
from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_intromember
from conditional.util.ldap import ldap_is_onfloor
from conditional.util.member import get_active_members, get_freshman_data, get_voting_members, get_cm, get_hm, req_cm

logger = structlog.get_logger()

dashboard_bp = Blueprint('dashboard_bp', __name__)

def is_seminar_attendance_valid(attendance):
    seminar = TechnicalSeminar.query.filter(
        TechnicalSeminar.id == attendance.seminar_id).first()
    return seminar and seminar.approved and seminar.timestamp > start_of_year()

# pylint: disable=too-many-statements
@dashboard_bp.route('/dashboard/')
@auth.oidc_auth("default")
@get_user
def display_dashboard(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('display dashboard')

    uid = user_dict["username"]

    can_vote = get_voting_members()

    on_floor = user_dict_is_onfloor(user_dict)

    data = {}
    data['username'] = uid
    data['active'] = user_dict_is_active(user_dict)
    data['bad_standing'] = user_dict_is_bad_standing(user_dict)
    data['onfloor'] = on_floor
    data['voting'] = bool(uid in can_vote)

    data['voting_count'] = {"Voting Members": len(can_vote),
                            "Active Members": len(get_active_members())}
    # freshman shit
    if user_dict_is_intromember(user_dict):
        data['freshman'] = get_freshman_data(uid)
    else:
        data['freshman'] = None

    spring = {}
    c_meetings = get_cm(user_dict['account'])
    spring['committee_meetings'] = len(c_meetings)
    spring['req_meetings'] = req_cm(uid)
    h_meetings = [(m.meeting_id, m.attendance_status) for m in get_hm(user_dict['account'])]
    spring['hm_missed'] = len([h for h in h_meetings if h[1] == "Absent"])
    eval_entry = SpringEval.query.filter(SpringEval.uid == uid,
                                         SpringEval.date_created > start_of_year(),
                                         SpringEval.active == True).first()  # pylint: disable=singleton-comparison
    if eval_entry is not None:
        spring['status'] = eval_entry.status
    else:
        spring['status'] = None

    data['spring'] = spring

    # only show housing if member has onfloor status
    if on_floor:
        housing = {}
        housing['points'] = user_dict['account'].housingPoints
        housing['room'] = user_dict['account'].roomNumber
        housing['queue_pos'] = get_queue_position(uid)
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
        MajorProject.query.filter(MajorProject.uid == uid,
                                  MajorProject.date > start_of_year())]

    data['major_projects_count'] = len(data['major_projects'])

    # technical seminar total
    t_seminars = [s.seminar_id for s in
                  MemberSeminarAttendance.query.filter(
                      MemberSeminarAttendance.uid == uid,
                  ) if is_seminar_attendance_valid(s)]
    data['ts_total'] = len(t_seminars)
    attendance = [m.name for m in TechnicalSeminar.query.filter(
        TechnicalSeminar.id.in_(t_seminars)
        )]

    data['ts_list'] = attendance

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
            Conditional.uid == uid,
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
            MemberHouseMeetingAttendance.uid == uid,
            MemberHouseMeetingAttendance.attendance_status == "Absent",
            HouseMeeting.date > start_of_year())]

    data['cm_attendance'] = c_meetings
    data['cm_attendance_len'] = len(c_meetings)
    data['hm_attendance'] = hm_attendance
    data['hm_attendance_len'] = len(hm_attendance)

    return render_template('dashboard.html', **data)
