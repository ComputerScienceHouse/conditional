import os
from conditional import app
from conditional.util.ldap import ldap_init

app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
app.templates_folder = os.path.join(os.getcwd(), "conditional/templates")
app.config['SERVER_NAME'] = "{}:{}".format(app.config['IP'], app.config['PORT'])

ldap_init(app.config['LDAP_RO'],
          app.config['LDAP_URL'],
          app.config['LDAP_BIND_DN'],
          app.config['LDAP_BIND_PW'],
          app.config['LDAP_USER_OU'],
          app.config['LDAP_GROUP_OU'],
          app.config['LDAP_COMMITTEE_OU'])

if __name__ == "__main__":
    app.run()
