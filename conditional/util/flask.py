from flask import render_template as flask_render_template
from conditional.models.models import EvalSettings

from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_alumni
from conditional.util.ldap import ldap_is_eboard
from conditional.util.ldap import ldap_is_financial_director
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_is_intromember


def render_template(request, template_name, **kwargs):
    user_name = request.headers.get('x-webauth-user')

    # TODO maybe use the webauth request decorator
    lockdown_query = EvalSettings.query.first()
    if lockdown_query:
        lockdown = lockdown_query.site_lockdown
    else:
        lockdown = False
    is_active = ldap_is_active(user_name)
    is_alumni = ldap_is_alumni(user_name)
    is_eboard = ldap_is_eboard(user_name)
    is_financial = ldap_is_financial_director(user_name)
    is_eval = ldap_is_eval_director(user_name)
    is_intromember = ldap_is_intromember(user_name)

    if is_eval:
        lockdown = False

    return flask_render_template(
        template_name,
        lockdown=lockdown,
        is_active=is_active,
        is_alumni=is_alumni,
        is_eboard=is_eboard,
        is_eval_director=is_eval,
        is_financial_director=is_financial,
        is_intromember=is_intromember,
        **kwargs)
