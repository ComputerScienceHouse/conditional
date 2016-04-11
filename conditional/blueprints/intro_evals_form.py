from flask import Blueprint
from flask import render_template
from flask import request

intro_evals_form_bp = Blueprint('intro_evals_form_bp', __name__)

@intro_evals_form_bp.route('/intro_evals_form/')
def display_intro_evals_form():
    # get user data
    import db.models as models

    user_name = request.headers.get('x-webauth-user')

    evalData = models.FreshmanEvalData.query.filter(
                models.FreshmanEvalData.uid == user_name).first()
    # return names in 'first last (username)' format
    return render_template('intro_evals_form.html',
                           username = user_name,
                           social_events = evalData.social_events,
                           other_notes = evalData.other_notes)

@intro_evals_form_bp.route('/intro_evals/submit', methods=['POST'])
def submit_intro_evals():
    from db.database import db_session
    import db.models as models
    user_name = request.headers.get('x-webauth-user')

    post_data = request.get_json()
    social_events = post_data['social_events']
    comments = post_data['comments']

    models.FreshmanEvalData.query.filter(
        models.FreshmanEvalData.uid == user_name).\
        update(
            {
                'social_events': social_events,
                'other_notes': comments
            })

    return "", 200
