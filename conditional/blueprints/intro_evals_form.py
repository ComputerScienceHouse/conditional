import structlog

from flask import Blueprint, request, redirect, jsonify

from conditional.models.models import FreshmanEvalData
from conditional.models.models import EvalSettings
from conditional.util.ldap import ldap_is_intromember
from conditional.util.flask import render_template

from conditional import db, get_user, auth

logger = structlog.get_logger()

intro_evals_form_bp = Blueprint('intro_evals_form_bp', __name__)


@intro_evals_form_bp.route('/intro_evals_form/')
@auth.oidc_auth
@get_user
def display_intro_evals_form(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Intro Evals Form')

    if not ldap_is_intromember(user_dict['account']):
        return redirect("/dashboard")
    eval_data = FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == user_dict['username']).first()

    is_open = EvalSettings.query.first().intro_form_active
    # return names in 'first last (username)' format
    return render_template('intro_evals_form.html',
                           username=user_dict['username'],
                           social_events=eval_data.social_events,
                           other_notes=eval_data.other_notes,
                           is_open=is_open)


@intro_evals_form_bp.route('/intro_evals/submit', methods=['POST'])
@auth.oidc_auth
@get_user
def submit_intro_evals(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Submit Intro Evals Form')

    post_data = request.get_json()
    social_events = post_data['socialEvents']
    comments = post_data['comments']

    FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == user_dict['username']). \
        update(
        {
            'social_events': social_events,
            'other_notes': comments
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200
