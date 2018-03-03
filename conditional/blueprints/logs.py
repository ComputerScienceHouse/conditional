import structlog
from flask import Blueprint, request

from conditional import auth
from conditional.models.models import UserLog
from conditional.util.auth import get_username
from conditional.util.flask import render_template
from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_is_eboard
from conditional.util.ldap import ldap_is_rtp

logger = structlog.get_logger()

log_bp = Blueprint('log_bp', __name__)


@log_bp.route('/logs')
@auth.oidc_auth
@get_username
def display_logs(username=None):
    log = logger.new(request=request)
    log.info('Display Logs')

    account = ldap_get_member(username)
    log.info(account.displayName)

    if not ldap_is_eboard(account) and not ldap_is_rtp(account):
        return "must be rtp or eboard", 403

    logs = UserLog.query.all()

    return render_template("logs.html", logs=logs, username=username)
