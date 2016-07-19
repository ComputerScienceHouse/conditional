from flask import Blueprint
from flask import request

spring_evals_bp = Blueprint('spring_evals_bp', __name__)

from util.ldap import ldap_get_active_members
from util.ldap import ldap_get_name

from db.models import MemberCommitteeAttendance
from db.models import MemberHouseMeetingAttendance
from db.models import MajorProject
from db.models import HouseMeeting
from db.models import SpringEval
from db.models import HousingEvalsSubmission

from util.flask import render_template

import structlog
import uuid

logger = structlog.get_logger()

@spring_evals_bp.route('/spring_evals/')
def display_spring_evals(internal=False):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('frontend', action='display membership evaluations listing')

    def get_cm_count(uid):
        return len([a for a in MemberCommitteeAttendance.query.filter(
            MemberCommitteeAttendance.uid == uid)])

    user_name = None
    if not internal:
        user_name = request.headers.get('x-webauth-user')

    members = [m['uid'] for m in ldap_get_active_members()]

    sp_members = []
    for member_uid in members:
        uid = member_uid[0].decode('utf-8')
        print(uid)
        spring_entry = SpringEval.query.filter(
            SpringEval.uid == uid and
            SpringEval.active).first()

        if spring_entry is None:
            from db.database import db_session

            db_session.add(SpringEval(uid))
            db_session.flush()
            db_session.commit()
            # something bad happened to get here
            print("User did not have existing spring eval data")

        evalData = None
        if internal:
            evalData = HousingEvalsSubmission.query.filter(
                HousingEvalsSubmission.uid == uid).first()

            if HousingEvalsSubmission.query.filter(
                HousingEvalsSubmission.uid == uid).count() > 0:
                evalData = \
                    {
                        'social_attended': evalData.social_attended,
                        'social_hosted': evalData.social_hosted,
                        'seminars_attended': evalData.technical_attended,
                        'seminars_hosted': evalData.technical_hosted,
                        'projects': evalData.projects,
                        'comments': evalData.comments
                    }
        h_meetings = [m.meeting_id for m in
            MemberHouseMeetingAttendance.query.filter(
                MemberHouseMeetingAttendance.uid == uid
            ).filter(
                MemberHouseMeetingAttendance.attendance_status == "Absent"
            )]
        member = {
                    'name': ldap_get_name(uid),
                    'uid': uid,
                    'status': spring_entry.status,
                    'committee_meetings': get_cm_count(uid),
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
                    'major_projects': [
                        {
                            'name': p.name,
                            'status': p.status,
                            'description': p.description
                        } for p in MajorProject.query.filter(
                            MajorProject.uid == uid)]
                }
        member['major_projects_len'] = len(member['major_projects'])
        member['major_project_passed'] = False
        for mp in member['major_projects']:
            if mp['status'] == "Passed":
                member['major_project_passed'] = True
                break

        if internal:
            member['housing_evals'] = evalData
        sp_members.append(member)

    sp_members.sort(key = lambda x: x['committee_meetings'], reverse=True)
    sp_members.sort(key = lambda x: len(x['house_meetings_missed']))
    sp_members.sort(key = lambda x: len([p for p in x['major_projects'] if p['status'] == "Passed"]), reverse=True)
    # return names in 'first last (username)' format
    if internal:
        return sp_members
    else:
        return render_template(request,
                                'spring_evals.html',
                                username = user_name,
                                members = sp_members)
