import structlog
from flask import Blueprint, request

from conditional import db, start_of_year, auth
from conditional.models.models import HouseMeeting
from conditional.models.models import MajorProject
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import SpringEval
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_get_active_members
from conditional.util.member import get_directorship_meetings, get_house_meetings, get_required_directorship_meetings

spring_evals_bp = Blueprint('spring_evals_bp', __name__)

logger = structlog.get_logger()


@spring_evals_bp.route('/spring_evals/')
@auth.oidc_auth
@get_user
def display_spring_evals(internal=False, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Membership Evaluations Listing')

    active_members = ldap_get_active_members()

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
        elif spring_entry.status != "Pending" and internal:
            continue

        eval_data = None

        h_meetings = [m.meeting_id for m in get_house_meetings(account, only_absent=True)]
        member = {
            'name': account.cn,
            'uid': uid,
            'status': spring_entry.status,
            'directorship_meetings': len(get_directorship_meetings(account)),
            'req_meetings': get_required_directorship_meetings(account),
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
                    MajorProject.date > start_of_year(),
                    MajorProject.uid == uid)]
        }
        member['major_projects_len'] = len(member['major_projects'])
        member['major_projects_passed'] = [
            {
                'name': p.name,
                'status': p.status,
                'description': p.description
            } for p in MajorProject.query.filter(
                MajorProject.date > start_of_year(),
                MajorProject.status == "Passed",
                MajorProject.uid == uid)]
        member['major_projects_passed_len'] = len(member['major_projects_passed'])
        member['major_project_passed'] = False
        for mp in member['major_projects']:
            if mp['status'] == "Passed":
                member['major_project_passed'] = True
                break

        if internal:
            member['housing_evals'] = eval_data
        sp_members.append(member)

    sp_members.sort(key=lambda x: x['directorship_meetings'], reverse=True)
    sp_members.sort(key=lambda x: len(x['house_meetings_missed']))
    sp_members.sort(key=lambda x: len([p for p in x['major_projects'] if p['status'] == "Passed"]), reverse=True)
    # return names in 'first last (username)' format
    if internal:
        return sp_members

    return render_template('spring_evals.html',
                           username=user_dict['username'],
                           members=sp_members)
