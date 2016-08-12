from flask import Blueprint, request, jsonify, redirect
from datetime import datetime
import structlog
import uuid

from conditional.util.ldap import ldap_get_name
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.flask import render_template

from conditional.models.models import Conditional

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
            'name': ldap_get_name(c.uid),
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

    if not ldap_is_eval_director(user_name):
        return "must be eval director", 403

    post_data = request.get_json()

    uid = post_data['uid']
    description = post_data['description']
    due_date = datetime.strptime(post_data['due_date'], "%Y-%m-%d")

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

    if not ldap_is_eval_director(user_name):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    cid = post_data['id']
    status = post_data['status']

    logger.info(action="updated conditional-%s to %s" % (cid, status))
    Conditional.query.filter(
        Conditional.id == cid). \
        update(
        {
            'status': status
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200
