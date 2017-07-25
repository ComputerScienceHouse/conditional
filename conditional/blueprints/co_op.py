import structlog

from flask import Blueprint, request, jsonify

from conditional.util.flask import render_template

from conditional.util.ldap import ldap_get_member, ldap_is_eval_director

from conditional.models.models import CurrentCoops

from conditional import db, start_of_year

co_op_bp = Blueprint('co_op_bp', __name__)

logger = structlog.get_logger()

@co_op_bp.route('/co_op/')
def display_co_op_form():
    log = logger.new(request=request)
    log.info('Display Co-Op Submission Page')

    # get user data
    user_name = request.headers.get('x-webauth-user')
    co_op = CurrentCoops.query.filter(
        CurrentCoops.uid == user_name, CurrentCoops.date_created > start_of_year()).first()

    return render_template(request,
                           'co_op.html',
                           username=user_name,
                           year=start_of_year().year,
                           on_coop=co_op)


@co_op_bp.route('/co_op/submit', methods=['POST'])
def submit_co_op_form():
    log = logger.new(request=request)

    user_name = request.headers.get('x-webauth-user')

    post_data = request.get_json()
    semester = post_data['semester']

    log.info('Submit {} Co-Op'.format(semester))

    if CurrentCoops.query.filter(CurrentCoops.uid == user_name, CurrentCoops.date_created > start_of_year()).first():
        return "User has already submitted this form!", 403

    co_op = CurrentCoops(uid=user_name, semester=semester)
    db.session.add(co_op)
    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200


@co_op_bp.route('/co_op/<uid>', methods=['DELETE'])
def delete_co_op(uid):
    log = logger.new(request=request)

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return "must be eval director", 403

    log.info('Delete {}\'s Co-Op'.format(uid))

    CurrentCoops.query.filter(CurrentCoops.uid == uid, CurrentCoops.date_created > start_of_year()).delete()

    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200
