from flask import Blueprint
from flask import render_template
from flask import request

conditionals_bp = Blueprint('conditionals_bp', __name__)

from util.ldap import ldap_get_name, ldap_is_eval_director

from datetime import datetime

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

@conditionals_bp.route('/conditionals/create', methods=['POST'])
def create_conditional():
    import db.models as models
    from db.database import db_session

    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return "must be eval director", 403

    post_data = request.get_json()

    uid = post_data['uid']
    description = post_data['description']
    due_date = datetime.strptime(post_data['due_date'], "%A %d. %B %Y")

    db_session.add(models.Conditional(uid, description, due_date))
    db_session.flush()
    db_session.commit()

    return 'ok', 200
