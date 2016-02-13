from flask import Blueprint
from flask import render_template
from flask import request

intro_evals_form_bp = Blueprint('intro_evals_form_bp', __name__)

@intro_evals_form_bp.route('/intro_evals_form/')
def display_intro_evals_form():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    # return names in 'first last (username)' format
    return render_template('intro_evals_form.html',
                           username = user_name)
