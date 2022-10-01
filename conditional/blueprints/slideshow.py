import json
from datetime import datetime

import structlog
from flask import Blueprint, jsonify, redirect, request

from conditional import db, auth
from conditional.blueprints.intro_evals import display_intro_evals
from conditional.blueprints.spring_evals import display_spring_evals
from conditional.models.models import FreshmanEvalData
from conditional.models.models import SpringEval
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_is_eval_director, ldap_is_intromember, ldap_set_failed, ldap_set_bad_standing, \
    ldap_set_inactive, ldap_get_member, ldap_set_not_intro_member, ldap_get_housingpoints, ldap_set_housingpoints

logger = structlog.get_logger()

slideshow_bp = Blueprint('slideshow_bp', __name__)


@slideshow_bp.route('/slideshow/intro')
@auth.oidc_auth
@get_user
def slideshow_intro_display(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Intro Slideshow')

    if not ldap_is_eval_director(user_dict['account']):
        return redirect("/dashboard")

    return render_template('intro_eval_slideshow.html',
                           username=user_dict['username'],
                           date=datetime.now().strftime("%Y-%m-%d"),
                           members=display_intro_evals(internal=True))


@slideshow_bp.route('/slideshow/intro/members')
@auth.oidc_auth
@get_user
def slideshow_intro_members(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Retrieve Intro Members Slideshow Data')

    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_intro_evals(internal=True))


@slideshow_bp.route('/slideshow/intro/review', methods=['POST'])
@auth.oidc_auth
@get_user
def slideshow_intro_review(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
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
@get_user
def slideshow_spring_display(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Membership Evaluations Slideshow')

    if not ldap_is_eval_director(user_dict['account']):
        return redirect("/dashboard")

    return render_template('spring_eval_slideshow.html',
                           username=user_dict['username'],
                           date=datetime.now().strftime("%Y-%m-%d"),
                           members=display_spring_evals(internal=True))


@slideshow_bp.route('/slideshow/spring/members')
@auth.oidc_auth
@get_user
def slideshow_spring_members(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Retreive Membership Evaluations Slideshow Data')

    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_spring_evals(internal=True))


@slideshow_bp.route('/slideshow/spring/review', methods=['POST'])
@auth.oidc_auth
@get_user
def slideshow_spring_review(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
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

    # Automate ldap group organizing
    account = ldap_get_member(uid)

    if status == "Passed":
        if ldap_is_intromember(account):
            ldap_set_not_intro_member(account)
        ldap_set_housingpoints(account, ldap_get_housingpoints(account) + 2)
    elif status == "Failed":
        if ldap_is_intromember(account):
            ldap_set_failed(account)
            ldap_set_inactive(account)
        else:
            ldap_set_bad_standing(account)

    return jsonify({"success": True}), 200
