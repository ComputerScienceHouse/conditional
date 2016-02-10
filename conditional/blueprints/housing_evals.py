from flask import Blueprint
from flask import render_template
from flask import request

housing_evals_bp = Blueprint('housing_evals_bp', __name__)

@housing_evals_bp.route('/housing_evals')
@housing_evals_bp.route('/housing_evals/')
def display_housing_evals():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    members = [
                {
                    'name': "Liam Middlebrook",
                    'social_attended': "Halloween Party\nHipster Movie Night",
                    'social_hosted': "None",
                    'seminars_attended': "C With Travis\nGetting Swifty With Harlan",
                    'seminars_hosted': "Missing License Wat!?",
                    'projects': "open-container\nConditional (the real pvals killer)",
                    'comments': "please don't fail me",
                    'points_awarded': 3,
                    'points': 0
                }
            ]
    # return names in 'first last (username)' format
    return render_template('housing_evals.html',
                            username = user_name,
                            members = members)
