from functools import lru_cache

from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_intro_members
from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_get_roomnumber
from conditional.util.ldap import ldap_get_onfloor_members
from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_onfloor

from conditional.models.models import FreshmanEvalData
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import TechnicalSeminar


@lru_cache(maxsize=1024)
def get_voting_members():
    voting_list = [uid for uid in [member.uid for member in ldap_get_active_members()]
                   if uid not in [member.uid for member in ldap_get_intro_members()]]

    passed_fall = FreshmanEvalData.query.filter(
        FreshmanEvalData.freshman_eval_result == "Passed"
    ).distinct()

    for intro_member in passed_fall:
        voting_list.append(intro_member.uid)

    return voting_list


@lru_cache(maxsize=1024)
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
                      MemberHouseMeetingAttendance.uid == user_name)]
    freshman['hm_missed'] = len([h for h in h_meetings if h[1] == "Absent"])
    freshman['social_events'] = freshman_data.social_events
    freshman['general_comments'] = freshman_data.other_notes
    freshman['fresh_proj'] = freshman_data.freshman_project
    freshman['sig_missed'] = freshman_data.signatures_missed
    freshman['eval_date'] = freshman_data.eval_date
    return freshman


@lru_cache(maxsize=1024)
def get_onfloor_members():
    return [uid for uid in [members.uid for members in ldap_get_active_members()]
            if uid in [members.uid for members in ldap_get_onfloor_members()]]
