from flask import Blueprint
from flask import render_template
from flask import request

spring_evals_bp = Blueprint('spring_evals_bp', __name__)

from util.ldap import ldap_get_active_members
from util.ldap import ldap_get_name

from db.models import MemberCommitteeAttendance
from db.models import MemberHouseMeetingAttendance
from db.models import MajorProject
from db.models import HouseMeeting

@spring_evals_bp.route('/spring_evals/')
def display_spring_evals():
    def get_cm_count(uid):
        return len([a for a in MemberCommitteeAttendance.query.filter(
            MemberCommitteeAttendance.uid == uid)])

    user_name = request.headers.get('x-webauth-user')

    members = [m['uid'] for m in ldap_get_active_members()]

    sp_members = []
    for member_uid in members:
        uid = member_uid[0].decode('utf-8')
        print(uid)
        h_meetings = [m.meeting_id for m in
            MemberHouseMeetingAttendance.query.filter(
                MemberHouseMeetingAttendance.uid == uid
            ).filter(
                MemberHouseMeetingAttendance.attendance_status == "Absent"
            )]
        member = {
                    'name': ldap_get_name(uid),
                    'uid': uid,
                    'committee_meetings': get_cm_count(uid),
                    'house_meetings_missed':
                        [
                            {
                                "date": m.date,
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

        sp_members.append(member)

    sp_members.sort(key = lambda x: x['major_project_passed'])
    sp_members.sort(key = lambda x: len(x['house_meetings_missed']))
    sp_members.sort(key = lambda x: x['committee_meetings'], reverse=True)
    # return names in 'first last (username)' format
    return render_template('spring_evals.html',
                            username = user_name,
                            members = sp_members)
