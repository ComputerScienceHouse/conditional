import os
from datetime import datetime

import structlog
from csh_ldap import CSHLDAP
from flask import Flask, redirect, render_template, g
from flask_migrate import Migrate
from flask_gzip import Gzip
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_sqlalchemy import SQLAlchemy

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

app = Flask(__name__)
gzip = Gzip(app)

# Load default configuration and any environment variable overrides
_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
app.config.from_pyfile(os.path.join(_root_dir, "config.env.py"))

# Load file based configuration overrides if present
_pyfile_config = os.path.join(_root_dir, "config.py")
if os.path.exists(_pyfile_config):
    app.config.from_pyfile(_pyfile_config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Sentry setup
sentry_sdk.init(
    dsn=app.config["SENTRY_DSN"],
    integrations=[FlaskIntegration(), SqlalchemyIntegration()],
    environment=app.config["SENTRY_ENV"],
)

ldap = CSHLDAP(
    app.config["LDAP_BIND_DN"], app.config["LDAP_BIND_PW"], ro=app.config["LDAP_RO"]
)

client_metadata = ClientMetadata(app.config["OIDC_CLIENT_CONFIG"])
provider_config = ProviderConfiguration(
    issuer=app.config["OIDC_ISSUER"], client_registration_info=client_metadata
)
frosh_provider_config = ProviderConfiguration(
    issuer=app.config["FROSH_OIDC_ISSUER"], client_registration_info=client_metadata
)

auth = OIDCAuthentication(
    {"default": provider_config, "frosh": frosh_provider_config}, app
)

app.secret_key = app.config["SECRET_KEY"]


def start_of_year():
    start = datetime(datetime.today().year, 6, 1)
    if datetime.today() < start:
        start = datetime(datetime.today().year - 1, 6, 1)
    return start


# pylint: disable=C0413
from .models.models import UserLog


# Configure Logging
def request_processor(
    logger, log_method, event_dict
):  # pylint: disable=unused-argument, redefined-outer-name
    if "request" in event_dict:
        flask_request = event_dict["request"]
        event_dict["ip"] = flask_request.remote_addr
        event_dict["method"] = flask_request.method
        event_dict["blueprint"] = flask_request.blueprint
        event_dict["path"] = flask_request.full_path
    if "auth_dict" in event_dict:
        auth_dict = event_dict["auth_dict"]
        event_dict["user"] = auth_dict["username"]
    return event_dict


def database_processor(
    logger, log_method, event_dict
):  # pylint: disable=unused-argument, redefined-outer-name
    if "request" in event_dict:
        if event_dict["method"] != "GET":
            log = UserLog(
                ipaddr=event_dict["ip"],
                user=event_dict["user"],
                method=event_dict["method"],
                blueprint=event_dict["blueprint"],
                path=event_dict["path"],
                description=event_dict["event"],
            )
            db.session.add(log)
            db.session.flush()
            db.session.commit()
        del event_dict["request"]
    return event_dict


structlog.configure(
    processors=[
        request_processor,
        database_processor,
        structlog.processors.KeyValueRenderer(),
    ]
)

logger = structlog.get_logger()

# pylint: disable=wrong-import-order
from conditional.util import context_processors
from conditional.util.auth import get_user
from .blueprints.dashboard import dashboard_bp  # pylint: disable=ungrouped-imports
from .blueprints.attendance import attendance_bp
from .blueprints.major_project_submission import major_project_bp
from .blueprints.intro_evals import intro_evals_bp
from .blueprints.intro_evals_form import intro_evals_form_bp
from .blueprints.housing import housing_bp
from .blueprints.spring_evals import spring_evals_bp
from .blueprints.conditional import conditionals_bp
from .blueprints.member_management import member_management_bp
from .blueprints.slideshow import slideshow_bp
from .blueprints.cache_management import cache_bp
from .blueprints.co_op import co_op_bp
from .blueprints.logs import log_bp
from .blueprints.packet import packet_bp

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
app.register_blueprint(log_bp)
app.register_blueprint(packet_bp)

from .util.ldap import ldap_get_member


@app.route("/<path:path>")
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


@app.route("/")
@auth.oidc_auth("default")
def default_route():
    return redirect("/dashboard")


@app.route("/logout")
@auth.oidc_logout
def logout():
    return redirect("/", 302)


@app.route("/health")
def health():
    """
    Shows an ok status if the application is up and running
    """
    return {"status": "ok"}


@app.errorhandler(404)
@app.errorhandler(500)
@auth.oidc_auth("default")
@get_user
def route_errors(error, user_dict=None):
    data = {}

    # Handle the case where the header isn't present
    if user_dict["username"] is not None:
        data["username"] = user_dict["account"].uid
        data["name"] = user_dict["account"].cn
    else:
        data["username"] = "unknown"
        data["name"] = "Unknown"

    # Figure out what kind of error was passed
    if isinstance(error, int):
        code = error
    elif hasattr(error, "code"):
        code = error.code
    else:
        # Unhandled exception
        code = 500

    # Is this a 404?
    if code == 404:
        error_desc = "Page Not Found"
    else:
        error_desc = type(error).__name__

    return render_template(
        "errors.html",
        error=error_desc,
        error_code=code,
        event_id=sentry_sdk.last_event_id(),
        **data
    ), int(code)


logger.info("conditional started")
