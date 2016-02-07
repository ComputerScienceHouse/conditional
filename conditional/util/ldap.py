from functools import wraps
import ldap

# Global state is gross. I'm sorry.
ldap_conn = None
user_search_ou = None
group_search_ou = None

class HousingLDAPError(Exception):
    pass

def ldap_init(ldap_url, bind_dn, bind_pw, user_ou, group_ou):
    user_search_ou = user_ou
    group_search_ou = group_ou
    if user_search_ou == "" or user_search_ou is None:
        raise HousingLDAPError("No user search OU provided.")
    if group_search_ou == "" or group_search_ou is None:
        raise HousingLDAPError("No group search OU provided.")
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
def _ldap_get_field(username, field):
    ldap_results = ldap_conn.search_s(user_search_ou, ldap.SCOPE_SUBTREE, "(uid=%s)"
            % username)
    if len(ldap_results) != 1:
        raise HousingLDAPError("Wrong number of results found for username %s."
                % username)
    return ldap_results[0][1][field]

@ldap_init_required
def _ldap_is_member_of_group(username, group):
    ldap_results = ldap_conn.search_s(group_search_ou, ldap.SCOPE_SUBTREE,
            "(cn=%s)" % group)
    if len(ldap_results) != 1:
        raise HousingLDAPError("Wrong number of results found for group %s." %
                group)
    return "uid=" + username + ",ou=Users,dc=csh,dc=rit,dc=edu" in \
        [x.decode('ascii') for x in ldap_results[0][1]['member']]

def ldap_get_housing_points(username):
    return int(_ldap_get_field('housingPoints'))

def ldap_get_room_number(username):
    return _ldap_get_field('roomNumber')

def ldap_is_eboard(username):
    return _ldap_is_member_of_group(username, 'eboard')
