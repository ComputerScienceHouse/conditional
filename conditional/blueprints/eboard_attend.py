from flask import Blueprint
from flask import render_template
from flask import request

eboard_attend_bp = Blueprint('eboard_attend_bp', __name__)

@eboard_attend_bp.route('/attendance/')
def display_eboard_attend():
    # get user data

    user_name = request.headers.get('x-webauth-user')
    print("access")
    # return names in 'first last (username)' format
    return render_template('eboard_attend.html',
                           username = user_name)
