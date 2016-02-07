from flask import Blueprint
from flask import render_template
from flask import request

spring_evals_form_bp = Blueprint('spring_evals_form_bp', __name__)

@spring_evals_form_bp.route('/spring_evals_form')
@spring_evals_form_bp.route('/spring_evals_form/')
def display_spring_evals_form():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    # return names in 'first last (username)' format
    return render_template('spring_evals_form.html',
                           username = user_name)
