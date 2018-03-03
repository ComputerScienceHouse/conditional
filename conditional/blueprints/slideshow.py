import json
from datetime import datetime

import structlog
from flask import Blueprint, jsonify, redirect, request

from conditional import db, auth
from conditional.blueprints.intro_evals import display_intro_evals
from conditional.blueprints.spring_evals import display_spring_evals
from conditional.models.models import FreshmanEvalData
from conditional.models.models import SpringEval
from conditional.util.auth import get_username
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_is_eval_director, ldap_get_member

logger = structlog.get_logger()

slideshow_bp = Blueprint('slideshow_bp', __name__)


@slideshow_bp.route('/slideshow/intro')
@auth.oidc_auth
@get_username
def slideshow_intro_display(username=None):
    log = logger.new(request=request)
    log.info('Display Intro Slideshow')

    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard")

    return render_template('intro_eval_slideshow.html',
                           username=username,
                           date=datetime.now().strftime("%Y-%m-%d"),
                           members=display_intro_evals(internal=True))


@slideshow_bp.route('/slideshow/intro/members')
def slideshow_intro_members():
    log = logger.new(request=request)
    log.info('Retrieve Intro Members Slideshow Data')

    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_intro_evals(internal=True))


@slideshow_bp.route('/slideshow/intro/review', methods=['POST'])
@auth.oidc_auth
@get_username
def slideshow_intro_review(username=None):
    log = logger.new(request=request)

    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    uid = post_data['uid']
    status = post_data['status']

    log.info('Intro Eval for {}: {}'.format(uid, status))
    FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == uid and
        FreshmanEvalData.active). \
        update(
        {
            'freshman_eval_result': status
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@slideshow_bp.route('/slideshow/spring')
@auth.oidc_auth
@get_username
def slideshow_spring_display(username=None):
    log = logger.new(request=request)
    log.info('Display Membership Evaluations Slideshow')

    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard")

    return render_template('spring_eval_slideshow.html',
                           username=username,
                           date=datetime.now().strftime("%Y-%m-%d"),
                           members=display_spring_evals(internal=True))


@slideshow_bp.route('/slideshow/spring/members')
def slideshow_spring_members():
    log = logger.new(request=request)
    log.info('Retreive Membership Evaluations Slideshow Data')

    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_spring_evals(internal=True))


@slideshow_bp.route('/slideshow/spring/review', methods=['POST'])
@auth.oidc_auth
@get_username
def slideshow_spring_review(username=None):
    log = logger.new(request=request)

    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    uid = post_data['uid']
    status = post_data['status']

    log.info('Spring Eval for {}: {}'.format(uid, status))

    SpringEval.query.filter(
        SpringEval.uid == uid and
        SpringEval.active). \
        update(
        {
            'status': status
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200
