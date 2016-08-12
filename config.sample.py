import os

# Flask config
DEBUG = True
HOST_NAME = 'localhost'
APP_NAME = 'conditional'
IP = '0.0.0.0'
PORT = 6969

# LDAP config
LDAP_RO = True
LDAP_URL = 'ldaps://ldap.csh.rit.edu:636/'
LDAP_BIND_DN = 'cn=conditional,ou=Apps,dc=csh,dc=rit,dc=edu'
LDAP_BIND_PW = ''
LDAP_USER_OU = 'ou=Users,dc=csh,dc=rit,dc=edu'
LDAP_GROUP_OU = 'ou=Groups,dc=csh,dc=rit,dc=edu'
LDAP_COMMITTEE_OU = 'ou=Committees,dc=csh,dc=rit,dc=edu'

# Database config
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(os.getcwd(), "data.db"))
ZOO_DATABASE_URI = 'mysql+pymysql://user:pass@host/database'
