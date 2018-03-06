import os
from raven import fetch_git_sha

# Flask config
DEBUG = True
ROOT_DIR = os.path.dirname(__file__)
HOST_NAME = 'localhost'
APP_NAME = 'conditional'
SERVER_NAME = '0.0.0.0:6969'
IP = '0.0.0.0'
PORT = 6969

# LDAP config
LDAP_RO = True
LDAP_BIND_DN = 'cn=conditional,ou=Apps,dc=csh,dc=rit,dc=edu'
LDAP_BIND_PW = ''

# Sentry config
# Do not set the DSN for local development
SENTRY_CONFIG = {
    'dsn': '',
    'release': fetch_git_sha(ROOT_DIR),
}

# Database config
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(os.getcwd(), "data.db"))
ZOO_DATABASE_URI = 'mysql+pymysql://user:pass@host/database'

# OIDC Config
OIDC_ISSUER = "https://sso.csh.rit.edu/auth/realms/csh"
OIDC_CLIENT_CONFIG = {
    'client_id': '',
    'client_secret': '',
    'post_logout_redirect_uris': ['http://0.0.0.0:6969/logout']
}

SECRET_KEY = ""

# General config
DUES_PER_SEMESTER = 80
