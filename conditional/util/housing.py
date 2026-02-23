from datetime import datetime

from conditional.models.models import InHousingQueue
from conditional.models.models import OnFloorStatusAssigned
from conditional.util.ldap import ldap_get_member, ldap_is_current_student


def get_housing_queue(is_eval_director=False):

    # Generate a dictionary of dictionaries where the UID is the key
    # and {'time': <datetime obj>} is the value. We are doing a left
    # outer join on the two tables to get a single result that has
    # both the member's UID and their on-floor datetime.
    in_queue = {
        entry.uid: {
            'time': entry.onfloor_granted
        } for entry in InHousingQueue.query.outerjoin(
            OnFloorStatusAssigned,
            OnFloorStatusAssigned.uid == InHousingQueue.uid
        ).with_entities(
            InHousingQueue.uid,
            OnFloorStatusAssigned.onfloor_granted
        ).all()
    }

    # CSHMember accounts that are in queue
    potential_accounts = [ldap_get_member(username) for username in in_queue]

    # Populate a list of dictionaries containing the name, username,
    # and on-floor datetime for each current studetn who has on-floor status
    # and is not already assigned to a room
    queue = [
        {
            "uid": account.uid,
            "name": account.cn,
            "points": account.housingPoints,
            "time": in_queue.get(account.uid, {}).get('time', datetime.now()) or datetime.now(),
            "in_queue": account.uid in in_queue
        } for account in potential_accounts
        if ldap_is_current_student(account) and (is_eval_director or account.roomNumber is None)
    ]

    # Sort based on time (ascending) and then points (decending).
    queue.sort(key=lambda m: m['time'])
    queue.sort(key=lambda m: m['points'], reverse=True)

    return queue


def get_queue_position(username):
    queue = get_housing_queue()
    try:
        index = next(index for (index, d) in enumerate(queue) if d["uid"] == username) + 1
    except (KeyError, StopIteration):
        index = None
    return index, len(queue)
