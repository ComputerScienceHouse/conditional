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
    # Member Status
    data['active'] = True
    # On-Floor Status
    data['onfloor'] = True
    # Voting Status
    data['voting'] = False

    freshman = {}

    freshman['status'] = "Pending"
    # number of committee meetings attended
    freshman['committee_meetings'] = 11

    # technical seminar total
    freshman['ts_total'] = 42
    freshman['ts_string'] = "Seminar #1\nSeminar #2"

    freshman['hm_missed'] = 0

    freshman['social_events'] = "Welcome Back, First Marks"

    freshman['general_comments'] = "Please accept me as a member kthnxbai."

    freshman['eval_date'] = "Oct 31, 2015"

    data['freshman'] = freshman

    spring = {}
    spring['mp_status'] = "Failed"
    spring['committee_meetings'] = 26
    spring['hm_missed'] = 26
    spring['general_comments'] = "I should win, please don't kick me out"

    data['spring'] = spring
    housing = {}
    housing['points'] = 2
    housing['room'] = "NRH3103"
    housing['future_room'] = "NRH3102"
    housing['queue_pos'] = 2
    housing['queue_len'] = 9

    data['housing'] = housing

    major_projects = []
    proj = {}
    proj['name'] = "open container"
    proj['status'] = "Passed"
    proj['description'] = "Base project description example."
    major_projects.append(proj)

    data['major_projects'] = major_projects
    data['major_projects_count'] = len(major_projects)

    conditionals = [{'description':'redo freshman project','deadline':'next year'}]
    data['conditionals'] = conditionals
    data['conditionals_len'] = len(conditionals)

    attendance = [{'type':'House Meeting', 'datetime': 'christmass'}]
    data['attendance'] = attendance
    data['attendance_len'] = len(attendance)

    return render_template('dashboard.html', **data)
