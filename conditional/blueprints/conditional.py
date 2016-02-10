from flask import Blueprint
from flask import render_template
from flask import request

conditionals_bp = Blueprint('conditionals_bp', __name__)

@conditionals_bp.route('/conditionals')
@conditionals_bp.route('/conditionals/')
def display_conditionals():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    members = [
                {
                    'name': "Liam Middlebrook",
                    'description': '2 - fiveeeee',
                    'deadline': "4-16-15"
                }
            ]
    # return names in 'first last (username)' format
    return render_template('conditional.html',
                            username = user_name,
                            members = members,
                            conditionals_len = len(members))
