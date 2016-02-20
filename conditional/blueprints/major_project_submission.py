from flask import Blueprint
from flask import render_template
from flask import request

from db.models import MajorProject
major_project_bp = Blueprint('major_project_bp', __name__)

@major_project_bp.route('/major_project/')
def display_major_project():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    major_projects = [
            {
                'username': p.uid,
                'name': p.name,
                'status': p.status,
                'description': p.description
            } for p in
        MajorProject.query.filter(MajorProject.uid == user_name)]

    major_projects_len = len(major_projects)
    # return names in 'first last (username)' format
    return render_template('major_project_submission.html',
                            major_projects = major_projects,
                            major_projects_len = major_projects_len,
                            username = user_name)
