from functools import wraps
from flask import request
from util.ldap import ldap_is_active, ldap_is_alumni, \
                                  ldap_is_eboard, ldap_is_eval_director, \
                                  ldap_is_financial_director

def webauth_request(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        user_name = request.headers.get('x-webauth-user')
        is_active = ldap_is_active(user_name)
        is_alumni = ldap_is_alumni(user_name)
        is_eboard = ldap_is_eboard(user_name)
        is_financial = ldap_is_financial_director(user_name)
        is_eval = ldap_is_eval_director(user_name)

        return func({"user_name" : user_name,
                     "is_active" : is_active,
                     "is_alumni" : is_alumni,
                     "is_eboard" : is_eboard,
                     "is_financial" : is_financial,
                     "is_eval" : is_eval}, *args, **kwargs)
    return wrapped_func
