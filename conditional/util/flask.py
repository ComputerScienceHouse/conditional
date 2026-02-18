from datetime import date

from flask import render_template as flask_render_template
from conditional.models.models import EvalSettings
from conditional.util.auth import get_user

from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_alumni
from conditional.util.ldap import ldap_is_eboard
from conditional.util.ldap import ldap_is_financial_director
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_is_intromember
from conditional.util.ldap import ldap_is_rtp

from conditional.models.models import CommitteeMeeting
from conditional.models.models import TechnicalSeminar

from conditional import db
from conditional.util.user_dict import user_dict_is_active, user_dict_is_alumni, user_dict_is_eboard, user_dict_is_eval_director, user_dict_is_financial_director, user_dict_is_intromember, user_dict_is_rtp


@get_user
def render_template(template_name, user_dict=None, **kwargs):

    if EvalSettings.query.first() is None:
        db.session.add(EvalSettings())
        db.session.flush()
        db.session.commit()
    lockdown = EvalSettings.query.first().site_lockdown
    accepting_dues = EvalSettings.query.first().accept_dues_until > date.today()
    is_active = user_dict_is_active(user_dict)
    is_alumni = user_dict_is_alumni(user_dict)
    is_eboard = user_dict_is_eboard(user_dict)
    is_financial = user_dict_is_financial_director(user_dict)
    is_eval = user_dict_is_eval_director(user_dict)
    is_intromember = user_dict_is_intromember(user_dict)
    is_rtp = user_dict_is_rtp(user_dict)

    cm_review = len(CommitteeMeeting.query.filter(
        CommitteeMeeting.approved == False).all()) # pylint: disable=singleton-comparison
    ts_review = len(TechnicalSeminar.query.filter(
        TechnicalSeminar.approved == False).all()) # pylint: disable=singleton-comparison

    admin_warning = lockdown

    if is_eboard or is_rtp:
        lockdown = False

    return flask_render_template(
        template_name,
        lockdown=lockdown,
        admin_warning=admin_warning,
        accepting_dues=accepting_dues,
        is_active=is_active,
        is_alumni=is_alumni,
        is_eboard=is_eboard,
        is_eval_director=is_eval,
        is_financial_director=is_financial,
        is_intromember=is_intromember,
        is_rtp=is_rtp,
        pending_review=(cm_review + ts_review),
        **kwargs)
