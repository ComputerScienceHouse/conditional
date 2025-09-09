from functools import wraps

from flask import request, session, redirect

from conditional import auth, app
from conditional.util.ldap import (
    ldap_is_active,
    ldap_is_alumni,
    ldap_is_eboard,
    ldap_is_eval_director,
    ldap_is_financial_director,
    ldap_get_member,
    ldap_is_current_student,
)


def webauth_request(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        user_name = request.headers.get("x-webauth-user")
        account = ldap_get_member(user_name)
        is_active = ldap_is_active(account)
        is_alumni = ldap_is_alumni(account)
        is_eboard = ldap_is_eboard(account)
        is_financial = ldap_is_financial_director(account)
        is_eval = ldap_is_eval_director(account)

        return func(
            {
                "user_name": user_name,
                "is_active": is_active,
                "is_alumni": is_alumni,
                "is_eboard": is_eboard,
                "is_financial": is_financial,
                "is_eval": is_eval,
            },
            *args,
            **kwargs,
        )

    return wrapped_func


def get_user(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        username = str(session["userinfo"].get("preferred_username", ""))
        account = ldap_get_member(username)
        current_student = ldap_is_current_student(account)

        user_dict = {
            "username": username,
            "account": account,
            "student": current_student,
        }

        kwargs["user_dict"] = user_dict
        return func(*args, **kwargs)

    return wrapped_function


def needs_auth(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        match session.get("provider"):
            case "csh":
                csh_auth()
                oidc_info = session["userinfo"]
                username = oidc_info["preferred_username"]
            case "frosh":
                frosh_auth()
                oidc_info = session["userinfo"]
                username = oidc_info["preferred_username"]
            case _:
                return redirect("/packet", code=301)

        username = str(session["userinfo"].get("preferred_username", ""))
        ritdn = str(session["userinfo"].get("ritdn", ""))
        account = ldap_get_member(username)
        current_student = ldap_is_current_student(account)

        user_dict = {
            "username": username,
            "account": account,
            "student": current_student,
            "ritdn": ritdn,
        }

        kwargs["user_dict"] = user_dict
        return func(*args, **kwargs)

    return wrapped_function


@auth.oidc_auth("default")
def csh_auth():
    return


@auth.oidc_auth("frosh")
def frosh_auth():
    return


@app.route("/auth/csh")
@auth.oidc_auth("default")
def csh_login():
    session["provider"] = "csh"
    return redirect("/packet", code=301)


@app.route("/auth/frosh")
@auth.oidc_auth("frosh")
def frosh_login():
    session["provider"] = "frosh"
    return redirect("/packet", code=301)
