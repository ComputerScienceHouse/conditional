import os
import subprocess
from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from csh_ldap import CSHLDAP
import structlog

app = Flask(__name__)

config = os.path.join(os.getcwd(), "config.py")

app.config.from_pyfile(config)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["GIT_REVISION"] = subprocess.check_output(['git',
                                                      'rev-parse',
                                                      '--short',
                                                      'HEAD']).decode('utf-8').rstrip()
db = SQLAlchemy(app)
migrate = Migrate(app, db)
logger = structlog.get_logger()

ldap = CSHLDAP(app.config['LDAP_BIND_DN'],
               app.config['LDAP_BIND_PW'],
               ro=app.config['LDAP_RO'])

# pylint: disable=C0413

from conditional.blueprints.dashboard import dashboard_bp
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

from conditional.util.flask import render_template
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
    username = request.headers.get('x-webauth-user')
    member = ldap_get_member(username)
    data = dict()
    data['username'] = member.uid
    data['name'] = member.cn
    code = error.code
    return render_template(request=request,
                            template_name='errors.html',
                            error=str(error),
                            error_code=code,
                            **data), int(code)

@app.cli.command()
def zoo():
    from conditional.models.migrate import free_the_zoo
    free_the_zoo(app.config['ZOO_DATABASE_URI'])

logger.info('conditional started')
