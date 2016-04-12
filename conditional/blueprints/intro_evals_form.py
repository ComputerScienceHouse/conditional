from flask import Blueprint
from flask import render_template
from flask import request

from db.models import FreshmanEvalData
from db.models import EvalSettings

intro_evals_form_bp = Blueprint('intro_evals_form_bp', __name__)

@intro_evals_form_bp.route('/intro_evals_form/')
def display_intro_evals_form():
    # get user data
    user_name = request.headers.get('x-webauth-user')

    evalData = FreshmanEvalData.query.filter(
                FreshmanEvalData.uid == user_name).first()

    is_open = EvalSettings.all().first().intro_form_active
    # return names in 'first last (username)' format
    return render_template('intro_evals_form.html',
                           username = user_name,
                           social_events = evalData.social_events,
                           other_notes = evalData.other_notes,
                           is_open = is_open)

@intro_evals_form_bp.route('/intro_evals/submit', methods=['POST'])
def submit_intro_evals():
    from db.database import db_session
    user_name = request.headers.get('x-webauth-user')

    post_data = request.get_json()
    social_events = post_data['social_events']
    comments = post_data['comments']

    FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == user_name).\
        update(
            {
                'social_events': social_events,
                'other_notes': comments
            })

    from db.database import db_session
    db_session.flush()
    db_session.commit()
    return "", 200
