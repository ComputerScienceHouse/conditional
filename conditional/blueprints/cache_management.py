import os
import signal

import structlog
from flask import Blueprint, request, redirect

from conditional import auth
from conditional.util.auth import get_user
from conditional.util.cache import clear_all_cached_functions
from conditional.util.ldap import _ldap_is_member_of_directorship
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_get_intro_members
from conditional.util.ldap import ldap_get_member
from conditional.util.ldap import ldap_get_onfloor_members
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_is_rtp

logger = structlog.get_logger()
cache_bp = Blueprint('cache_bp', __name__)


@cache_bp.route('/restart')
@auth.oidc_auth("default")
@get_user
def restart_app(user_dict=None):
    if not ldap_is_rtp(user_dict['account']):
        return redirect("/dashboard")

    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Restart Conditional')
    os.kill(os.getpid(), signal.SIGINT)
    return "application restarted", 200


@cache_bp.route('/clearcache')
@auth.oidc_auth("default")
@get_user
def clear_cache(user_dict=None):
    if not ldap_is_eval_director(user_dict['account']) and not ldap_is_rtp(user_dict['account']):
        return redirect("/dashboard")

    log = logger.new(request=request, auth_dict=user_dict)
    log.info('Purge All Caches')

    clear_all_cached_functions()

    return "cache cleared", 200


def clear_members_cache():
    ldap_get_member.cache_clear()
    ldap_get_active_members.cache_clear()
    ldap_get_current_students.cache_clear()
    ldap_get_intro_members.cache_clear()
    ldap_get_onfloor_members.cache_clear()


def clear_committee_cache():
    _ldap_is_member_of_directorship.clear_cache()
