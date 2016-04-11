from flask import Blueprint
from flask import render_template
from flask import request

from db.models import HousingEvalsSubmission
housing_evals_form_bp = Blueprint('housing_evals_form_bp', __name__)

@housing_evals_form_bp.route('/housing_evals_form/')
def display_housing_evals_form():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    housing_evals = [
            {
                'username': e.uid,
                'social_attended': e.social_attended,
                'social_hosted': e.social_hosted,
                'seminars_attended': e.technical_attended,
                'seminars_hosted': e.technical_hosted,
                'projects': e.projects,
                'comments': e.comments
            } for e in
        HousingEvalsSubmission.query.all()]

    # return names in 'first last (username)' format
    return render_template('housing_evals_form.html',
                           username = user_name,
                           housing_evals = housing_evals,
                           housing_evals_len = len(housing_evals))

@housing_evals_form_bp.route('/housing_evals/submit', methods=['POST'])
def display_housing_evals_submit_form():

    from db.database import db_session
    user_name = request.headers.get('x-webauth-user')

    post_data = request.get_json()
    social_attended = post_data['social_attended']
    social_hosted = post_data['social_hosted']
    seminars_attended = post_data['seminars_attended']
    seminars_hosted = post_data['seminars_hosted']
    projects = post_data['projects']
    comments = post_data['comments']

    hEval = HousingEvalsSubmission(user_name, social_attended,
        social_hosted, seminars_attended, seminars_hosted,
        projects, comments)

    db_session.add(hEval)
    db_session.commit()
    return "", 200
