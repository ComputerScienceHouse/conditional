from flask import Blueprint
from flask import render_template
from flask import request

intro_evals_bp = Blueprint('intro_evals_bp', __name__)

from util.ldap import ldap_get_intro_members, ldap_get_name

@intro_evals_bp.route('/intro_evals/')
def display_intro_evals():
    # get user data
    import db.models as models

    def get_cm_count(uid):
        return len([a for a in models.MemberCommitteeAttendance.query.filter(
            models.MemberCommitteeAttendance.uid == uid)])

    def freshman_cm_pass(uid):
        # TODO FIXME
        # 1 per week for 10 weeks
        return True

    user_name = request.headers.get('x-webauth-user')

    members = [m['uid'] for m in ldap_get_intro_members()]

    ie_members = []
    for member_uid in members:
        uid = member_uid[0].decode('utf-8')
        freshman_data = models.FreshmanEvalData.query.filter(
            models.FreshmanEvalData.uid == uid).first()
        h_meetings = [m.meeting_id for m in
            models.MemberHouseMeetingAttendance.query.filter(
                models.MemberHouseMeetingAttendance.uid == uid
            ).filter(
                models.MemberHouseMeetingAttendance.attendance_status == "Absent"
            )]
        member = {
                    'name': ldap_get_name(uid),
                    'uid': uid,
                    'eval_date': freshman_data.eval_date,
                    'signatures_missed': freshman_data.signatures_missed,
                    'committee_meetings': get_cm_count(uid),
                    'committee_meetings_passed': freshman_cm_pass(uid),
                    'house_meetings_missed':
                        [
                            {
                                "date": m.date,
                                "reason":
    models.MemberHouseMeetingAttendance.query.filter(
        models.MemberHouseMeetingAttendance.uid == uid).filter(
            models.MemberHouseMeetingAttendance.meeting_id == m.id).first().excuse
                            }
                            for m in models.HouseMeeting.query.filter(
                                models.HouseMeeting.id.in_(h_meetings)
                            )
                        ],
                    'technical_seminars':
                        [s.name for s in models.TechnicalSeminar.query.filter(
                            models.TechnicalSeminar.id.in_(
                                [a.seminar_id for a in models.MemberSeminarAttendance.query.filter(
                                    models.MemberSeminarAttendance.uid == uid)]
                            ))
                        ],
                    'social_events': freshman_data.social_events,
                    'freshman_project': freshman_data.freshman_project,
                    'comments': freshman_data.other_notes
                 }
        ie_members.append(member)

    ie_members.sort(key = lambda x: x['freshman_project'] == "Passed")
    ie_members.sort(key = lambda x: len(x['house_meetings_missed']))
    ie_members.sort(key = lambda x: x['committee_meetings'], reverse=True)
    ie_members.sort(key = lambda x: x['signatures_missed'])

    # return names in 'first last (username)' format
    return render_template('intro_evals.html',
                            username = user_name,
                            members = ie_members)

