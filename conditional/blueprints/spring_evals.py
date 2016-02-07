from flask import Blueprint
from flask import render_template
from flask import request

spring_evals_bp = Blueprint('spring_evals_bp', __name__)

@spring_evals_bp.route('/spring_evals')
@spring_evals_bp.route('/spring_evals/')
def display_spring_evals():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    # return names in 'first last (username)' format
    return render_template('spring_evals.html',
                           username = user_name)
