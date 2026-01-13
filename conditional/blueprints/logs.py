import structlog
from flask import Blueprint, request

from conditional import auth
from conditional.models.models import UserLog
from conditional.util.auth import get_user
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_is_eboard
from conditional.util.ldap import ldap_is_rtp

logger = structlog.get_logger()

log_bp = Blueprint('log_bp', __name__)


@log_bp.route('/logs')
@auth.oidc_auth("default")
@get_user
def display_logs(user_dict=None):
    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Display Logs')

    log.info(user_dict['account'].displayName)

    if not ldap_is_eboard(user_dict['account']) and not ldap_is_rtp(user_dict['account']):
        return "must be rtp or eboard", 403

    logs = UserLog.query.all()

    return render_template("logs.html", logs=logs, username=user_dict['username'])
