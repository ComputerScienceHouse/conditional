import structlog
from flask import Blueprint, request, jsonify

from conditional import db, start_of_year, auth
from conditional.models.models import CurrentCoops
from conditional.util.member import req_cm
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_is_eval_director, ldap_is_current_student
from conditional.util.ldap import _ldap_add_member_to_group as ldap_add_member_to_group
from conditional.util.ldap import _ldap_remove_member_from_group as ldap_remove_member_from_group
from conditional.util.ldap import _ldap_is_member_of_group as ldap_is_member_of_group

co_op_bp = Blueprint('co_op_bp', __name__)

logger = structlog.get_logger()


@co_op_bp.route('/co_op/')
@auth.oidc_auth
@get_user
def display_co_op_form(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Co-Op Submission Page')

    co_op = CurrentCoops.query.filter(
        CurrentCoops.uid == user_dict['uid'], CurrentCoops.date_created > start_of_year()).first()

    return render_template('co_op.html',
                           username=user_dict['uid'],
                           year=start_of_year().year,
                           on_coop=co_op)


@co_op_bp.route('/co_op/submit', methods=['POST'])
@auth.oidc_auth
@get_user
def submit_co_op_form(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    valid_semesters = ['Fall', 'Spring']
    post_data = request.get_json()
    semester = post_data['semester']
    if post_data['semester'] not in valid_semesters:
        return "Invalid semester submitted", 400
    if not ldap_is_current_student(user_dict['account']):
        return "Must be current student", 403

    log.info('Submit {} Co-Op'.format(semester))

    if CurrentCoops.query.filter(CurrentCoops.uid == user_dict['uid'],
                                 CurrentCoops.date_created > start_of_year()).first():
        return "User has already submitted this form!", 403

    # Add to corresponding co-op ldap group
    ldap_add_member_to_group(user_dict['account'], semester.lower() + '_coop')

    co_op = CurrentCoops(uid=user_dict['uid'], semester=semester)
    db.session.add(co_op)
    db.session.flush()
    db.session.commit()
    req_cm.cache_clear()

    return jsonify({"success": True}), 200


@co_op_bp.route('/co_op/<uid>', methods=['DELETE'])
@auth.oidc_auth
@get_user
def delete_co_op(uid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    log.info('Delete {}\'s Co-Op'.format(uid))

    # Remove from corresponding co-op ldap group
    if ldap_is_member_of_group(user_dict['account'], 'fall_coop'):
        ldap_remove_member_from_group(user_dict['account'], 'fall_coop')
    if ldap_is_member_of_group(user_dict['account'], 'spring_coop'):
        ldap_remove_member_from_group(user_dict['account'], 'spring_coop')

    CurrentCoops.query.filter(CurrentCoops.uid == uid, CurrentCoops.date_created > start_of_year()).delete()

    db.session.flush()
    db.session.commit()
    req_cm.cache_clear()

    return jsonify({"success": True}), 200


@co_op_bp.route('/co_op/manage')
@auth.oidc_auth
@get_user
def display_co_op_management(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Co-Op Management')

    if not ldap_is_eval_director(user_dict['account']):
        return "must be eval director", 403

    co_op_list = [(member.semester, member.uid)
                  for member in CurrentCoops.query.filter(
            CurrentCoops.date_created > start_of_year(),
            CurrentCoops.semester != "Neither")]

    return render_template("co_op_management.html",
                           username=user_dict['uid'],
                           co_op=co_op_list,
                           )
