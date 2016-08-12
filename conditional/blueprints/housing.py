from flask import Blueprint, request
import structlog
import uuid

from conditional.models.models import FreshmanAccount
from conditional.util.housing import get_queue_with_points
from conditional.util.ldap import ldap_get_onfloor_members
from conditional.util.ldap import ldap_get_room_number
from conditional.util.ldap import ldap_get_name
from conditional.util.flask import render_template


logger = structlog.get_logger()

housing_bp = Blueprint('housing_bp', __name__)


@housing_bp.route('/housing')
def display_housing():
    log = logger.new(user_name=request.headers.get("x-webauth-user"),
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display housing')

    # get user data

    user_name = request.headers.get('x-webauth-user')

    housing = {}
    onfloors = [uids['uid'][0].decode('utf-8') for uids in ldap_get_onfloor_members()]
    onfloor_freshmen = FreshmanAccount.query.filter(
        FreshmanAccount.room_number is not None
    )

    room_list = set()

    for m in onfloors:
        room = ldap_get_room_number(m)
        if room in housing:
            housing[room].append(ldap_get_name(m))
        else:
            housing[room] = [ldap_get_name(m)]
        room_list.add(room)

    for f in onfloor_freshmen:
        name = f.name
        room = str(f.room_number)
        if room in housing:
            housing[room].append(name)
        else:
            housing[room] = [name]
        room_list.add(room)

    # return names in 'first last (username)' format
    return render_template(request,
                           'housing.html',
                           username=user_name,
                           queue=get_queue_with_points(),
                           housing=housing,
                           room_list=sorted(list(room_list)))
