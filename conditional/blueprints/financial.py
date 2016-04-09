from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import jsonify
from util.ldap import ldap_get_room_number, ldap_get_name, ldap_get_current_students, ldap_is_financial_director, ldap_set_active, ldap_is_active

financial_bp = Blueprint('financial_bp', __name__)

@financial_bp.route('/financial')
def display_financial():
    # get user data
    import db.models as models

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_financial_director(user_name) and user_name != 'loothelion':
        return redirect("/dashboard", code=302)

    members = [
        {
            'uid': m[0].decode('utf-8'),
            'name': ldap_get_name(m[0].decode('utf-8')),
            'onfloor': ldap_get_room_number(m[0].decode('utf-8')) != "N/A",
            'paid': "checked" if ldap_is_active(m[0].decode('utf-8')) else ""
        } for m in ldap_get_current_students()]

    # return names in 'first last (username)' format
    return render_template('financial.html',
                           username = user_name,
                           members=members)

@financial_bp.route('/financial/edit', methods=['POST'])
def edit_financial():
    # get user data
    import db.models as models

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_financial_director(user_name) and user_name != 'loothelion':
        return redirect("/dashboard", code=302)

    uid = request.form.get('uid')
    active = request.form.get('active') == "on"

    # LDAP SET VALUE
    ldap_set_active(uid, active)

    return redirect("/financial", code=302)
