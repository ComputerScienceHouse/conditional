from flask import Blueprint
from flask import render_template
from flask import request

spring_evals_bp = Blueprint('spring_evals_bp', __name__)

@spring_evals_bp.route('/spring_evals')
@spring_evals_bp.route('/spring_evals/')
def display_spring_evals():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    members = [
                {
                    'name': "Liam Middlebrook",
                    'committee_meetings': 24,
                    'house_meetings_missed': 0,
                    'house_meetings_comments': "",
                    'major_project': 'open_container',
                    'major_project_passed': True,
                    'comments': "please don't fail me",
                    'result': 'Pending'
                },
                {
                    'name': "Julien Eid",
                    'committee_meetings': 69,
                    'house_meetings_missed': 0,
                    'house_meetings_comments': "",
                    'major_project': 'wii-u shit',
                    'major_project_passed': True,
                    'comments': "imdabes",
                    'result': 'Passed'
                },
                {
                    'name': "James Forcier",
                    'committee_meetings': 3,
                    'house_meetings_missed': 5,
                    'house_meetings_comments': "",
                    'major_project': 'Bobby Junior',
                    'major_project_passed': False,
                    'comments': "Jazzazazazazzz",
                    'result': 'Failed'
                }
            ]
    # return names in 'first last (username)' format
    return render_template('spring_evals.html',
                            username = user_name,
                            members = members)
