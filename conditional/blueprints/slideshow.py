import json
import uuid

from datetime import datetime

import structlog

from flask import Blueprint, jsonify, redirect, request

from conditional.util.flask import render_template
from conditional.blueprints.intro_evals import display_intro_evals
from conditional.blueprints.spring_evals import display_spring_evals

from conditional.util.ldap import ldap_is_eval_director, ldap_get_member

from conditional.models.models import CurrentCoops
from conditional.models.models import FreshmanEvalData
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import OnFloorStatusAssigned
from conditional.models.models import SpringEval

from conditional import db


logger = structlog.get_logger()

slideshow_bp = Blueprint('slideshow_bp', __name__)


@slideshow_bp.route('/slideshow/intro')
def slideshow_intro_display():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display intro slideshow')

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
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve intro members slideshow data')

    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_intro_evals(internal=True))


@slideshow_bp.route('/slideshow/intro/review', methods=['POST'])
def slideshow_intro_review():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit intro member evaluation')

    # get user data
    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    uid = post_data['uid']
    status = post_data['status']

    logger.info("backend", action="submit intro eval for %s status: %s" % (uid, status))
    FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == uid and
        FreshmanEvalData.active). \
        update(
        {
            'freshman_eval_result': status
        })

    if status == "Failed":
        for mca in MemberCommitteeAttendance.query.filter(MemberCommitteeAttendance.uid == uid):
            db.session.delete(mca)
        for mts in MemberSeminarAttendance.query.filter(MemberSeminarAttendance.uid == uid):
            db.session.delete(mts)
        for mhm in MemberHouseMeetingAttendance.query.filter(MemberHouseMeetingAttendance.uid == uid):
            db.session.delete(mhm)
        for mof in OnFloorStatusAssigned.query.filter(OnFloorStatusAssigned.uid == uid):
            db.session.delete(mof)
        for mco in CurrentCoops.query.filter(CurrentCoops.uid == uid):
            db.session.delete(mco)
        for mse in SpringEval.query.filter(SpringEval.uid == uid):
            db.session.delete(mse)
        logger.info("backend", action="delete user data for %s" % (uid))

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@slideshow_bp.route('/slideshow/spring')
def slideshow_spring_display():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display membership evaluations slideshow')

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
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='retreive membership evaluations slideshow daat')

    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_spring_evals(internal=True))


@slideshow_bp.route('/slideshow/spring/review', methods=['POST'])
def slideshow_spring_review():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit membership evaulation')

    # get user data
    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    uid = post_data['uid']
    status = post_data['status']

    logger.info("backend", action="submit spring eval for %s status: %s" % (uid, status))

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
