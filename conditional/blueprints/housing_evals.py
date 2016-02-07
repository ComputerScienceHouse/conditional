from flask import Blueprint
from flask import render_template
from flask import request

housing_evals_bp = Blueprint('housing_evals_bp', __name__)

@housing_evals_bp.route('/housing_evals')
@housing_evals_bp.route('/housing_evals/')
def display_housing_evals():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    # return names in 'first last (username)' format
    return render_template('housing_evals.html',
                           username = user_name)
