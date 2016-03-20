from flask import Blueprint
from flask import render_template
from flask import request

conditionals_bp = Blueprint('conditionals_bp', __name__)

from util.ldap import ldap_get_name

@conditionals_bp.route('/conditionals/')
def display_conditionals():
    # get user data
    import db.models as models
    user_name = request.headers.get('x-webauth-user')

    conditionals = [
            {
                'name': ldap_get_name(c.uid),
                'date_created': c.date_created,
                'date_due': c.date_due,
                'description': c.description
            } for c in
        models.Conditional.query.all()]
    # return names in 'first last (username)' format
    return render_template('conditional.html',
                            username = user_name,
                            conditionals=conditionals,
                            conditionals_len = len(conditionals))
