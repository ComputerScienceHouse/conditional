from flask import Blueprint
from flask import render_template
from flask import request
from util.housing import get_queue_with_points
from util.ldap import ldap_get_onfloor_members
from util.ldap import ldap_get_room_number
from util.ldap import ldap_get_name

housing_bp = Blueprint('housing_bp', __name__)

@housing_bp.route('/housing')
def display_housing():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    housing = {}
    onfloors = [uids['uid'][0].decode('utf-8') for uids in ldap_get_onfloor_members()]


    room_list = set()
    for m in onfloors:
        room = ldap_get_room_number(m)
        if room in housing:
            housing[room].append(ldap_get_name(m))
        else:
            housing[room] = [ldap_get_name(m)]
        room_list.add(room)

    # return names in 'first last (username)' format
    return render_template('housing.html',
                           username = user_name,
                           queue=get_queue_with_points(),
                           housing=housing,
                           room_list=list(room_list))
