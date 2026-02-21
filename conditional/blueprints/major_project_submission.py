import json
import os
import requests

import requests
import boto3

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

major_project_bp = Blueprint("major_project_bp", __name__)


@major_project_bp.route("/major_project/")
@auth.oidc_auth("default")
@get_user
def display_major_project(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info("Display Major Project Page")

    major_projects = [
        {
            "username": p.uid,
            "name": ldap_get_member(p.uid).cn,
            "proj_name": p.name,
            "status": p.status,
            "description": p.description,
            "id": p.id,
            "is_owner": bool(user_dict["username"] == p.uid),
        }
        for p in MajorProject.query.filter(
            MajorProject.date > start_of_year()
        ).order_by(desc(MajorProject.id))
    ]

    major_projects_len = len(major_projects)
    # return names in 'first last (username)' format
    return render_template(
        "major_project_submission.html",
        major_projects=major_projects,
        major_projects_len=major_projects_len,
        username=user_dict["username"])

@major_project_bp.route("/major_project/upload", methods=["POST"])
@auth.oidc_auth("default")
@get_user
def upload_major_project_files(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Uploading Major Project File(s)')

    if len(list(request.files.keys())) <1:
        return "No file", 400
    
    # Temporarily save files to a place, to be uploaded on submit

    for _, file in request.files.lists():
        file = file[0]
        safe_name = secure_filename(file.filename)
        filename = f"/tmp/{user_dict['username']}/{safe_name}"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        file.save(filename)
    
    return jsonify({"success": True}), 200



@major_project_bp.route("/major_project/submit", methods=["POST"])
@auth.oidc_auth("default")
@get_user
def submit_major_project(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info("Submit Major Project")

    post_data = request.get_json()

    print(post_data) # TODO: Remove this later

    name = post_data["projectName"]
    tldr = post_data['projectTldr']
    time_spent = post_data['projectTimeSpent']
    skills = post_data['projectSkills']
    description = post_data["projectDescription"]

    user_id = user_dict['username']

    print(f"Skills: {skills}")

    # All fields are required in order to be able to submit the form
    # TODO: Do we want any of the fields to have enforced min or max lengths?
    if name == "" or tldr == "" or time_spent == "" or skills == "" or description == "":
        return jsonify({"success": False}), 400
    
    # TODO: Ensure all the information is being passed to the object
    project = MajorProject(user_id, name, tldr, time_spent, description)

    # Save the info to the database
    db.session.add(project)
    db.session.commit()

    project = MajorProject.query.filter(
        MajorProject.name == name and MajorProject.uid == user_id
    ).first()

    # Fail if attempting to retreive non-existent project
    if project is None:
        return jsonify({"success": False}), 500
    
    # Sanitize input so that the Slackbot cannot ping @channel
    name = name.replace("<!", "<! ")

    # Send the slack ping only after we know that the data was properly saved to the DB
    # TODO: Maybe add more info to the slack ping?
    send_slack_ping(
        {
            "text": f"<!subteam^S5XENJJAH> *{get_member_name(user_id)}* ({user_id})"
            f" submitted their major project, *{name}*!"
        }
    )

    # Connect to S3 bucket
    s3 = boto3.resource("s3", endpoint_url="https://s3.csh.rit.edu")
    bucket = s3.create_bucket(Bucket="major-project-media")

    # Collect all the locally cached files and put them in the bucket
    for file in os.listdir(f"/tmp/{user_id}"):
        filepath = f"/tmp/{user_id}/{file}"

        # TODO: Remove this later
        print(f"Filepath in S3: {filepath}")

        bucket.upload_file(filepath, f"{project.id}--{file}")
        os.remove(filepath)
        
    # Delete the temp directory once all the files have been stored in S3
    os.rmdir(f"/tmp/{user_id}")

    return jsonify({"success": True}), 200


@major_project_bp.route("/major_project/review", methods=["POST"])
@auth.oidc_auth("default")
@get_user
def major_project_review(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not ldap_is_eval_director(user_dict["account"]):
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    pid = post_data["id"]
    status = post_data["status"]

    log.info(f"{status} Major Project ID: {pid}")

    print(post_data)
    MajorProject.query.filter(MajorProject.id == pid).update({"status": status})
    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@major_project_bp.route("/major_project/delete/<pid>", methods=["DELETE"])
@auth.oidc_auth("default")
@get_user
def major_project_delete(pid, user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info(f"Delete Major Project ID: {pid}")

    major_project = MajorProject.query.filter(MajorProject.id == pid).first()
    creator = major_project.uid

    if creator == user_dict["username"] or ldap_is_eval_director(user_dict["account"]):
        MajorProject.query.filter(MajorProject.id == pid).delete()
        db.session.flush()
        db.session.commit()
        return jsonify({"success": True}), 200

    return "Must be project owner to delete!", 401


def send_slack_ping(payload):
    requests.post(app.config["WEBHOOK_URL"], json.dumps(payload), timeout=120)
