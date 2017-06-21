import os
import subprocess
from datetime import datetime
from flask import Flask, redirect, request, render_template, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from csh_ldap import CSHLDAP
from raven import fetch_git_sha
from raven.contrib.flask import Sentry
from raven.exceptions import InvalidGitRepository
import structlog

app = Flask(__name__)

config = os.path.join(app.config.get('ROOT_DIR', os.getcwd()), "config.py")

app.config.from_pyfile(config)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

try:
    app.config["GIT_REVISION"] = fetch_git_sha(app.config["ROOT_DIR"])[:7]
except (InvalidGitRepository, KeyError):
    app.config["GIT_REVISION"] = "unknown"


db = SQLAlchemy(app)
migrate = Migrate(app, db)
sentry = Sentry(app)

ldap = CSHLDAP(app.config['LDAP_BIND_DN'],
               app.config['LDAP_BIND_PW'],
               ro=app.config['LDAP_RO'])

def start_of_year():
    start = datetime(datetime.today().year, 6, 1)
    if datetime.today() < start:
        start = datetime(datetime.today().year-1, 6, 1)
    return start

# pylint: disable=C0413
from conditional.models.models import UserLog

# Configure Logging
def request_processor(logger, log_method, event_dict): # pylint: disable=unused-argument, redefined-outer-name
    if 'request' in event_dict:
        flask_request = event_dict['request']
        event_dict['user'] = flask_request.headers.get("x-webauth-user")
        event_dict['ip'] = flask_request.remote_addr
        event_dict['method'] = flask_request.method
        event_dict['blueprint'] = flask_request.blueprint
        event_dict['path'] = flask_request.full_path
    return event_dict


def database_processor(logger, log_method, event_dict): # pylint: disable=unused-argument, redefined-outer-name
    if 'request' in event_dict:
        if event_dict['method'] != 'GET':
            log = UserLog(
                ipaddr=event_dict['ip'],
                user=event_dict['user'],
                method=event_dict['method'],
                blueprint=event_dict['blueprint'],
                path=event_dict['path'],
                description=event_dict['event']
                )
            db.session.add(log)
            db.session.flush()
            db.session.commit()
        del event_dict['request']
    return event_dict

structlog.configure(processors=[
    request_processor,
    database_processor,
    structlog.processors.KeyValueRenderer()
    ])

logger = structlog.get_logger()


from conditional.blueprints.dashboard import dashboard_bp # pylint: disable=ungrouped-imports
from conditional.blueprints.attendance import attendance_bp
from conditional.blueprints.major_project_submission import major_project_bp
from conditional.blueprints.intro_evals import intro_evals_bp
from conditional.blueprints.intro_evals_form import intro_evals_form_bp
from conditional.blueprints.housing import housing_bp
from conditional.blueprints.spring_evals import spring_evals_bp
from conditional.blueprints.conditional import conditionals_bp
from conditional.blueprints.member_management import member_management_bp
from conditional.blueprints.slideshow import slideshow_bp
from conditional.blueprints.cache_management import cache_bp
from conditional.blueprints.co_op import co_op_bp

app.register_blueprint(dashboard_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(major_project_bp)
app.register_blueprint(intro_evals_bp)
app.register_blueprint(intro_evals_form_bp)
app.register_blueprint(housing_bp)
app.register_blueprint(spring_evals_bp)
app.register_blueprint(conditionals_bp)
app.register_blueprint(member_management_bp)
app.register_blueprint(slideshow_bp)
app.register_blueprint(cache_bp)
app.register_blueprint(co_op_bp)

from conditional.util.ldap import ldap_get_member

@app.route('/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


@app.route('/')
def default_route():
    return redirect('/dashboard')

@app.errorhandler(404)
@app.errorhandler(500)
def route_errors(error):
    data = dict()
    username = request.headers.get('x-webauth-user')

    # Handle the case where the header isn't present
    if username is not None:
        member = ldap_get_member(username)
        data['username'] = member.uid
        data['name'] = member.cn
    else:
        data['username'] = "unknown"
        data['name'] = "Unknown"

    # Figure out what kind of error was passed
    if isinstance(error, int):
        code = error
    elif hasattr(error, 'code'):
        code = error.code
    else:
        # Unhandled exception
        code = 500

    # Is this a 404?
    if code == 404:
        error_desc = "Page Not Found"
    else:
        error_desc = type(error).__name__

    return render_template('errors.html',
                            error=error_desc,
                            error_code=code,
                            event_id=g.sentry_event_id,
                            public_dsn=sentry.client.get_public_dsn('https'),
                            **data), int(code)

@app.cli.command()
def zoo():
    from conditional.models.migrate import free_the_zoo
    free_the_zoo(app.config['ZOO_DATABASE_URI'])

logger.info('conditional started')
