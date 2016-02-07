from flask import Blueprint
from flask import render_template
from flask import request

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/dashboard/')
def display_dashboard():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    return render_template('dashboard.html',
                           username = user_name)
