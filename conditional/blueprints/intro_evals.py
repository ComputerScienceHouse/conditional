from flask import Blueprint
from flask import request

intro_evals_bp = Blueprint('intro_evals_bp', __name__)

from util.ldap import ldap_get_intro_members
from util.ldap import ldap_get_name

from db.models import MemberCommitteeAttendance
from db.models import FreshmanEvalData
from db.models import MemberHouseMeetingAttendance
from db.models import MemberSeminarAttendance
from db.models import HouseMeeting
from db.models import TechnicalSeminar
from util.flask import render_template

import structlog
import uuid

logger = structlog.get_logger()

@intro_evals_bp.route('/intro_evals/')
def display_intro_evals(internal=False):
    log = logger.new(request_id=str(uuid.uuid4()))
    log.info('frontend', action='display intro evals listing')

    # get user data
    def get_cm_count(uid):
        return len([a for a in MemberCommitteeAttendance.query.filter(
            MemberCommitteeAttendance.uid == uid)])

    user_name = None
    if not internal:
        user_name = request.headers.get('x-webauth-user')

    members = [m['uid'] for m in ldap_get_intro_members()]

    ie_members = []
    for member_uid in members:
        uid = member_uid[0].decode('utf-8')
        freshman_data = FreshmanEvalData.query.filter(
            FreshmanEvalData.uid == uid).first()
        ## Add continue for if freshman_data.status != Pending
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
                    'committee_meetings': get_cm_count(uid),
                    'committee_meetings_passed': get_cm_count(uid) >= 10,
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
                    'status': freshman_data.freshman_eval_result
                 }
        ie_members.append(member)

    ie_members.sort(key = lambda x: x['freshman_project'] == "Passed")
    ie_members.sort(key = lambda x: len(x['house_meetings_missed']))
    ie_members.sort(key = lambda x: x['committee_meetings'], reverse=True)
    ie_members.sort(key = lambda x: x['signatures_missed'])

    if internal:
        return ie_members
    else:
        # return names in 'first last (username)' format
        return render_template(request,
                                'intro_evals.html',
                                username = user_name,
                                members = ie_members)
