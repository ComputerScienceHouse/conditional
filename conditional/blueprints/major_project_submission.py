from flask import Blueprint
from flask import render_template
from flask import request

major_project_bp = Blueprint('major_project_bp', __name__)

@major_project_bp.route('/major_project/')
def display_major_project():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    # return names in 'first last (username)' format
    return render_template('major_project_submission.html',
                           username = user_name)
