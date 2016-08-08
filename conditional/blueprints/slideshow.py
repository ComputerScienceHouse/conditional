from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request

import json

from util.flask import render_template
from blueprints.intro_evals import display_intro_evals
from blueprints.spring_evals import display_spring_evals

from util.ldap import ldap_get_housing_points
from util.ldap import ldap_set_housingpoints
from util.ldap import ldap_is_eval_director

from db.models import FreshmanEvalData
from db.models import SpringEval
from db.models import HousingEvalsSubmission

from datetime import datetime

import structlog
import uuid

logger = structlog.get_logger()

slideshow_bp = Blueprint('slideshow_bp', __name__)

@slideshow_bp.route('/slideshow/intro')
def slideshow_intro_display():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('frontend', action='display intro slideshow')

    user_name = request.headers.get('x-webauth-user')
    if not ldap_is_eval_director(user_name):
        return redirect("/dashboard")

    return render_template(request,
                           'intro_eval_slideshow.html',
                           username = user_name,
                           date = datetime.utcnow().strftime("%Y-%m-%d"),
                           members = display_intro_evals(internal=True))

@slideshow_bp.route('/slideshow/intro/members')
def slideshow_intro_members():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('api', action='retreive intro members slideshow data')

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

    if not ldap_is_eval_director(user_name):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    uid = post_data['uid']
    status = post_data['status']

    logger.info("backend", action="submit intro eval for %s status: %s" % (uid, status))
    FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == uid and
        FreshmanEvalData.active).\
        update(
            {
                'freshman_eval_result': status
            })

    from db.database import db_session
    db_session.flush()
    db_session.commit()
    return jsonify({"success": True}), 200

@slideshow_bp.route('/slideshow/spring')
def slideshow_spring_display():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
            request_id=str(uuid.uuid4()))
    log.info('frontend', action='display membership evaluations slideshow')

    user_name = request.headers.get('x-webauth-user')
    if not ldap_is_eval_director(user_name):
        return redirect("/dashboard")

    return render_template(request,
                           'spring_eval_slideshow.html',
                           username = user_name,
                           date = datetime.utcnow().strftime("%Y-%m-%d"),
                           members = display_spring_evals(internal=True))

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

    if not ldap_is_eval_director(user_name):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    uid = post_data['uid']
    status = post_data['status']
    #points = post_data['points']
    logger.info("backend", action="submit spring eval for %s status: %s" % (uid, status))

    SpringEval.query.filter(
        SpringEval.uid == uid and
        SpringEval.active).\
        update(
            {
                'status': status
            })

    # points are handeled automagically through constitutional override
    #HousingEvalsSubmission.query.filter(
    #    HousingEvalsSubmission.uid == uid and
    #    HousingEvalsSubmission.active).\
    #    update(
    #        {
    #            'points': points
    #        })

    #current_points = ldap_get_housing_points(uid)
    #ldap_set_housingpoints(uid, current_points + points)

    from db.database import db_session
    db_session.flush()
    db_session.commit()
    return jsonify({"success": True}), 200
