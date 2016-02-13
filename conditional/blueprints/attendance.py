from flask import Blueprint
from flask import render_template
from flask import request

attendance_bp = Blueprint('attendance_bp', __name__)

@attendance_bp.route('/attendance/')
def display_attendance():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    # return names in 'first last (username)' format
    return render_template('attendance.html',
                           username = user_name)
