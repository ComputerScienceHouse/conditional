import os
import signal
import structlog

from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_is_rtp
from conditional.util.ldap import ldap_get_housing_points
from conditional.util.ldap import ldap_get_active_members
from conditional.util.ldap import ldap_get_intro_members
from conditional.util.ldap import ldap_get_non_alumni_members
from conditional.util.ldap import ldap_get_onfloor_members
from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_get_name

from flask import Blueprint, request, redirect

logger = structlog.get_logger()
cache_bp = Blueprint('cache_bp', __name__)

@cache_bp.route('/restart')
def restart_app():
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_rtp(user_name):
        return redirect("/dashboard")

    logger.info('api', action='restart conditional')
    os.kill(os.getpid(), signal.SIGINT)
    return "application restarted", 200


@cache_bp.route('/clearcache')
def clear_cache():
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) or ldap_is_rtp(user_name):
        return redirect("/dashboard")

    logger.info('api', action='purge system cache')

    ldap_get_housing_points.cache_clear()
    ldap_get_active_members.cache_clear()
    ldap_get_intro_members.cache_clear()
    ldap_get_non_alumni_members.cache_clear()
    ldap_get_onfloor_members.cache_clear()
    ldap_get_current_students.cache_clear()
    ldap_get_name.cache_clear()
    return "cache cleared", 200


def clear_housing_points_cache():
    ldap_get_housing_points.cache_clear()


def clear_active_members_cache():
    ldap_get_active_members.cache_clear()


def clear_intro_members_cache():
    ldap_get_intro_members.cache_clear()


def clear_non_alumni_cache():
    ldap_get_non_alumni_members.cache_clear()


def clear_onfloor_members_cache():
    ldap_get_onfloor_members.cache_clear()


def clear_current_students_cache():
    ldap_get_current_students.cache_clear()


def clear_user_cache(username):
    ldap_get_name(username).cache_clear()
