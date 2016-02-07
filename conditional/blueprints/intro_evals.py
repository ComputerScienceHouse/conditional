from flask import Blueprint
from flask import render_template
from flask import request

intro_evals_bp = Blueprint('intro_evals_bp', __name__)

@intro_evals_bp.route('/intro_evals')
@intro_evals_bp.route('/intro_evals/')
def display_intro_evals():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    # return names in 'first last (username)' format
    return render_template('intro_evals.html',
                           username = user_name)

