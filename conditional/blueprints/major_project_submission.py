import json
import os

import requests
import boto3
from botocore.exceptions import ClientError

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import redirect

from sqlalchemy import desc

import structlog
from werkzeug.utils import secure_filename

from conditional.util.context_processors import get_member_name

from conditional.models.models import MajorProject

from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_get_member
from conditional.util.flask import render_template

from conditional import db, start_of_year, get_user, auth, app

logger = structlog.get_logger()

major_project_bp = Blueprint('major_project_bp', __name__)


@major_project_bp.route('/major_project/')
@auth.oidc_auth
@get_user
def display_major_project(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Major Project Page')

    major_projects = [
        {
            'username': p.uid,
            'name': ldap_get_member(p.uid).cn,
            'proj_name': p.name,
            'status': p.status,
            'description': p.description,
            'id': p.id,
            'is_owner': bool(user_dict['username'] == p.uid)
        } for p in
        MajorProject.query.filter(
            MajorProject.date > start_of_year()).order_by(
                desc(MajorProject.id))]

    major_projects_len = len(major_projects)
    # return names in 'first last (username)' format
    return render_template('major_project_submission.html',
                           major_projects=major_projects,
                           major_projects_len=major_projects_len,
                           username=user_dict['username'])

@major_project_bp.route('/major_project/upload', methods=['POST'])
@auth.oidc_auth
@get_user
def upload_major_project_files(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Uploading Major Project File(s)')

    print(request.files)
    if len(list(request.files.keys())) < 1:
        return "No file", 400

    # Temporarily save files to a place, to be uploaded on submit

    for _, file in request.files.lists():
        file = file[0] # remove it from the list because this is not the best
        safe_name = secure_filename(file.filename)
        filename = f"/tmp/{user_dict['username']}/{safe_name}"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        file.save(filename)


@major_project_bp.route('/major_project/submit', methods=['POST'])
@auth.oidc_auth
@get_user
def submit_major_project(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Submit Major Project')

    post_data = request.get_json()
    name = post_data['projectName']
    description = post_data['projectDescription']

    if name == "" or len(description.strip().split()) < 50:
        return jsonify({"success": False}), 400
    project = MajorProject(user_dict['username'], name, description)

    # Acquire S3 Bucket instance
    s3 = boto3.resource("s3")
    bucket = s3.create_bucket(Bucket="major-project-media")
    # Collect all the locally cached files and put them in the bucket
    for file in os.listdir(f"/tmp/{user_dict['username']}"):
        bucket.upload_file(file, file.split("/")[-1])
        os.remove(file)
    os.rmdir(f"/tmp/{user_dict['username']}")

    username = user_dict['username']
    send_slack_ping({"text":f"<!subteam^S5XENJJAH> *{get_member_name(username)}* ({username})"
                            f" submitted their major project, *{name}*!"})
    db.session.add(project)
    db.session.commit()
    return jsonify({"success": True}), 200


@major_project_bp.route('/major_project/review', methods=['POST'])
@auth.oidc_auth
@get_user
def major_project_review(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict['account']):
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
@get_user
def major_project_delete(pid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Delete Major Project ID: {}'.format(pid))

    major_project = MajorProject.query.filter(
        MajorProject.id == pid
    ).first()
    creator = major_project.uid

    if creator == user_dict['username'] or ldap_is_eval_director(user_dict['account']):
        MajorProject.query.filter(
            MajorProject.id == pid
        ).delete()
        db.session.flush()
        db.session.commit()
        return jsonify({"success": True}), 200

    return "Must be project owner to delete!", 401

def send_slack_ping(payload):
    requests.post(app.config['WEBHOOK_URL'], json.dumps(payload))
