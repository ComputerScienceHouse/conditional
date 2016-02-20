from flask import Blueprint
from flask import render_template
from flask import request

spring_evals_bp = Blueprint('spring_evals_bp', __name__)

@spring_evals_bp.route('/spring_evals/')
def display_spring_evals():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    members = [
                {
                    'name': "Liam Middlebrook",
                    'uid': 'loothelion',
                    'committee_meetings': 24,
                    'house_meetings_missed': [{'date': "aprial fools fayas ads", 'reason': "I was playing videogames"}],
                    'major_projects': [
                        {
                            'name': "open container",
                            'status': "Passed",
                            'description': "Riding With A Flask"
                        }],
                    'major_projects_len': 1,
                    'major_project_passed': True,
                    'social_events': "",
                    'comments': "please don't fail me",
                    'result': 'Pending'
                },
                {
                    'name': "Julien Eid",
                    'uid': 'jeid',
                    'committee_meetings': 69,
                    'house_meetings_missed': [],
                    'major_projects': [
                        {
                            'name': "wii-u shit",
                            'status': "Failed",
                            'description': "Rot 3 Encryption"
                        }],
                    'major_projects_len': 1,
                    'major_project_passed': False,
                    'social_events': "Manipulation and Opportunism",
                    'comments': "imdabes",
                    'result': 'Passed'
                }
            ]
    # return names in 'first last (username)' format
    return render_template('spring_evals.html',
                            username = user_name,
                            members = members)
