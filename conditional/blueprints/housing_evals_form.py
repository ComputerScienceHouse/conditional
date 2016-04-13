from flask import Blueprint
from flask import request
from flask import jsonify

from db.models import HousingEvalsSubmission
from db.models import EvalSettings
from util.flask import render_template

housing_evals_form_bp = Blueprint('housing_evals_form_bp', __name__)

@housing_evals_form_bp.route('/housing_evals_form/')
def display_housing_evals_form():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    evalData = HousingEvalsSubmission.query.filter(
        HousingEvalsSubmission.uid == user_name).first()

    evalData = \
        {
            'social_attended': evalData.social_attended,
            'social_hosted': evalData.social_hosted,
            'seminars_attended': evalData.technical_attended,
            'seminars_hosted': evalData.technical_hosted,
            'projects': evalData.projects,
            'comments': evalData.comments
        }

    is_open = EvalSettings.query.first().housing_form_active

    # return names in 'first last (username)' format
    return render_template(request,
                           'housing_evals_form.html',
                           username = user_name,
                           eval_data = evalData,
                           is_open = is_open)

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

    if HousingEvalsSubmission.query.filter(
        HousingEvalsSubmission.uid == user_name).count() > 0:
        HousingEvalsSubmission.query.filter(
            HousingEvalsSubmission.uid == user_name).\
            update(
                {
                    'social_attended': social_attended,
                    'social_hosted': social_hosted,
                    'technical_attended': seminars_attended,
                    'technical_hosted': seminars_hosted,
                    'projects': projects,
                    'comments': comments
                })
    else:
        hEval = HousingEvalsSubmission(user_name, social_attended,
            social_hosted, seminars_attended, seminars_hosted,
            projects, comments)

        db_session.add(hEval)
    db_session.commit()
    return jsonify({"success": True}), 200
