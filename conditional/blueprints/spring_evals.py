import structlog
from flask import Blueprint, request
from sqlalchemy import func

from conditional import db, start_of_year, auth
from conditional.models.models import CommitteeMeeting, HouseMeeting, MemberCommitteeAttendance
from conditional.models.models import MajorProject, MemberHouseMeetingAttendance, SpringEval
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_get_active_members
from conditional.util.member import req_cm

spring_evals_bp = Blueprint('spring_evals_bp', __name__)

logger = structlog.get_logger()


@spring_evals_bp.route('/spring_evals/')
@auth.oidc_auth("default")
@get_user
def display_spring_evals(internal=False, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Membership Evaluations Listing')

    active_members = ldap_get_active_members()

    cm_count = dict([tuple(row) for row in MemberCommitteeAttendance.query.join(
        CommitteeMeeting,
        MemberCommitteeAttendance.meeting_id == CommitteeMeeting.id
    ).with_entities(
        MemberCommitteeAttendance.uid,
        CommitteeMeeting.timestamp,
        CommitteeMeeting.approved,
    ).filter(
        CommitteeMeeting.approved,
        CommitteeMeeting.timestamp >= start_of_year()
    ).with_entities(
        MemberCommitteeAttendance.uid,
        func.count(MemberCommitteeAttendance.uid) #pylint: disable=not-callable
    ).group_by(
        MemberCommitteeAttendance.uid
    ).all()])

    hm_missed = dict([tuple(row) for row in MemberHouseMeetingAttendance.query.join(
        HouseMeeting,
        MemberHouseMeetingAttendance.meeting_id == HouseMeeting.id
    ).filter(
        HouseMeeting.date >= start_of_year(),
        MemberHouseMeetingAttendance.attendance_status == 'Absent'
    ).with_entities(
        MemberHouseMeetingAttendance.uid,
            func.count(MemberHouseMeetingAttendance.uid) #pylint: disable=not-callable
    ).group_by(
        MemberHouseMeetingAttendance.uid
    ).all()])

    major_project_query = MajorProject.query.filter(
        MajorProject.date >= start_of_year()
    ).all()

    major_projects = {}

    for project in major_project_query:
        if not project.uid in major_projects:
            major_projects[project.uid] = []

        major_projects.get(project.uid).append({
            'name': project.name,
            'status': project.status,
            'description': project.description
        })

    sp_members = []
    for account in active_members:
        uid = account.uid
        spring_entry = SpringEval.query.filter(
            SpringEval.date_created > start_of_year(),
            SpringEval.uid == uid,
            SpringEval.active == True).first() # pylint: disable=singleton-comparison

        if spring_entry is None:
            spring_entry = SpringEval(uid)
            db.session.add(spring_entry)
            db.session.flush()
            db.session.commit()
        elif spring_entry.status != 'Pending' and internal:
            continue

        member_missed_hms = []

        if  hm_missed.get(uid, 0) != 0:
            member_missed_hms = MemberHouseMeetingAttendance.query.join(
                HouseMeeting,
                MemberHouseMeetingAttendance.meeting_id == HouseMeeting.id
            ).filter(
                HouseMeeting.date >= start_of_year(),
                MemberHouseMeetingAttendance.attendance_status == 'Absent',
                MemberHouseMeetingAttendance.uid == uid,
            ).with_entities(
                func.array_agg(HouseMeeting.date)
            ).scalar()

        member = {
            'name': account.cn,
            'uid': uid,
            'status': spring_entry.status,
            'committee_meetings': cm_count.get(uid, 0),
            'req_meetings': req_cm(account),
            'house_meetings_missed': member_missed_hms,
            'major_projects': major_projects.get(uid, [])
        }

        passed_mps = [project for project in member['major_projects'] if project['status'] == 'Passed']

        member['major_projects_len'] = len(member['major_projects'])
        member['major_projects_passed'] = passed_mps
        member['major_projects_passed_len'] = len(member['major_projects_passed'])
        member['major_project_passed'] = member['major_projects_passed_len'] > 0

        sp_members.append(member)

    sp_members.sort(key=lambda x: x['committee_meetings'], reverse=True)
    sp_members.sort(key=lambda x: len(x['house_meetings_missed']))
    sp_members.sort(key=lambda x: x['major_projects_passed_len'], reverse=True)
    # return names in 'first last (username)' format
    if internal:
        return sp_members

    return render_template('spring_evals.html',
                           username=user_dict['username'],
                           members=sp_members)
