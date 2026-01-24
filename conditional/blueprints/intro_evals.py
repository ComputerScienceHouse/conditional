from datetime import datetime

import structlog
from flask import Blueprint, request
from sqlalchemy import func

from conditional import start_of_year, auth
from conditional.models.models import CommitteeMeeting
from conditional.models.models import FreshmanAccount
from conditional.models.models import FreshmanCommitteeAttendance
from conditional.models.models import FreshmanEvalData
from conditional.models.models import FreshmanHouseMeetingAttendance
from conditional.models.models import FreshmanSeminarAttendance
from conditional.models.models import HouseMeeting
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import TechnicalSeminar
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_get_intro_members

intro_evals_bp = Blueprint('intro_evals_bp', __name__)

logger = structlog.get_logger()

def get_intro_members_without_accounts():
    freshman_cm_count = dict([tuple(row) for row in FreshmanCommitteeAttendance.query.join(
        CommitteeMeeting,
        FreshmanCommitteeAttendance.meeting_id == CommitteeMeeting.id
    ).with_entities(
        FreshmanCommitteeAttendance.fid,
        CommitteeMeeting.timestamp,
        CommitteeMeeting.approved,
    ).filter(
        CommitteeMeeting.approved,
        CommitteeMeeting.timestamp >= start_of_year()
    ).with_entities(
        FreshmanCommitteeAttendance.fid,
        func.count(FreshmanCommitteeAttendance.fid) #pylint: disable=not-callable
    ).group_by(
        FreshmanCommitteeAttendance.fid
    ).all()])

    freshman_hm_missed = dict([tuple(row) for row in FreshmanHouseMeetingAttendance.query.join(
        HouseMeeting,
        FreshmanHouseMeetingAttendance.meeting_id == HouseMeeting.id
    ).filter(
        HouseMeeting.date >= start_of_year(),
        FreshmanHouseMeetingAttendance.attendance_status == 'Absent'
    ).with_entities(
        FreshmanHouseMeetingAttendance.fid,
            func.count(FreshmanHouseMeetingAttendance.fid) #pylint: disable=not-callable
    ).group_by(
        FreshmanHouseMeetingAttendance.fid
    ).all()])

    freshman_ts_attendance_query = FreshmanSeminarAttendance.query.join(
        TechnicalSeminar,
        FreshmanSeminarAttendance.seminar_id == TechnicalSeminar.id
    ).with_entities(
        FreshmanSeminarAttendance.fid,
        TechnicalSeminar.timestamp,
        TechnicalSeminar.approved
    ).filter(
        TechnicalSeminar.approved,
        TechnicalSeminar.timestamp >= start_of_year()
    ).with_entities(
        FreshmanSeminarAttendance.fid,
        TechnicalSeminar.name
    ).all()

    freshman_ts_attendance_dict = {}

    for row in freshman_ts_attendance_query:
        if not row[0] in freshman_ts_attendance_dict:
            freshman_ts_attendance_dict[row[0]] = []

            freshman_ts_attendance_dict[row[0]].append(row[1])

    # freshmen who don't have accounts
    freshman_accounts = list(FreshmanAccount.query.filter(
        FreshmanAccount.eval_date > start_of_year(),
        FreshmanAccount.eval_date > datetime.now()))

    ie_members = []

    for freshman_account in freshman_accounts:
        missed_hms = []
        if freshman_hm_missed.get(freshman_account.id, 0) != 0:
            missed_hms = FreshmanHouseMeetingAttendance.query.join(
                    HouseMeeting,
                    FreshmanHouseMeetingAttendance.meeting_id == HouseMeeting.id
            ).filter(
                    HouseMeeting.date >= start_of_year(), # TODO: this needs to be fixed
                    FreshmanHouseMeetingAttendance.attendance_status == 'Absent',
                    FreshmanHouseMeetingAttendance.fid == freshman_account.id,
            ).with_entities(
                    func.array_agg(HouseMeeting.date)
            ).scalar()

        if freshman_account.signatures_missed is None:
            signatures_missed = -1
        else:
            signatures_missed = freshman_account.signatures_missed

        cms_attended = freshman_cm_count.get(freshman_account.id, 0)

        freshman = {
            'name': freshman_account.name,
            'uid': freshman_account.id,
            'eval_date': freshman_account.eval_date.strftime("%Y-%m-%d"),
            'signatures_missed': signatures_missed,
            'committee_meetings': cms_attended,
            'committee_meetings_passed': cms_attended >= 6,
            'house_meetings_missed': missed_hms,
            'technical_seminars': freshman_ts_attendance_dict.get(freshman_account.id, []),
            'social_events': '',
            'comments': "",
            'ldap_account': False,
            'status': "Pending"
        }
        ie_members.append(freshman)

    return ie_members

@intro_evals_bp.route('/intro_evals/')
@auth.oidc_auth("default")
@get_user
def display_intro_evals(internal=False, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Intro Evals Listing')

    members = ldap_get_intro_members()

    ie_members = get_intro_members_without_accounts()

    account_cm_count = dict([tuple(row) for row in MemberCommitteeAttendance.query.join(
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

    account_hm_missed = dict([tuple(row) for row in MemberHouseMeetingAttendance.query.join(
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

    account_ts_attendance_query = MemberSeminarAttendance.query.join(
        TechnicalSeminar,
        MemberSeminarAttendance.seminar_id == TechnicalSeminar.id
    ).with_entities(
        MemberSeminarAttendance.uid,
        TechnicalSeminar.timestamp,
        TechnicalSeminar.approved
    ).filter(
        TechnicalSeminar.approved,
        TechnicalSeminar.timestamp >= start_of_year()
    ).with_entities(
        MemberSeminarAttendance.uid,
        TechnicalSeminar.name
    ).all()

    account_ts_attendance_dict = {}

    for row in account_ts_attendance_query:
        if not row[0] in account_ts_attendance_dict:
            account_ts_attendance_dict[row[0]] = []

            account_ts_attendance_dict[row[0]].append(row[1])

    # freshmen who have accounts
    for member in members:
        uid = member.uid
        name = member.cn
        freshman_data = FreshmanEvalData.query.filter(
            FreshmanEvalData.eval_date > start_of_year(),
            FreshmanEvalData.uid == uid).first()

        if freshman_data is None:
            continue
        if freshman_data.freshman_eval_result != "Pending" and internal:
            continue

        member_missed_hms = []

        if account_hm_missed.get(uid, 0) != 0:
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

        cms_attended = account_cm_count.get(uid, 0)

        member_info = {
            'name': name,
            'uid': uid,
            'eval_date': freshman_data.eval_date.strftime("%Y-%m-%d"),
            'signatures_missed': freshman_data.signatures_missed,
            'committee_meetings': cms_attended,
            'committee_meetings_passed': cms_attended >= 6,
            'house_meetings_missed': member_missed_hms,
            'technical_seminars': account_ts_attendance_dict.get(uid, []),
            'social_events': freshman_data.social_events,
            'comments': freshman_data.other_notes,
            'ldap_account': True,
            'status': freshman_data.freshman_eval_result
        }
        ie_members.append(member_info)

    ie_members.sort(key=lambda x: len(x['house_meetings_missed']))
    ie_members.sort(key=lambda x: x['committee_meetings'], reverse=True)
    ie_members.sort(key=lambda x: x['signatures_missed'])
    ie_members.sort(key=lambda x: x['status'] == "Passed")

    if internal:
        return ie_members

    # return names in 'first last (username)' format
    return render_template('intro_evals.html',
                           username=user_dict['username'],
                           members=ie_members)
