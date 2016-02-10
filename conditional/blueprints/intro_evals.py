from flask import Blueprint
from flask import render_template
from flask import request

intro_evals_bp = Blueprint('intro_evals_bp', __name__)

@intro_evals_bp.route('/intro_evals')
@intro_evals_bp.route('/intro_evals/')
def display_intro_evals():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    members = [
                {
                    'name': "Liam Middlebrook",
                    'packet_due': '2015-12-23',
                    'eval_date': '2016-02-13',
                    'signatures_missed': 3,
                    'committee_meetings': 24,
                    'committee_meetings_passed': False,
                    'house_meetings_missed': 0,
                    'house_meetings_comments': "",
                    'technical_seminars': "Seminar 1\nSeminar 2",
                    'techincal_seminars_passed': True,
                    'social_events': "",
                    'freshmen_project': False,
                    'comments': "please don't fail me",
                    'result': 'Pending'
                }
            ]

    # return names in 'first last (username)' format
    return render_template('intro_evals.html',
                            username = user_name,
                            members = members)

