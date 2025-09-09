from datetime import date
from typing import Optional

from conditional import ldap
from conditional.util.cache import service_cache


def _ldap_get_group_members(group):
    return ldap.get_group(group).get_members()


def _ldap_is_member_of_group(member, group):
    group_list = member.get("memberOf")
    for group_dn in group_list:
        if group == group_dn.split(",")[0][3:]:
            return True
    return False


def _ldap_add_member_to_group(account, group):
    if not _ldap_is_member_of_group(account, group):
        ldap.get_group(group).add_member(account, dn=False)


def _ldap_remove_member_from_group(account, group):
    if _ldap_is_member_of_group(account, group):
        ldap.get_group(group).del_member(account, dn=False)


@service_cache(maxsize=256)
def _ldap_is_member_of_directorship(account, directorship):
    directors = ldap.get_directorship_heads(directorship)
    for director in directors:
        if director.uid == account.uid:
            return True
    return False


@service_cache(maxsize=1024)
def ldap_get_member(username):
    return ldap.get_member(username, uid=True)


@service_cache(maxsize=1024)
def ldap_get_active_members():
    return _ldap_get_group_members("active")


@service_cache(maxsize=1024)
def ldap_get_intro_members():
    return _ldap_get_group_members("intromembers")


@service_cache(maxsize=1024)
def ldap_get_onfloor_members():
    return _ldap_get_group_members("onfloor")


@service_cache(maxsize=1024)
def ldap_get_current_students():
    return _ldap_get_group_members("current_student")


@service_cache(maxsize=1024)
def ldap_get_rtps():
    return _ldap_get_group_members("active_rtp")


@service_cache(maxsize=1024)
def ldap_get_3das():
    return _ldap_get_group_members("3da")


@service_cache(maxsize=1024)
def ldap_get_webmasters():
    return _ldap_get_group_members("webmaster")


@service_cache(maxsize=1024)
def ldap_get_cms():
    return _ldap_get_group_members("constitutional_maintainers")


@service_cache(maxsize=1024)
def ldap_get_wms():
    return _ldap_get_group_members("wiki_maintainers")


@service_cache(maxsize=1024)
def ldap_get_drink_admins():
    return _ldap_get_group_members("drink")


@service_cache(maxsize=1024)
def ldap_is_on_coop(account):
    if date.today().month > 6:
        return _ldap_is_member_of_group(account, "fall_coop")
    return _ldap_is_member_of_group(account, "spring_coop")


@service_cache(maxsize=128)
def ldap_get_roomnumber(account):
    try:
        return account.roomNumber
    except AttributeError:
        return ""


@service_cache(maxsize=128)
def ldap_is_active(account):
    return _ldap_is_member_of_group(account, "active")


@service_cache(maxsize=128)
def ldap_is_bad_standing(account):
    return _ldap_is_member_of_group(account, "bad_standing")


@service_cache(maxsize=128)
def ldap_is_alumni(account):
    # If the user is not active, they are an alumni.
    return not _ldap_is_member_of_group(account, "active")


@service_cache(maxsize=128)
def ldap_is_eboard(account):
    return _ldap_is_member_of_group(account, "eboard")


@service_cache(maxsize=128)
def ldap_is_rtp(account):
    return _ldap_is_member_of_group(account, "rtp")


@service_cache(maxsize=128)
def ldap_is_intromember(account):
    return _ldap_is_member_of_group(account, "intromembers")


@service_cache(maxsize=128)
def ldap_is_onfloor(account):
    return _ldap_is_member_of_group(account, "onfloor")


@service_cache(maxsize=128)
def ldap_is_financial_director(account):
    return _ldap_is_member_of_directorship(account, "Financial")


@service_cache(maxsize=128)
def ldap_is_eval_director(account):
    return _ldap_is_member_of_directorship(account, "Evaluations")


@service_cache(maxsize=256)
def ldap_is_current_student(account):
    return _ldap_is_member_of_group(account, "current_student")


def ldap_get_eboard_role(account) -> Optional[str]:
    """
    :param member: A CSHMember instance
    :return: A String or None
    """

    return_val = None

    if _ldap_is_member_of_group(account, "eboard-chairman"):
        return_val = "Chairperson"
    elif _ldap_is_member_of_group(account, "eboard-evaluations"):
        return_val = "Evals"
    elif _ldap_is_member_of_group(account, "eboard-financial"):
        return_val = "Financial"
    elif _ldap_is_member_of_group(account, "eboard-history"):
        return_val = "History"
    elif _ldap_is_member_of_group(account, "eboard-imps"):
        return_val = "Imps"
    elif _ldap_is_member_of_group(account, "eboard-opcomm"):
        return_val = "OpComm"
    elif _ldap_is_member_of_group(account, "eboard-research"):
        return_val = "R&D"
    elif _ldap_is_member_of_group(account, "eboard-social"):
        return_val = "Social"
    elif _ldap_is_member_of_group(account, "eboard-pr"):
        return_val = "PR"
    elif _ldap_is_member_of_group(account, "eboard-secretary"):
        return_val = "Secretary"

    return return_val


def ldap_set_housingpoints(account, housing_points):
    account.housingPoints = housing_points
    ldap_get_current_students.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_roomnumber(account, room_number):
    if room_number == "":
        room_number = None
    account.roomNumber = room_number
    ldap_get_current_students.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_active(account):
    _ldap_add_member_to_group(account, "active")
    ldap_get_active_members.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_inactive(account):
    _ldap_remove_member_from_group(account, "active")
    ldap_get_active_members.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_intro_member(account):
    _ldap_add_member_to_group(account, "intromembers")
    ldap_get_intro_members().cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_not_intro_member(account):
    _ldap_remove_member_from_group(account, "intromembers")
    ldap_get_intro_members().cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_current_student(account):
    _ldap_add_member_to_group(account, "current_student")
    ldap_get_current_students.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_non_current_student(account):
    _ldap_remove_member_from_group(account, "current_student")
    ldap_get_current_students.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_failed(account):
    _ldap_add_member_to_group(account, "failed")
    ldap_get_member.cache_clear()


def ldap_set_bad_standing(account):
    _ldap_add_member_to_group(account, "bad_standing")
    ldap_get_member.cache_clear()


def ldap_set_onfloor(account):
    _ldap_add_member_to_group(account, "onfloor")
    ldap_get_onfloor_members.cache_clear()
    ldap_get_member.cache_clear()
