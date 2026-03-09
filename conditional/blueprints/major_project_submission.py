import json
import os
import botocore
import requests
import boto3

from conditional.models.models import MajorProject, MajorProjectSkill
from conditional.util.user_dict import user_dict_is_eval_director
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import redirect

from sqlalchemy import func, desc

import structlog
from werkzeug.utils import secure_filename

from conditional.util.context_processors import get_member_name

from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_get_member
from conditional.util.flask import render_template

from conditional import db, start_of_year, get_user, auth, app

import collections
collections.Callable = collections.abc.Callable

logger = structlog.get_logger()

major_project_bp = Blueprint("major_project_bp", __name__)

def list_files_in_folder(bucket_name, folder_prefix):

    s3 = boto3.client( 
        service_name="s3",
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'], 
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
        endpoint_url=app.config['S3_URI']
    )
     
    try:
        response = s3.list_objects(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        else:
            return []
        
    except botocore.exceptions.ClientError as e:
        print(f"Error listing files in the folder: {e}")
        return []

@major_project_bp.route("/major_project/")
@auth.oidc_auth("default")
@get_user
def display_major_project(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info("Display Major Project Page")

    # There is probably a better way to do this, but it does work

    proj_list = db.session.query(
        MajorProject.id,
        MajorProject.date,
        MajorProject.uid,
        MajorProject.name,
        MajorProject.tldr,
        MajorProject.timeSpent,
        MajorProject.description,
        MajorProject.links,
        MajorProject.status,
        func.array_agg(MajorProjectSkill.skill).label("skills")
    ).outerjoin(MajorProjectSkill,
        MajorProject.id == MajorProjectSkill.project_id
    ).group_by(MajorProject.id
    ).where(MajorProject.date >= start_of_year()
    ).order_by(desc(MajorProject.date), desc(MajorProject.id))

    s3 = boto3.client( 
            service_name="s3",
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'], 
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
            endpoint_url=app.config['S3_URI']
        )

    major_projects = [
        {
            "id": p.id,
            "date": p.date,
            "username": p.uid,
            "name": ldap_get_member(p.uid).cn,
            "proj_name": p.name,
            "tldr": p.tldr,
            "time_spent": p.timeSpent,
            "skills": p.skills,
            "desc": p.description,
            "links": list(filter(None, p.links.split("\n"))),
            "status": p.status,
            "is_owner": bool(user_dict["username"] == p.uid),
            "files": list_files_in_folder("major-project-media", f"{p.id}/")
        }
        for p in proj_list
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

    # log.info(f"user_dict: {user_dict}")

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

    print(f"Post Data: {post_data}") # TODO: Remove this later

    name = post_data["projectName"]
    tldr = post_data['projectTldr']
    time_spent = post_data['projectTimeSpent']
    skills = post_data['projectSkills']
    description = post_data["projectDescription"]
    links = post_data['projectLinks']

    user_id = user_dict['username']

    log.info(user_id)

    # All fields are required in order to be able to submit the form
    # TODO: Do we want any of the fields to have enforced min or max lengths?
    if not name or not tldr or not time_spent or not description:
        return jsonify({"success": False}), 400
    
    # TODO: Ensure all the information is being passed to the object
    project = MajorProject(user_id, name, tldr, time_spent, description, links)

    # Save the info to the database
    db.session.add(project)
    db.session.commit()


    # project_id = project.id
    project = MajorProject.query.filter(
        MajorProject.name == name,
        MajorProject.uid == user_id
    ).first()
    
    skills_list = list(filter(lambda x: x != 'None', skills))
    print(f"Skills: {list(skills_list)}")

    for skill in skills_list:
        skill = skill.strip()
        
        if skill != "" and skill != 'None':
            mp_skill = MajorProjectSkill(project.id, skill)
            db.session.add(mp_skill)

    db.session.commit()
    
    # Fail if attempting to retreive non-existent project
    if project is None:
        return jsonify({"success": False}), 500
    
    # Sanitize input so that the Slackbot cannot ping @channel
    name = name.replace("<!", "<! ")

    # Connect to S3 bucket
    s3 = boto3.client("s3", 
                        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
                        endpoint_url=app.config['S3_URI'])
    
    # Collect all the locally cached files and put them in the bucket
    temp_dir = f"/tmp/{user_id}"
    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            filepath = f"{temp_dir}/{file}"

            s3.upload_file(filepath, 'major-project-media', f"{project.id}/{file}")
            
            os.remove(filepath)
        
        # Delete the temp directory once all the files have been stored in S3
        os.rmdir(temp_dir)


    # Send the slack ping only after we know that the data was properly saved to the DB
    # TODO: Maybe add more info to the slack ping?
    # send_slack_ping(
    #     {
    #         "text": f"<!subteam^S5XENJJAH> *{get_member_name(user_id)}* ({user_id})"
    #         f" submitted their major project, *{name}*!"
    #     }
    # )

    return jsonify({"success": True}), 200


@major_project_bp.route("/major_project/review", methods=["POST"])
@auth.oidc_auth("default")
@get_user
def major_project_review(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)

    if not user_dict_is_eval_director(user_dict["account"]):
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

    if creator == user_dict["username"] or user_dict_is_eval_director(user_dict["account"]):
        MajorProject.query.filter(MajorProject.id == pid).delete()
        
        db.session.flush()
        db.session.commit()
        
        return jsonify({"success": True}), 200

    return "Must be project owner to delete!", 401


def send_slack_ping(payload):
    requests.post(app.config["WEBHOOK_URL"], json.dumps(payload), timeout=120)