from datetime import date

from flask import render_template as flask_render_template
from conditional.models.models import EvalSettings
from conditional.util.auth import get_username

from conditional.util.ldap import ldap_is_active
from conditional.util.ldap import ldap_is_alumni
from conditional.util.ldap import ldap_is_eboard
from conditional.util.ldap import ldap_is_financial_director
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.ldap import ldap_is_intromember
from conditional.util.ldap import ldap_is_rtp
from conditional.util.ldap import ldap_get_member

from conditional.models.models import CommitteeMeeting
from conditional.models.models import TechnicalSeminar

from conditional import db


@get_username
def render_template(template_name, username=None, **kwargs):

    if EvalSettings.query.first() is None:
        db.session.add(EvalSettings())
        db.session.flush()
        db.session.commit()
    account = ldap_get_member(username)
    lockdown = EvalSettings.query.first().site_lockdown
    accepting_dues = EvalSettings.query.first().accept_dues_until > date.today()
    is_active = ldap_is_active(account)
    is_alumni = ldap_is_alumni(account)
    is_eboard = ldap_is_eboard(account)
    is_financial = ldap_is_financial_director(account)
    is_eval = ldap_is_eval_director(account)
    is_intromember = ldap_is_intromember(account)
    is_rtp = ldap_is_rtp(account)

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
