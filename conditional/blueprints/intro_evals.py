from datetime import datetime
import uuid
import structlog

from flask import Blueprint, request

from conditional.util.ldap import ldap_get_intro_members
from conditional.util.ldap import ldap_get_name

from conditional.models.models import FreshmanCommitteeAttendance
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import FreshmanAccount
from conditional.models.models import FreshmanEvalData
from conditional.models.models import FreshmanHouseMeetingAttendance
from conditional.models.models import FreshmanSeminarAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import HouseMeeting
from conditional.models.models import TechnicalSeminar
from conditional.util.flask import render_template

intro_evals_bp = Blueprint('intro_evals_bp', __name__)

logger = structlog.get_logger()


@intro_evals_bp.route('/intro_evals/')
def display_intro_evals(internal=False):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display intro evals listing')

    # get user data
    def get_uid_cm_count(member_id):
        return len([a for a in MemberCommitteeAttendance.query.filter(
            MemberCommitteeAttendance.uid == member_id)])

    def get_fid_cm_count(member_id):
        return len([a for a in FreshmanCommitteeAttendance.query.filter(
            FreshmanCommitteeAttendance.fid == member_id)])

    user_name = None
    if not internal:
        user_name = request.headers.get('x-webauth-user')

    members = [m['uid'] for m in ldap_get_intro_members()]

    ie_members = []

    # freshmen who don't have accounts
    fids = [f for f in FreshmanAccount.query.filter(
        FreshmanAccount.eval_date > datetime.now())]

    for fid in fids:
        h_meetings = [m.meeting_id for m in
                      FreshmanHouseMeetingAttendance.query.filter(
                          FreshmanHouseMeetingAttendance.fid == fid.id
                      ).filter(
                          FreshmanHouseMeetingAttendance.attendance_status == "Absent"
                      )]

        if fid.signatures_missed is None:
            signatures_missed = -1
        else:
            signatures_missed = fid.signatures_missed

        freshman = {
            'name': fid.name,
            'uid': fid.id,
            'eval_date': fid.eval_date.strftime("%Y-%m-%d"),
            'signatures_missed': signatures_missed,
            'committee_meetings': get_fid_cm_count(fid.id),
            'committee_meetings_passed': get_fid_cm_count(fid.id) >= 10,
            'house_meetings_missed':
                [
                    {
                        "date": m.date.strftime("%Y-%m-%d"),
                        "reason":
                            FreshmanHouseMeetingAttendance.query.filter(
                                FreshmanHouseMeetingAttendance.fid == fid.id).filter(
                                FreshmanHouseMeetingAttendance.meeting_id == m.id).first().excuse
                    }
                    for m in HouseMeeting.query.filter(
                        HouseMeeting.id.in_(h_meetings)
                    )
                ],
            'technical_seminars':
                [s.name for s in TechnicalSeminar.query.filter(
                    TechnicalSeminar.id.in_(
                        [a.seminar_id for a in FreshmanSeminarAttendance.query.filter(
                            FreshmanSeminarAttendance.fid == fid.id)]
                    ))
                 ],
            'social_events': '',
            'freshman_project': "Pending",
            'comments': "",
            'ldap_account': False,
            'status': "Pending"
        }
        ie_members.append(freshman)

    # freshmen who have accounts
    for member_uid in members:
        uid = member_uid[0].decode('utf-8')
        freshman_data = FreshmanEvalData.query.filter(
            FreshmanEvalData.uid == uid).first()

        if freshman_data is None:
            continue
        elif freshman_data.freshman_eval_result != "Pending" and internal:
            continue

        h_meetings = [m.meeting_id for m in
                      MemberHouseMeetingAttendance.query.filter(
                          MemberHouseMeetingAttendance.uid == uid
                      ).filter(
                          MemberHouseMeetingAttendance.attendance_status == "Absent"
                      )]
        member = {
            'name': ldap_get_name(uid),
            'uid': uid,
            'eval_date': freshman_data.eval_date.strftime("%Y-%m-%d"),
            'signatures_missed': freshman_data.signatures_missed,
            'committee_meetings': get_uid_cm_count(uid),
            'committee_meetings_passed': get_uid_cm_count(uid) >= 10,
            'house_meetings_missed':
                [
                    {
                        "date": m.date.strftime("%Y-%m-%d"),
                        "reason":
                            MemberHouseMeetingAttendance.query.filter(
                                MemberHouseMeetingAttendance.uid == uid).filter(
                                MemberHouseMeetingAttendance.meeting_id == m.id).first().excuse
                    }
                    for m in HouseMeeting.query.filter(
                        HouseMeeting.id.in_(h_meetings)
                    )
                ],
            'technical_seminars':
                [s.name for s in TechnicalSeminar.query.filter(
                    TechnicalSeminar.id.in_(
                        [a.seminar_id for a in MemberSeminarAttendance.query.filter(
                            MemberSeminarAttendance.uid == uid)]
                    ))
                 ],
            'social_events': freshman_data.social_events,
            'freshman_project': freshman_data.freshman_project,
            'comments': freshman_data.other_notes,
            'ldap_account': True,
            'status': freshman_data.freshman_eval_result
        }
        ie_members.append(member)

    ie_members.sort(key=lambda x: x['freshman_project'] == "Passed")
    ie_members.sort(key=lambda x: len(x['house_meetings_missed']))
    ie_members.sort(key=lambda x: x['committee_meetings'], reverse=True)
    ie_members.sort(key=lambda x: x['signatures_missed'])
    ie_members.sort(key=lambda x: x['status'] == "Passed")

    if internal:
        return ie_members
    else:
        # return names in 'first last (username)' format
        return render_template(request,
                               'intro_evals.html',
                               username=user_name,
                               members=ie_members)
