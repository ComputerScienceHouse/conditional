from functools import lru_cache
from util.ldap import ldap_get_housing_points, ldap_get_room_number, ldap_get_name
import db.models as models

@lru_cache(maxsize=1024)
def get_housing_queue():
    ofm = [
        {
            'uid': m.uid,
            'time': m.onfloor_granted,
            'points': ldap_get_housing_points(m.uid)
        } for m in models.OnFloorStatusAssigned.query.all()]

    # sort by housing points then by time in queue
    ofm.sort(key = lambda m: m['time'])
    ofm.sort(key = lambda m: m['points'], reverse=True)

    queue = [m['uid'] for m in ofm if ldap_get_room_number(m['uid']) == "N/A"]

    return queue

def get_queue_with_points():
    ofm = [
        {
            'uid': m.uid,
            'time': m.onfloor_granted,
            'points': ldap_get_housing_points(m.uid)
        } for m in models.OnFloorStatusAssigned.query.all()]

    # sort by housing points then by time in queue
    ofm.sort(key = lambda m: m['time'])
    ofm.sort(key = lambda m: m['points'], reverse=True)

    queue = [
        {
            'name': ldap_get_name(m['uid']),
            'points': m['points']
        } for m in ofm if ldap_get_room_number(m['uid']) == "N/A"]

    return queue

def get_queue_length():
    return len(get_housing_queue())

def get_queue_position(username):
    return get_housing_queue().index(username)
