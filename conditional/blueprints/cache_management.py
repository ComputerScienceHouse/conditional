import os
import signal
import structlog

from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_is_rtp

from conditional.util.ldap import _ldap_is_member_of_directorship
from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_intro_members
from conditional.util.ldap import ldap_get_onfloor_members
from conditional.util.ldap import ldap_get_current_students

from conditional.util.member import get_voting_members
from conditional.util.member import get_members_info
from conditional.util.member import get_onfloor_members


from flask import Blueprint, request, redirect

logger = structlog.get_logger()
cache_bp = Blueprint('cache_bp', __name__)


@cache_bp.route('/restart')
def restart_app():
    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)
    if not ldap_is_rtp(account):
        return redirect("/dashboard")

    logger.info('api', action='restart conditional')
    os.kill(os.getpid(), signal.SIGINT)
    return "application restarted", 200


@cache_bp.route('/clearcache')
def clear_cache():
    user_name = request.headers.get('x-webauth-user')
    account = ldap_get_member(user_name)

    if not ldap_is_eval_director(account) or not ldap_is_rtp(account):
        return redirect("/dashboard")

    logger.info('api', action='purge system cache')

    _ldap_is_member_of_directorship.cache_clear()
    ldap_get_member.cache_clear()
    ldap_get_active_members.cache_clear()
    ldap_get_intro_members.cache_clear()
    ldap_get_onfloor_members.cache_clear()
    ldap_get_current_students.cache_clear()

    get_voting_members.cache_clear()
    get_members_info.cache_clear()
    get_onfloor_members.cache_clear()
    return "cache cleared", 200


def clear_members_cache():
    ldap_get_member.cache_clear()
    ldap_get_active_members.cache_clear()
    ldap_get_current_students.cache_clear()
    ldap_get_intro_members.cache_clear()
    ldap_get_onfloor_members.cache_clear()


def clear_committee_cache():
    _ldap_is_member_of_directorship.clear_cache()
