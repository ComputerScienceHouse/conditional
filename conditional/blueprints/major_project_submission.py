from flask import Blueprint, request, jsonify, redirect
import structlog
import uuid

from conditional.models.models import MajorProject

from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_get_name
from conditional.util.flask import render_template

from conditional import db


logger = structlog.get_logger()

major_project_bp = Blueprint('major_project_bp', __name__)


@major_project_bp.route('/major_project/')
def display_major_project():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display major project form')

    # get user data

    user_name = request.headers.get('x-webauth-user')

    major_projects = [
        {
            'username': p.uid,
            'name': ldap_get_name(p.uid),
            'proj_name': p.name,
            'status': p.status,
            'description': p.description,
            'id': p.id
        } for p in
        MajorProject.query]

    major_projects_len = len(major_projects)
    # return names in 'first last (username)' format
    return render_template(request,
                           'major_project_submission.html',
                           major_projects=major_projects,
                           major_projects_len=major_projects_len,
                           username=user_name)


@major_project_bp.route('/major_project/submit', methods=['POST'])
def submit_major_project():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit major project')

    user_name = request.headers.get('x-webauth-user')

    post_data = request.get_json()
    name = post_data['project_name']
    description = post_data['project_description']

    project = MajorProject(user_name, name, description)

    db.session.add(project)
    db.session.commit()
    return jsonify({"success": True}), 200


@major_project_bp.route('/major_project/review', methods=['POST'])
def major_project_review():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('api', action='review major project')

    # get user data
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    pid = post_data['id']
    status = post_data['status']

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
