import uuid

from datetime import datetime

import structlog

from flask import Blueprint, request, jsonify, redirect

from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.flask import render_template

from conditional.models.models import Conditional, SpringEval, FreshmanEvalData

from conditional import db

conditionals_bp = Blueprint('conditionals_bp', __name__)

logger = structlog.get_logger()


@conditionals_bp.route('/conditionals/')
def display_conditionals():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display conditional listing page')

    # get user data
    user_name = request.headers.get('x-webauth-user')

    conditionals = [
        {
            'name': ldap_get_member(c.uid).cn,
            'date_created': c.date_created,
            'date_due': c.date_due,
            'description': c.description,
            'id': c.id
        } for c in
        Conditional.query.filter(
            Conditional.status == "Pending")]
    # return names in 'first last (username)' format
    return render_template(request,
                           'conditional.html',
                           username=user_name,
                           conditionals=conditionals,
                           conditionals_len=len(conditionals))


@conditionals_bp.route('/conditionals/create', methods=['POST'])
def create_conditional():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='create new conditional')

    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    post_data = request.get_json()

    uid = post_data['uid']
    description = post_data['description']
    due_date = datetime.strptime(post_data['dueDate'], "%Y-%m-%d")
    if post_data['evaluation'] == 'spring':
        current_eval = SpringEval.query.filter(SpringEval.status == "Pending",
            SpringEval.uid == uid,
            SpringEval.active == True).first().id # pylint: disable=singleton-comparison
        db.session.add(Conditional(uid, description, due_date, s_eval=current_eval))
    elif post_data['evaluation'] == 'intro':
        if uid.isdigit():
            current_eval = FreshmanEvalData.query.filter(FreshmanEvalData.freshman_eval_result == "Pending",
                FreshmanEvalData.id == uid).first().id
        else:
            current_eval = FreshmanEvalData.query.filter(FreshmanEvalData.freshman_eval_result == "Pending",
                FreshmanEvalData.uid == uid).first().id
        db.session.add(Conditional(uid, description, due_date, i_eval=current_eval))
    else:
        db.session.add(Conditional(uid, description, due_date))

    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200


@conditionals_bp.route('/conditionals/review', methods=['POST'])
def conditional_review():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='review a conditional')

    # get user data
    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    cid = post_data['id']
    status = post_data['status']

    logger.info(action="updated conditional-%s to %s" % (cid, status))
    conditional = Conditional.query.filter(Conditional.id == cid)
    cond_obj = conditional.first()

    conditional.update(
        {
            'status': status
        })
    if cond_obj.s_evaluation:
        SpringEval.query.filter(SpringEval.id == cond_obj.s_evaluation).update(
            {
                'status': status
            })
    elif cond_obj.i_evaluation:
        FreshmanEvalData.query.filter(FreshmanEvalData.id == cond_obj.i_evaluation).update(
            {
                'freshman_eval_result': status
            })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@conditionals_bp.route('/conditionals/delete/<cid>', methods=['DELETE'])
def conditional_delete(cid):
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='delete conditional')

    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

    if ldap_is_eval_director(account):
        Conditional.query.filter(
            Conditional.id == cid
        ).delete()
        db.session.flush()
        db.session.commit()
        return jsonify({"success": True}), 200

    return "Must be evals director to delete!", 401
