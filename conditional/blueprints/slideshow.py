import json

from datetime import datetime

import structlog

from flask import Blueprint, jsonify, redirect, request

from conditional.util.flask import render_template
from conditional.blueprints.intro_evals import display_intro_evals
from conditional.blueprints.spring_evals import display_spring_evals

from conditional.util.ldap import ldap_is_eval_director, ldap_get_member

from conditional.models.models import FreshmanEvalData
from conditional.models.models import SpringEval

from conditional import db


logger = structlog.get_logger()

slideshow_bp = Blueprint('slideshow_bp', __name__)


@slideshow_bp.route('/slideshow/intro')
def slideshow_intro_display():
    log = logger.new(request=request)
    log.info('Display Intro Slideshow')

    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard")

    return render_template(request,
                           'intro_eval_slideshow.html',
                           username=user_name,
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
def slideshow_intro_review():
    log = logger.new(request=request)

    # get user data
    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

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
def slideshow_spring_display():
    log = logger.new(request=request)
    log.info('Display Membership Evaluations Slideshow')

    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard")

    return render_template(request,
                           'spring_eval_slideshow.html',
                           username=user_name,
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
def slideshow_spring_review():
    log = logger.new(request=request)

    # get user data
    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

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
