from datetime import datetime
from sqlalchemy import func, or_

from conditional import start_of_year
from conditional.models.models import CommitteeMeeting
from conditional.models.models import CurrentCoops
from conditional.models.models import FreshmanEvalData
from conditional.models.models import HouseMeeting
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import TechnicalSeminar
from conditional.util.cache import service_cache
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_get_intro_members
from conditional.util.ldap import ldap_get_onfloor_members
from conditional.util.ldap import ldap_get_roomnumber
from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_onfloor
from conditional.util.ldap import ldap_is_intromember
from conditional.util.ldap import ldap_get_member

@service_cache(maxsize=1024)
def get_members_info():
    members = ldap_get_current_students()
    member_list = []

    for account in members:
        uid = account.uid
        name = account.cn
        active = ldap_is_active(account)
        onfloor = ldap_is_onfloor(account)
        room = ldap_get_roomnumber(account)
        hp = account.housingPoints
        member_list.append({
            "uid": uid,
            "name": name,
            "active": active,
            "onfloor": onfloor,
            "room": room,
            "hp": hp
        })

    return member_list


def get_freshman_data(user_name):
    freshman = {}
    freshman_data = FreshmanEvalData.query.filter(FreshmanEvalData.uid == user_name).first()

    if freshman_data is None:
        return None
    freshman['status'] = freshman_data.freshman_eval_result
    # number of committee meetings attended
    c_meetings = [m.meeting_id for m in
                  MemberCommitteeAttendance.query.filter(
                      MemberCommitteeAttendance.uid == user_name
                  ) if CommitteeMeeting.query.filter(
                      CommitteeMeeting.id == m.meeting_id).first().approved]
    freshman['committee_meetings'] = len(c_meetings)
    # technical seminar total
    t_seminars = [s.seminar_id for s in
                  MemberSeminarAttendance.query.filter(
                      MemberSeminarAttendance.uid == user_name
                  ) if TechnicalSeminar.query.filter(
                      TechnicalSeminar.id == s.seminar_id).first().approved]
    freshman['ts_total'] = len(t_seminars)
    attendance = [m.name for m in TechnicalSeminar.query.filter(
        TechnicalSeminar.id.in_(t_seminars)
        )]

    freshman['ts_list'] = attendance

    h_meetings = [(m.meeting_id, m.attendance_status) for m in
                  MemberHouseMeetingAttendance.query.filter(
                      MemberHouseMeetingAttendance.uid == user_name)]
    freshman['hm_missed'] = len([h for h in h_meetings if h[1] == "Absent"])
    freshman['social_events'] = freshman_data.social_events
    freshman['general_comments'] = freshman_data.other_notes
    freshman['sig_missed'] = freshman_data.signatures_missed
    freshman['eval_date'] = freshman_data.eval_date
    return freshman


@service_cache(maxsize=1024)
def get_onfloor_members():
    return [uid for uid in [members.uid for members in ldap_get_active_members()]
            if uid in [members.uid for members in ldap_get_onfloor_members()]]


def get_cm(member):
    query_result = CommitteeMeeting.query.join(
        MemberCommitteeAttendance,
        MemberCommitteeAttendance.meeting_id == CommitteeMeeting.id
    ).with_entities(
        MemberCommitteeAttendance.uid,
        CommitteeMeeting.timestamp,
        CommitteeMeeting.committee
    ).filter(
        CommitteeMeeting.timestamp > start_of_year(),
        MemberCommitteeAttendance.uid == member.uid,
        CommitteeMeeting.approved
    ).all()

    c_meetings = [{
        "uid": cm.uid,
        "timestamp": cm.timestamp,
        "committee": cm.committee
    } for cm in query_result]

    return c_meetings


def get_hm(member, only_absent=False):
    h_meetings = MemberHouseMeetingAttendance.query.outerjoin(
                  HouseMeeting,
                  MemberHouseMeetingAttendance.meeting_id == HouseMeeting.id).with_entities(
                      MemberHouseMeetingAttendance.meeting_id,
                      MemberHouseMeetingAttendance.attendance_status,
                      HouseMeeting.date).filter(
                          HouseMeeting.date > start_of_year(),
                          MemberHouseMeetingAttendance.uid == member.uid)
    if only_absent:
        h_meetings = h_meetings.filter(MemberHouseMeetingAttendance.attendance_status == "Absent")
    return h_meetings


# @service_cache(maxsize=128)
def req_cm(uid, members_on_coop = None):
    # Get the number of required committee meetings based on if the member
    # is going on co-op in the current operating session.
    on_coop = False
    if members_on_coop:
        on_coop = uid in members_on_coop
    else:
        co_op = CurrentCoops.query.filter(
            CurrentCoops.uid == uid,
            CurrentCoops.date_created > start_of_year()).first()
        if co_op:
            on_coop = True
    if on_coop:
        return 15
    return 30

@service_cache(maxsize=256)
def get_voting_members():
    if datetime.today() < datetime(start_of_year().year, 12, 31):
        semester = "Fall"
        semester_start = datetime(start_of_year().year,6,1)
    else:
        semester = "Spring"
        semester_start = datetime(start_of_year().year + 1,1,1)

    active_members = set(ldap_get_active_members())
    intro_members = set(ldap_get_intro_members())

    coop_members = CurrentCoops.query.filter(
        CurrentCoops.date_created > start_of_year(),
        CurrentCoops.semester == semester,
    ).with_entities(
        func.array_agg(CurrentCoops.uid)
    ).scalar()

    # have to do this because if it's none then set constructor screams
    if coop_members is None:
        coop_members = set()
    else:
        coop_members = set(coop_members)

    passed_fall_members = FreshmanEvalData.query.filter(
            FreshmanEvalData.freshman_eval_result == "Passed",
            FreshmanEvalData.eval_date > start_of_year(),
    ).with_entities(
        func.array_agg(FreshmanEvalData.uid)
    ).scalar()

    if passed_fall_members is None:
        passed_fall_members = set()
    else:
        passed_fall_members = set(passed_fall_members)

    active_not_intro = active_members - intro_members
    active_not_intro = set(map(lambda member: member.uid, active_not_intro))

    eligible_members = (active_not_intro - coop_members) | passed_fall_members

    passing_dm = set(member.uid for member in MemberCommitteeAttendance.query.join(
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
        MemberCommitteeAttendance.uid
    ).group_by(
        MemberCommitteeAttendance.uid
    ).having(
        func.count(MemberCommitteeAttendance.uid) >= 6 #pylint: disable=not-callable
    ).with_entities(
        MemberCommitteeAttendance.uid
    ).all())

    passing_ts = set(member.uid for member in MemberSeminarAttendance.query.join(
        TechnicalSeminar,
        MemberSeminarAttendance.seminar_id == TechnicalSeminar.id
    ).filter(
        TechnicalSeminar.approved,
        TechnicalSeminar.timestamp >= semester_start
    ).with_entities(
        MemberSeminarAttendance.uid
    ).group_by(
        MemberSeminarAttendance.uid
    ).having(
        func.count(MemberSeminarAttendance.uid) >= 2 #pylint: disable=not-callable
    ).all())

    passing_hm = set(member.uid for member in MemberHouseMeetingAttendance.query.join(
        HouseMeeting,
        MemberHouseMeetingAttendance.meeting_id == HouseMeeting.id
    ).filter(
        HouseMeeting.date >= semester_start, or_(
            MemberHouseMeetingAttendance.attendance_status == 'Attended',
            # MemberHouseMeetingAttendance.attendance_status == 'Excused'
        )
    ).with_entities(
        MemberHouseMeetingAttendance.uid
    ).group_by(
        MemberHouseMeetingAttendance.uid
    ).having(
        func.count(MemberHouseMeetingAttendance.uid) >= 6 #pylint: disable=not-callable
    ).all())

    passing_reqs = passing_dm & passing_ts & passing_hm

    return eligible_members & passing_reqs

def gatekeep_status(username):
    if datetime.today() < datetime(start_of_year().year, 12, 31):
        semester = "Fall"
        semester_start = datetime(start_of_year().year,6,1)
    else:
        semester = "Spring"
        semester_start = datetime(start_of_year().year + 1,1,1)

    # groups
    ldap_member = ldap_get_member(username)
    is_intro_member = ldap_is_intromember(ldap_member)
    is_active_member = ldap_is_active(ldap_member) and not is_intro_member

    is_on_coop = (
        CurrentCoops.query.filter(
            CurrentCoops.date_created > start_of_year(),
            CurrentCoops.semester == semester,
            CurrentCoops.uid == username,
        ).first()
        is not None
    )

    passed_fall = (
        FreshmanEvalData.query.filter(
            FreshmanEvalData.freshman_eval_result == "Passed",
            FreshmanEvalData.eval_date > start_of_year(),
            FreshmanEvalData.uid == username,
        ).first()
        is not None
    )
    eligibility_of_groups = (is_active_member and not is_on_coop) or passed_fall

    # number of directorship meetings attended in the current semester
    d_meetings = (
        MemberCommitteeAttendance.query.join(
            CommitteeMeeting,
            MemberCommitteeAttendance.meeting_id == CommitteeMeeting.id,
        )
        .filter(
            MemberCommitteeAttendance.uid == username,
            bool(CommitteeMeeting.approved),
            CommitteeMeeting.timestamp >= semester_start,
        )
        .count()
    )
    # number of technical seminars attended in the current semester
    t_seminars = (
        MemberSeminarAttendance.query.join(
            TechnicalSeminar,
            MemberSeminarAttendance.seminar_id == TechnicalSeminar.id,
        )
        .filter(
            MemberSeminarAttendance.uid == username,
            bool(TechnicalSeminar.approved),
            TechnicalSeminar.timestamp >= semester_start,
        )
        .count()
    )
    # number of house meetings attended in the current semester
    h_meetings = (
        MemberHouseMeetingAttendance.query.join(
            HouseMeeting,
            MemberHouseMeetingAttendance.meeting_id == HouseMeeting.id,
        )
        .filter(
            MemberHouseMeetingAttendance.uid == username,
            HouseMeeting.date >= semester_start
        )
        .count()
    )
    result = eligibility_of_groups and (d_meetings >= 6 and t_seminars >= 2 and h_meetings >= 6)

    return {
        "result": result,
        "h_meetings": h_meetings,
        "c_meetings": d_meetings,
        "t_seminars": t_seminars,
    }
