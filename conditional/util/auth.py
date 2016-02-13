from functools import wraps
from flask import request
from conditional.util.ldap import ldap_is_active, ldap_is_alumni, \
                                  ldap_is_eboard

def webauth_request(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        user_name = request.headers.get('x-webauth-user')
        is_active = ldap_is_active(user_name)
        is_alumni = ldap_is_alumni(user_name)
        is_eboard = ldap_is_eboard(user_name)

        return func({"user_name" : user_name,
                     "is_active" : is_active,
                     "is_alumni" : is_alumni,
                     "is_eboard" : is_eboard}, *args, **kwargs)
    return wrapped_func
