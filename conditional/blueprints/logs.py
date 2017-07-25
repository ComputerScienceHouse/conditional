import structlog

from flask import Blueprint, request

from conditional.models.models import UserLog

from conditional.util.ldap import ldap_is_eboard
from conditional.util.ldap import ldap_is_rtp
from conditional.util.ldap import ldap_get_member

from conditional.util.flask import render_template

logger = structlog.get_logger()

log_bp = Blueprint('log_bp', __name__)

@log_bp.route('/logs')
def display_logs():
    log = logger.new(request=request)
    log.info('Display Logs')

    username = request.headers.get('x-webauth-user')
    account = ldap_get_member(username)
    log.info(account.displayName)

    if not ldap_is_eboard(account) and not ldap_is_rtp(account):
        return "must be rtp or eboard", 403

    logs = UserLog.query.all()

    return render_template(request, "logs.html", logs=logs, username=username)
