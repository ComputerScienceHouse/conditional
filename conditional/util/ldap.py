from functools import wraps
import ldap

# Global state is gross. I'm sorry.
ldap_conn = None
search_ou = None

class HousingLDAPError(Exception):
    pass

def ldap_init(ldap_url, bind_dn, bind_pw, base_ou):
    search_ou = base_ou
    if search_ou == "" or search_ou is None:
        raise HousingLDAPError("No search OU provided. Check your configs.")
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
    ldap_results = ldap_conn.search_s(search_ou, ldap.SCOPE_SUBTREE, "(uid=%s)"
            % username)
    if len(ldap_results) != 1:
        raise HousingLDAPError("Wrong number of results found for username %s.")
    return ldap_results[0][1][field]

def ldap_get_housing_points(username):
    return int(_ldap_get_field('housingPoints'))

def ldap_get_room_number(username):
    return _ldap_get_field('roomNumber')
