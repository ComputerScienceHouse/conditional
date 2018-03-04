import structlog
from flask import Blueprint, request, jsonify

from conditional import db, start_of_year, auth
from conditional.models.models import CurrentCoops
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_is_eval_director

co_op_bp = Blueprint('co_op_bp', __name__)

logger = structlog.get_logger()


@co_op_bp.route('/co_op/')
@auth.oidc_auth
@get_user
def display_co_op_form(user_dict=None):
    log = logger.new(request=request)
    log.info('Display Co-Op Submission Page')

    co_op = CurrentCoops.query.filter(
        CurrentCoops.uid == user_dict['username'], CurrentCoops.date_created > start_of_year()).first()

    return render_template('co_op.html',
                           username=user_dict['username'],
                           year=start_of_year().year,
                           on_coop=co_op)


@co_op_bp.route('/co_op/submit', methods=['POST'])
@auth.oidc_auth
@get_user
def submit_co_op_form(user_dict=None):
    log = logger.new(request=request)

    post_data = request.get_json()
    semester = post_data['semester']

    log.info('Submit {} Co-Op'.format(semester))

    if CurrentCoops.query.filter(CurrentCoops.uid == user_dict['username'],
                                 CurrentCoops.date_created > start_of_year()).first():
        return "User has already submitted this form!", 403

    co_op = CurrentCoops(uid=user_dict['username'], semester=semester)
    db.session.add(co_op)
    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200


@co_op_bp.route('/co_op/<uid>', methods=['DELETE'])
@auth.oidc_auth
@get_user
def delete_co_op(uid, user_dict=None):
    log = logger.new(request=request)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    log.info('Delete {}\'s Co-Op'.format(uid))

    CurrentCoops.query.filter(CurrentCoops.uid == uid, CurrentCoops.date_created > start_of_year()).delete()

    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200
