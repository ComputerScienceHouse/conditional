import structlog
from flask import Blueprint, request
from sqlalchemy import func

from conditional import start_of_year, auth
from conditional.models.models import CommitteeMeeting, CurrentCoops, HouseMeeting, MemberCommitteeAttendance, MemberSeminarAttendance, TechnicalSeminar
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_get_active_members
from conditional.util.member import get_semester_info

gatekeep_bp = Blueprint('gatekeep_bp', __name__)

logger = structlog.get_logger()

@gatekeep_bp.route('/gatekeep_status/')
@auth.oidc_auth("default")
@get_user
def display_spring_evals(internal=False, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Gatekeep Status Listing')

    _, semester_start = get_semester_info()
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
        CommitteeMeeting.timestamp >= semester_start
    ).with_entities(
        MemberCommitteeAttendance.uid,
        func.count(MemberCommitteeAttendance.uid) #pylint: disable=not-callable
    ).group_by(
        MemberCommitteeAttendance.uid
    ).all()])

    ts_count = dict([tuple(row) for row in MemberSeminarAttendance.query.join(
        TechnicalSeminar,
        MemberSeminarAttendance.seminar_id == TechnicalSeminar.id
    ).with_entities(
        MemberSeminarAttendance.uid,
        TechnicalSeminar.timestamp,
        TechnicalSeminar.approved,
    ).filter(
        TechnicalSeminar.approved,
        TechnicalSeminar.timestamp >= semester_start
    ).with_entities(
        MemberSeminarAttendance.uid,
        func.count(MemberSeminarAttendance.uid) #pylint: disable=not-callable
    ).group_by(
        MemberSeminarAttendance.uid
    ).all()])

    hm_missed = dict([tuple(row) for row in MemberHouseMeetingAttendance.query.join(
        HouseMeeting,
        MemberHouseMeetingAttendance.meeting_id == HouseMeeting.id
    ).filter(
        HouseMeeting.date >= semester_start,
        MemberHouseMeetingAttendance.attendance_status == 'Absent'
    ).with_entities(
        MemberHouseMeetingAttendance.uid,
            func.count(MemberHouseMeetingAttendance.uid) #pylint: disable=not-callable
    ).group_by(
        MemberHouseMeetingAttendance.uid
    ).all()])

    gk_members = []
    for account in active_members:
        uid = account.uid
        name = account.cn

        member_missed_hms = []

        if hm_missed.get(uid, 0) != 0:
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

        cm_attended_count = cm_count.get(uid, 0)
        ts_attended_count = ts_count.get(uid, 0)

        passing = len(member_missed_hms) <= 1 and cm_attended_count >= 6 and ts_attended_count >= 2

        status = 'disenfranchised'

        if passing:
            status = 'passed'

        member = {
            'name': name,
            'uid': uid,
            'status': status,
            'committee_meetings': cm_attended_count,
            'technical_seminars': ts_attended_count,
            'req_meetings': 6,
            'req_seminars': 2,
            'house_meetings_missed': member_missed_hms,
        }

        gk_members.append(member)

    gk_members.sort(key=lambda x: x['committee_meetings'], reverse=True)
    gk_members.sort(key=lambda x: x['technical_seminars'], reverse=True)
    gk_members.sort(key=lambda x: len(x['house_meetings_missed']))
    # return names in 'first last (username)' format
    if internal:
        return gk_members

    return render_template('gatekeep.html',
                           username=user_dict['username'],
                           members=gk_members,
                           req_meetings=6,
                           req_seminars=2)
