import os
from raven import fetch_git_sha

# Flask config
DEBUG = True
ROOT_DIR = os.path.dirname(__file__)
HOST_NAME = 'localhost'
APP_NAME = 'conditional'
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
