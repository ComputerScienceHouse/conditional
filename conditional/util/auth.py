from functools import wraps

from flask import session

from conditional.util.ldap import ldap_get_member, ldap_is_current_student

def get_user(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        username = str(session["userinfo"].get("preferred_username", ""))
        account = ldap_get_member(username)
        current_student = ldap_is_current_student(account)

        user_dict = {
            'username': username,
            'account': account,
            'student': current_student
        }

        kwargs["user_dict"] = user_dict
        return func(*args, **kwargs)

    return wrapped_function
