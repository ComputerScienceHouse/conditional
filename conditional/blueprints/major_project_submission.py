import structlog

from flask import Blueprint, request, jsonify, redirect

from sqlalchemy import desc

from conditional.models.models import MajorProject

from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_get_member
from conditional.util.flask import render_template

from conditional import db, start_of_year, get_username, auth

logger = structlog.get_logger()

major_project_bp = Blueprint('major_project_bp', __name__)


@major_project_bp.route('/major_project/')
@auth.oidc_auth
@get_username
def display_major_project(username=None):
    log = logger.new(request=request)
    log.info('Display Major Project Page')

    major_projects = [
        {
            'username': p.uid,
            'name': ldap_get_member(p.uid).cn,
            'proj_name': p.name,
            'status': p.status,
            'description': p.description,
            'id': p.id,
            'is_owner': bool(username == p.uid)
        } for p in
        MajorProject.query.filter(
            MajorProject.date > start_of_year()).order_by(
                desc(MajorProject.id))]

    major_projects_len = len(major_projects)
    # return names in 'first last (username)' format
    return render_template('major_project_submission.html',
                           major_projects=major_projects,
                           major_projects_len=major_projects_len,
                           username=username)


@major_project_bp.route('/major_project/submit', methods=['POST'])
@auth.oidc_auth
@get_username
def submit_major_project(username=None):
    log = logger.new(request=request)
    log.info('Submit Major Project')

    post_data = request.get_json()
    name = post_data['projectName']
    description = post_data['projectDescription']

    if name == "" or description == "":
        return jsonify({"success": False}), 400
    project = MajorProject(username, name, description)

    db.session.add(project)
    db.session.commit()
    return jsonify({"success": True}), 200


@major_project_bp.route('/major_project/review', methods=['POST'])
@auth.oidc_auth
@get_username
def major_project_review(username=None):
    log = logger.new(request=request)

    account = ldap_get_member(username)

    if not ldap_is_eval_director(account):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    pid = post_data['id']
    status = post_data['status']

    log.info('{} Major Project ID: {}'.format(status, pid))

    print(post_data)
    MajorProject.query.filter(
        MajorProject.id == pid). \
        update(
        {
            'status': status
        })
    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@major_project_bp.route('/major_project/delete/<pid>', methods=['DELETE'])
@auth.oidc_auth
@get_username
def major_project_delete(pid, username=None):
    log = logger.new(request=request)
    log.info('Delete Major Project ID: {}'.format(pid))

    account = ldap_get_member(username)

    major_project = MajorProject.query.filter(
        MajorProject.id == pid
    ).first()
    creator = major_project.uid

    if creator == username or ldap_is_eval_director(account):
        MajorProject.query.filter(
            MajorProject.id == pid
        ).delete()
        db.session.flush()
        db.session.commit()
        return jsonify({"success": True}), 200

    return "Must be project owner to delete!", 401
