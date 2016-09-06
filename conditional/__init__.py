from flask import Flask
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import structlog

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
logger = structlog.get_logger()

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

from conditional.util.ldap import ldap_get_housing_points
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_intro_members
from conditional.util.ldap import ldap_get_non_alumni_members
from conditional.util.ldap import ldap_get_onfloor_members
from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_get_name

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

logger.info('conditional started')


@app.route('/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


@app.route('/')
def default_route():
    return redirect('/dashboard')

@app.route('/clearcache')
def clear_cache():
    ldap_get_housing_points.cache_clear()
    ldap_get_active_members.cache_clear()
    ldap_get_intro_members.cache_clear()
    ldap_get_non_alumni_members.cache_clear()
    ldap_get_onfloor_members.cache_clear()
    ldap_get_current_students.cache_clear()
    ldap_get_name.cache_clear()

@app.cli.command()
def zoo():
    from conditional.models.migrate import free_the_zoo
    free_the_zoo(app.config['ZOO_DATABASE_URI'])
