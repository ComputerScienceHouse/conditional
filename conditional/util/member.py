from datetime import datetime

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


@service_cache(maxsize=1024)
def get_voting_members():

    if datetime.today() < datetime(start_of_year().year, 12, 31):
        semester = 'Fall'
    else:
        semester = 'Spring'

    active_members = set(member.uid for member in ldap_get_active_members())
    intro_members = set(member.uid for member in ldap_get_intro_members())
    on_coop = set(member.uid for member in CurrentCoops.query.filter(
        CurrentCoops.date_created > start_of_year(),
        CurrentCoops.semester == semester).all())

    voting_list = list(active_members - intro_members - on_coop)

    passed_fall = FreshmanEvalData.query.filter(
        FreshmanEvalData.freshman_eval_result == "Passed",
        FreshmanEvalData.eval_date > start_of_year()
    ).distinct()

    for intro_member in passed_fall:
        if intro_member.uid not in voting_list:
            voting_list.append(intro_member.uid)

    return voting_list


@service_cache(maxsize=1024)
def get_members_info():
    members = [account for account in ldap_get_current_students()]
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
    freshman['fresh_proj'] = freshman_data.freshman_project
    freshman['sig_missed'] = freshman_data.signatures_missed
    freshman['eval_date'] = freshman_data.eval_date
    return freshman


@service_cache(maxsize=1024)
def get_onfloor_members():
    return [uid for uid in [members.uid for members in ldap_get_active_members()]
            if uid in [members.uid for members in ldap_get_onfloor_members()]]


def get_cm(member):
    c_meetings = [{
        "uid": cm.uid,
        "timestamp": cm.timestamp,
        "committee": cm.committee
    } for cm in CommitteeMeeting.query.join(
        MemberCommitteeAttendance,
        MemberCommitteeAttendance.meeting_id == CommitteeMeeting.id
        ).with_entities(
            MemberCommitteeAttendance.uid,
            CommitteeMeeting.timestamp,
            CommitteeMeeting.committee
            ).filter(
                CommitteeMeeting.timestamp > start_of_year(),
                MemberCommitteeAttendance.uid == member.uid,
                CommitteeMeeting.approved == True # pylint: disable=singleton-comparison
                ).all()]
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


@service_cache(maxsize=128)
def req_cm(member):
    # Get the number of required committee meetings based on if the member
    # is going on co-op in the current operating session.
    co_op = CurrentCoops.query.filter(
        CurrentCoops.uid == member.uid,
        CurrentCoops.date_created > start_of_year()).first()
    if co_op:
        return 15
    return 30
