import uuid
import structlog

from flask import Blueprint, request, redirect, jsonify

from conditional.models.models import FreshmanEvalData
from conditional.models.models import EvalSettings
from conditional.util.ldap import ldap_is_intromember
from conditional.util.flask import render_template

from conditional import db

logger = structlog.get_logger()

intro_evals_form_bp = Blueprint('intro_evals_form_bp', __name__)


@intro_evals_form_bp.route('/intro_evals_form/')
def display_intro_evals_form():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display intro evals form')

    # get user data
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_intromember(user_name):
        return redirect("/dashboard")
    eval_data = FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == user_name).first()

    is_open = EvalSettings.query.first().intro_form_active
    # return names in 'first last (username)' format
    return render_template(request,
                           'intro_evals_form.html',
                           username=user_name,
                           social_events=eval_data.social_events,
                           other_notes=eval_data.other_notes,
                           is_open=is_open)


@intro_evals_form_bp.route('/intro_evals/submit', methods=['POST'])
def submit_intro_evals():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit intro evals form')

    user_name = request.headers.get('x-webauth-user')

    post_data = request.get_json()
    social_events = post_data['socialEvents']
    comments = post_data['comments']

    FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == user_name). \
        update(
        {
            'social_events': social_events,
            'other_notes': comments
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200
