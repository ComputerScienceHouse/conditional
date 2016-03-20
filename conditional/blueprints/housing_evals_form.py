from flask import Blueprint
from flask import render_template
from flask import request

housing_evals_form_bp = Blueprint('housing_evals_form_bp', __name__)

@housing_evals_form_bp.route('/housing_evals_form/')
def display_housing_evals_form():
    # get user data

    import db.models as models

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
        models.HousingEvalsSubmission.query.all()]

    # return names in 'first last (username)' format
    return render_template('housing_evals_form.html',
                           username = user_name,
                           housing_evals = housing_evals,
                           housing_evals_len = len(housing_evals))

@housing_evals_form_bp.route('/housing_evals/submit', methods=['POST'])
def display_housing_evals_submit_form():

    from db.database import db_session
    import db.models as models

    user_name = request.headers.get('x-webauth-user')

    social_attended = request.form.get('social_attended')
    social_hosted = request.form.get('social_hosted')
    seminars_attended = request.form.get('seminars_attended')
    seminars_hosted = request.form.get('seminars_hosted')
    projects = request.form.get('projects')
    comments = request.form.get('comments')

    hEval = models.HousingEvalsSubmission(user_name, social_attended,
        social_hosted, seminars_attended, seminars_hosted,
        projects, comments)

    db_session.add(hEval)
    db_session.commit()
    return "", 200
