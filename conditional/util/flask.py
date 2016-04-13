from flask import render_template as flask_render_template
from db.models import EvalSettings

from util.ldap import ldap_is_active
from util.ldap import ldap_is_alumni
from util.ldap import ldap_is_eboard
from util.ldap import ldap_is_financial_director
from util.ldap import ldap_is_eval_director

def render_template(request, template_name, **kwargs):
    user_name = request.headers.get('x-webauth-user')

    #TODO maybe use the webauth request decorator
    lockdown = EvalSettings.query.first().site_lockdown
    is_active = ldap_is_active(user_name)
    is_alumni = ldap_is_alumni(user_name)
    is_eboard = ldap_is_eboard(user_name)
    is_financial = ldap_is_financial_director(user_name)
    is_eval = ldap_is_eval_director(user_name)

    if is_eval:
        lockdown = False

    return flask_render_template(
        template_name,
        lockdown=lockdown,
        is_eboard=is_eboard,
        is_eval=is_eval,
        is_financial=is_financial,
        **kwargs)
