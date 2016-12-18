import os

# Flask config
DEBUG = True
HOST_NAME = 'localhost'
APP_NAME = 'conditional'
IP = '0.0.0.0'
PORT = 6969

# LDAP config
LDAP_RO = True
LDAP_BIND_DN = 'cn=conditional,ou=Apps,dc=csh,dc=rit,dc=edu'
LDAP_BIND_PW = ''

# Database config
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(os.getcwd(), "data.db"))
ZOO_DATABASE_URI = 'mysql+pymysql://user:pass@host/database'
