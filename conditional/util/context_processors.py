# pylint: disable=bare-except

import hashlib
import urllib

from conditional import app
from conditional.models.models import FreshmanAccount
from conditional.util.cache import service_cache
from conditional.util.ldap import ldap_get_member, ldap_is_current_student


def get_member_name(uid):
    try:
        return get_csh_name(uid)
    except:
        return get_freshman_name(uid)


@service_cache(maxsize=256)
def get_csh_name(username):
    member = ldap_get_member(username)
    return member.cn


@service_cache(maxsize=256)
def get_freshman_name(uid):
    freshman = FreshmanAccount.query.filter_by(id=uid).first()
    return freshman.name


@service_cache(maxsize=256)
def check_current_student(username):
    member = ldap_get_member(username)
    return ldap_is_current_student(member)


@service_cache(maxsize=256)
def get_rit_image(username: str) -> str:
    if username:
        addresses = [username + "@rit.edu", username + "@g.rit.edu"]
        for addr in addresses:
            url = (
                "https://gravatar.com/avatar/"
                + hashlib.md5(addr.encode("utf8")).hexdigest()
                + ".jpg?d=404&s=250"
            )
            try:
                with urllib.request.urlopen(url) as gravatar:
                    if gravatar.getcode() == 200:
                        return url
            except:
                continue
    return "https://www.gravatar.com/avatar/freshmen?d=mp&f=y"


@app.context_processor
def utility_processor():
    return {
        "get_csh_name": get_csh_name,
        "get_freshman_name": get_freshman_name,
        "get_rit_image": get_rit_image,
        "get_member_name": get_member_name,
        "check_current_student": check_current_student,
    }
