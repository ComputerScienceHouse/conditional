from conditional import ldap
from conditional.util.cache import service_cache

from csh_ldap import CSHGroup, CSHMember


def _ldap_get_group_members(group: str) -> list[CSHMember]:
    return ldap.get_group(group).get_members()


def _ldap_is_member_of_group(member: CSHMember, group: str) -> bool:
    return ldap.get_group(group).check_member(member)


def _ldap_add_member_to_group(account: CSHMember, group: str):
    if not _ldap_is_member_of_group(account, group):
        ldap.get_group(group).add_member(account, dn=False)


def _ldap_remove_member_from_group(account: CSHMember, group: str):
    if _ldap_is_member_of_group(account, group):
        ldap.get_group(group).del_member(account, dn=False)


@service_cache(maxsize=256)
def _ldap_is_member_of_directorship(account: CSHMember, directorship: str):
    return account.in_group(f'eboard-{directorship}', dn=True)
# TODO: try in_group(ldap.get_group(f'eboard-{directorship}')) and profile

@service_cache(maxsize=1024)
def ldap_get_member(username: str) -> CSHMember:
    return ldap.get_member(username, uid=True)

@service_cache(maxsize=1024)
def ldap_get_active_members() -> list[CSHMember]:
    return _ldap_get_group_members("active")


@service_cache(maxsize=1024)
def ldap_get_intro_members() -> list[CSHMember]:
    return _ldap_get_group_members("intromembers")


@service_cache(maxsize=1024)
def ldap_get_onfloor_members() -> list[CSHMember]:
    return _ldap_get_group_members("onfloor")


@service_cache(maxsize=1024)
def ldap_get_current_students() -> list[CSHMember]:
    return _ldap_get_group_members("current_student")


@service_cache(maxsize=128)
def ldap_get_roomnumber(account) -> str:
    try:
        return account.roomNumber
    except AttributeError:
        return ""


@service_cache(maxsize=128)
def ldap_is_active(account) -> bool:
    return _ldap_is_member_of_group(account, 'active')


@service_cache(maxsize=128)
def ldap_is_bad_standing(account) -> bool:
    return _ldap_is_member_of_group(account, 'bad_standing')


@service_cache(maxsize=128)
def ldap_is_alumni(account) -> bool:
    # If the user is not active, they are an alumni.
    return not _ldap_is_member_of_group(account, 'active')


@service_cache(maxsize=128)
def ldap_is_eboard(account) -> bool:
    return _ldap_is_member_of_group(account, 'eboard')


@service_cache(maxsize=128)
def ldap_is_rtp(account) -> bool:
    return _ldap_is_member_of_group(account, 'rtp')


@service_cache(maxsize=128)
def ldap_is_intromember(account) -> bool:
    return _ldap_is_member_of_group(account, 'intromembers')


@service_cache(maxsize=128)
def ldap_is_onfloor(account) -> bool:
    return _ldap_is_member_of_group(account, 'onfloor')


@service_cache(maxsize=128)
def ldap_is_financial_director(account) -> bool:
    return _ldap_is_member_of_directorship(account, 'Financial')


@service_cache(maxsize=128)
def ldap_is_eval_director(account) -> bool:
    return _ldap_is_member_of_directorship(account, 'Evaluations')


@service_cache(maxsize=256)
def ldap_is_current_student(account) -> bool:
    return _ldap_is_member_of_group(account, 'current_student')


def ldap_set_housingpoints(account, housing_points) -> bool:
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
    _ldap_add_member_to_group(account, 'active')
    ldap_get_active_members.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_inactive(account):
    _ldap_remove_member_from_group(account, 'active')
    ldap_get_active_members.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_intro_member(account):
    _ldap_add_member_to_group(account, 'intromembers')
    ldap_get_intro_members().cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_not_intro_member(account):
    _ldap_remove_member_from_group(account, 'intromembers')
    ldap_get_intro_members().cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_current_student(account):
    _ldap_add_member_to_group(account, 'current_student')
    ldap_get_current_students.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_non_current_student(account):
    _ldap_remove_member_from_group(account, 'current_student')
    ldap_get_current_students.cache_clear()
    ldap_get_member.cache_clear()


def ldap_set_failed(account):
    _ldap_add_member_to_group(account, 'failed')
    ldap_get_member.cache_clear()


def ldap_set_bad_standing(account):
    _ldap_add_member_to_group(account, 'bad_standing')
    ldap_get_member.cache_clear()


def ldap_set_onfloor(account):
    _ldap_add_member_to_group(account, 'onfloor')
    ldap_get_onfloor_members.cache_clear()
    ldap_get_member.cache_clear()
