from flask import Blueprint
from flask import render_template
from flask import request

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/dashboard/')
def display_dashboard():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    data = {}
    data['username'] = user_name

    # number of committee meetings attended
    data['committee_meetings'] = 11

    # technical seminar total
    data['ts_total'] = 2

    #
    return render_template('dashboard.html', **data)
