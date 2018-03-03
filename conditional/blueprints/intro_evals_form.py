import structlog

from flask import Blueprint, request, redirect, jsonify

from conditional.models.models import FreshmanEvalData
from conditional.models.models import EvalSettings
from conditional.util.ldap import ldap_is_intromember
from conditional.util.ldap import ldap_get_member
from conditional.util.flask import render_template

from conditional import db, get_username, auth

logger = structlog.get_logger()

intro_evals_form_bp = Blueprint('intro_evals_form_bp', __name__)


@intro_evals_form_bp.route('/intro_evals_form/')
@auth.oidc_auth
@get_username
def display_intro_evals_form(username=None):
    log = logger.new(request=request)
    log.info('Display Intro Evals Form')

    account = ldap_get_member(username)

    if not ldap_is_intromember(account):
        return redirect("/dashboard")
    eval_data = FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == username).first()

    is_open = EvalSettings.query.first().intro_form_active
    # return names in 'first last (username)' format
    return render_template('intro_evals_form.html',
                           username=username,
                           social_events=eval_data.social_events,
                           other_notes=eval_data.other_notes,
                           is_open=is_open)


@intro_evals_form_bp.route('/intro_evals/submit', methods=['POST'])
@auth.oidc_auth
@get_username
def submit_intro_evals(username=None):
    log = logger.new(request=request)
    log.info('Submit Intro Evals Form')

    post_data = request.get_json()
    social_events = post_data['socialEvents']
    comments = post_data['comments']

    FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == username). \
        update(
        {
            'social_events': social_events,
            'other_notes': comments
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200
