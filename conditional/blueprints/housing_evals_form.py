from flask import Blueprint
from flask import render_template
from flask import request

housing_evals_form_bp = Blueprint('housing_evals_form_bp', __name__)

@housing_evals_form_bp.route('/housing_evals_form')
@housing_evals_form_bp.route('/housing_evals_form/')
def display_housing_evals_form():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    # return names in 'first last (username)' format
    return render_template('housing_evals_form.html',
                           username = user_name)
