from flask import Blueprint
from flask import render_template
from flask import request

from db.models import FreshmanAccount
from db.models import EvalSettings

member_management_bp = Blueprint('member_management_bp', __name__)

@member_management_bp.route('/manage')
def display_member_management():
    return ""

@member_management_bp.route('/manage/eval', methods=['POST'])
def member_management_eval():
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()
    housing_form_active = post_data['housing']
    intro_form_active = post_data['intro']
    site_lockdown = post_data['lockdown']

    EvalSettings.query.all().first().update(
        {
            'housing_form_active': housing_form_active,
            'intro_form_active': intro_form_active,
            'site_lockdown': site_lockdown
        })

    return ""

@member_management_bp.route('/manage/adduser', methods=['POST'])
def member_management_adduser():
    from db.database import db_session

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    name = post_data['name']

    db_session.add(FreshmanAccount(name))
    db_session.flush()
    db_session.commit()
    return ""
