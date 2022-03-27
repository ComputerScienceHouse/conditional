from datetime import datetime

import structlog
from flask import Blueprint, request

from conditional import start_of_year, auth
from conditional.models.models import DirectorshipMeeting
from conditional.models.models import FreshmanAccount
from conditional.models.models import FreshmanDirectorshipAttendance
from conditional.models.models import FreshmanEvalData
from conditional.models.models import FreshmanHouseMeetingAttendance
from conditional.models.models import FreshmanSeminarAttendance
from conditional.models.models import HouseMeeting
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import TechnicalSeminar
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_get_intro_members
from conditional.util.member import get_directorship_meetings, get_house_meetings

intro_evals_bp = Blueprint('intro_evals_bp', __name__)

logger = structlog.get_logger()


@intro_evals_bp.route('/intro_evals/')
@auth.oidc_auth
@get_user
def display_intro_evals(internal=False, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Intro Evals Listing')

    def get_frosh_directorship_meetings(fid):
        """
        Get all directorship meetings from a given frosh account id
        """
        c_meetings = [{
            "uid": cm[0],
            "timestamp": cm[1],
            "directorship": cm[2]
        } for cm in DirectorshipMeeting.query.join(
            FreshmanDirectorshipAttendance,
            FreshmanDirectorshipAttendance.meeting_id == DirectorshipMeeting.id
            ).with_entities(
                FreshmanDirectorshipAttendance.fid,
                DirectorshipMeeting.timestamp,
                DirectorshipMeeting.directorship
                ).filter(
                    DirectorshipMeeting.timestamp > start_of_year(),
                    FreshmanDirectorshipAttendance.fid == fid,
                    DirectorshipMeeting.approved == True # pylint: disable=singleton-comparison
                    ).all()]
        return c_meetings

    members = ldap_get_intro_members()

    ie_members = []

    # freshmen who don't have accounts
    fids = list(FreshmanAccount.query.filter(
        FreshmanAccount.eval_date > start_of_year(),
        FreshmanAccount.eval_date > datetime.now()))

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
            'directorship_meetings': [{
                "uid": cm['uid'],
                "timestamp": cm['timestamp'].strftime("%Y-%m-%d"),
                "directorship": cm['directorship']
            } for cm in get_frosh_directorship_meetings(fid.id)],
            'directorship_meetings_passed': len(get_frosh_directorship_meetings(fid.id)) >= 6,
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
                            FreshmanSeminarAttendance.fid == fid.id)
                            if TechnicalSeminar.query.filter(TechnicalSeminar.id == a.seminar_id).first().approved]
                    ))
                 ],
            'social_events': '',
            'comments': "",
            'ldap_account': False,
            'status': "Pending"
        }
        ie_members.append(freshman)

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

        h_meetings = [m.meeting_id for m in get_house_meetings(member, only_absent=True)]
        member_info = {
            'name': name,
            'uid': uid,
            'eval_date': freshman_data.eval_date.strftime("%Y-%m-%d"),
            'signatures_missed': freshman_data.signatures_missed,
            'directorship_meetings': [{
                "uid": cm['uid'],
                "timestamp": cm['timestamp'].strftime("%Y-%m-%d"),
                "directorship": cm['directorship']
            } for cm in get_directorship_meetings(member)],
            'directorship_meetings_passed': len(get_directorship_meetings(member)) >= 6,
            'house_meetings_missed':
                [
                    {
                        "date": m.date.strftime("%Y-%m-%d"),
                        "reason":
                            MemberHouseMeetingAttendance.query.filter(
                                MemberHouseMeetingAttendance.uid == uid,
                                MemberHouseMeetingAttendance.meeting_id == m.id).first().excuse
                    }
                    for m in HouseMeeting.query.filter(
                        HouseMeeting.id.in_(h_meetings)
                    )
                ],
            'technical_seminars':
                [seminar.name for seminar in TechnicalSeminar.query.join(
                    MemberSeminarAttendance,
                    MemberSeminarAttendance.seminar_id == TechnicalSeminar.id
                    ).with_entities(
                        TechnicalSeminar.name
                        ).filter(
                            TechnicalSeminar.timestamp > start_of_year(),
                            MemberSeminarAttendance.uid == member.uid,
                            TechnicalSeminar.approved == True # pylint: disable=singleton-comparison
                            ).all()],
            'social_events': freshman_data.social_events,
            'comments': freshman_data.other_notes,
            'ldap_account': True,
            'status': freshman_data.freshman_eval_result
        }
        ie_members.append(member_info)

    ie_members.sort(key=lambda x: len(x['house_meetings_missed']))
    ie_members.sort(key=lambda x: x['directorship_meetings_passed'], reverse=True)
    ie_members.sort(key=lambda x: x['signatures_missed'])
    ie_members.sort(key=lambda x: x['status'] == "Passed")

    if internal:
        return ie_members

    # return names in 'first last (username)' format
    return render_template('intro_evals.html',
                           username=user_dict['username'],
                           members=ie_members)
