from datetime import datetime

from conditional import ldap

from conditional.models.models import InHousingQueue
from conditional.models.models import OnFloorStatusAssigned

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

    queue = ldap.get_group_member_attributes(groups=['current_student'],
                                             excluded_groups=[],
                                             attributes=['uid', 'housingPoints', 'cn', 'roomNumber'])

    # if the user is not evals, they should only see people in the queue without a room number
    if not is_eval_director:
        def member_in_queue(member):
            return (
               member['uid'] in in_queue
               and ('roomNumber' not in member or member['roomNumber'] is not None)
            )
        queue = list(filter(member_in_queue, queue))

    # set the time they were added to the queue
    # i'm sorry this is cursed, it's this way because of database structure or something
    for member in queue:
        member['time'] = in_queue.get(member['uid'], {}).get('time', datetime.now()) or datetime.now()

    # Sort based on time (ascending) and then points (decending).
    queue.sort(key=lambda m: m['time'])
    queue.sort(key=lambda m: m['housingPoints'], reverse=True)

    return queue


def get_queue_position(username):
    queue = get_housing_queue()
    try:
        index = next(index for (index, d) in enumerate(queue) if d["uid"] == username) + 1
    except (KeyError, StopIteration):
        index = None
    return index, len(queue)
