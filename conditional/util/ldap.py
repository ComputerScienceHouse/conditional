from functools import wraps

import ldap

# Global state is gross. I'm sorry.
ldap_conn = None
user_search_ou = None
group_search_ou = None
read_only = False

class HousingLDAPError(Exception):
    pass

def ldap_init(ro, ldap_url, bind_dn, bind_pw, user_ou, group_ou):
    global user_search_ou, group_search_ou, ldap_conn, read_only
    read_only = ro
    user_search_ou = user_ou
    group_search_ou = group_ou
    ldap_conn = ldap.initialize(ldap_url, bytes_mode=False)
    ldap_conn.simple_bind_s(bind_dn, bind_pw)

def ldap_init_required(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        if ldap_conn is not None:
            return func(*args, **kwargs)
        raise HousingLDAPError("LDAP uninitialized. Did you forget to call ldap_init?")
    return wrapped_func

@ldap_init_required
def __ldap_get_field__(username, field):
    ldap_results = ldap_conn.search_s(user_search_ou, ldap.SCOPE_SUBTREE, "(uid=%s)"
            % username)
    if len(ldap_results) != 1:
        raise HousingLDAPError("Wrong number of results found for username %s."
                % username)
    if not field in ldap_results[0][1]:
        return None
    return ldap_results[0][1][field][0]

@ldap_init_required
def __ldap_set_field__(username, field, new_val):
    if read_only:
        print('LDAP modification: setting %s on %s to %s' % (field,
                                                             username,
                                                             new_val))
        return
    ldap_results = ldap_conn.search_s(user_search_ou, ldap.SCOPE_SUBTREE,
            "(uid=%s)" % username)
    if len(ldap_results) != 1:
        raise HousingLDAPError("Wrong number of results found for username %s."
                % username)
    ldap_new_val = ldap_results
    ldap_new_val[0][1][field] = str(new_val).encode('ascii')
    ldapModlist = ldap.modlist.modifyModlist(ldap_results, ldap_new_val)
    userdn = "uid=%s,ou=Users,dc=csh,dc=rit,dc=edu" % username
    ldap_conn.modify_s(userdn, ldapModlist)

@ldap_init_required
def __ldap_get_members__():
    return ldap_conn.search_s(user_search_ou, ldap.SCOPE_SUBTREE,
            "objectClass=houseMember")

@ldap_init_required
def __ldap_is_member_of_group__(username, group):
    ldap_results = ldap_conn.search_s(group_search_ou, ldap.SCOPE_SUBTREE,
            "(cn=%s)" % group)
    if len(ldap_results) != 1:
        raise HousingLDAPError("Wrong number of results found for group %s." %
                group)
    return "uid=" + username + ",ou=Users,dc=csh,dc=rit,dc=edu" in \
        [x.decode('ascii') for x in ldap_results[0][1]['member']]

def ldap_get_housing_points(username):
    return int(__ldap_get_field__(username, 'housingPoints'))

def ldap_get_room_number(username):
    roomno = __ldap_get_field__(username, 'roomNumber')
    if roomno is None:
        return "N/A"
    return roomno.decode('utf-8')

def ldap_get_all_members():
    return __ldap_get_members__()

def ldap_get_active_members():
    return [str(str(x[0]).split(",")[0]).split("=")[1] \
            for x in __ldap_get_members__()[1:] \
            if ldap_is_active(str(str(x[0]).split(",")[0]).split("=")[1])]

def ldap_is_active(username):
    # When active members become a group rather than an attribute this will
    # change to use __ldap_is_member_of_group__.
    return __ldap_get_field__(username, 'active').decode('utf-8') == '1'

def ldap_is_alumni(username):
    # When alumni status becomes a group rather than an attribute this will
    # change to use __ldap_is_member_of_group__.
    return __ldap_get_field__(username, 'alumni').decode('utf-8') == '1'

def ldap_is_eboard(username):
    return __ldap_is_member_of_group__(username, 'eboard')

def ldap_is_intromember(username):
    return __ldap_is_member_of_group__(username, 'intromembers')

def ldap_is_onfloor(username):
    return __ldap_get_field__(username, 'onfloor').decode('utf-8') == '1'

def ldap_set_housingpoints(username, housing_points):
    __ldap_set_field__(username, 'housingPoints', housing_points)

def ldap_set_roomnumber(username, room_number):
    __ldap_set_field__(username, 'roomNumber', room_number)

def ldap_set_active(username, is_active):
    __ldap_set_field__(username, 'active', str(int(is_active)).encode('ascii'))
