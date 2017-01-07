from datetime import datetime

from conditional.util.ldap import ldap_get_current_students
from conditional.util.ldap import ldap_is_onfloor

from conditional.models.models import InHousingQueue
from conditional.models.models import OnFloorStatusAssigned

def get_housing_queue(is_eval_director=False):

    # Generate a dictionary of dictionaries where the UID is the key
    # and {'time': <datetime obj>} is the value. We are doing a left
    # outer join on the two tables to get a single result that has
    # both the member's UID and their on-floor datetime.
    in_queue = {entry.uid: {'time': entry.onfloor_granted} for entry
    in InHousingQueue.query.outerjoin(OnFloorStatusAssigned,
    OnFloorStatusAssigned.uid == InHousingQueue.uid)\
    .with_entities(InHousingQueue.uid, OnFloorStatusAssigned.onfloor_granted)\
    .all()}

    # Populate a list of dictionaries containing the name, username,
    # and on-floor datetime for each member who has on-floor status,
    # is not already assigned to a room and is in the above query.
    queue = [{"uid": account.uid,
              "name": account.cn,
              "points": account.housingPoints,
              "time": in_queue.get(account.uid, {}).get('time', datetime.now()) or datetime.now(),
              "in_queue": account.uid in in_queue}
             for account in ldap_get_current_students()
             if ldap_is_onfloor(account) and (is_eval_director or account.uid in in_queue)
             and account.roomNumber is None]

    # Sort based on time (ascending) and then points (decending).
    queue.sort(key=lambda m: m['time'])
    queue.sort(key=lambda m: m['points'], reverse=True)

    return queue


def get_queue_position(username):

    queue = get_housing_queue()
    try:
        index = next(index for (index, d) in enumerate(get_housing_queue())
             if d["uid"] == username) + 1
    except (KeyError, StopIteration):
        index = None
    return (index, len(queue))
