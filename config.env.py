import json
import secrets
import os
from os import environ as env

# Fetch the version number from the npm package file
with open(os.path.join(os.getcwd(), "package.json")) as package_file:
    VERSION = json.load(package_file)["version"]

# Flask config
DEBUG = env.get("CONDITIONAL_DEBUG", "false").lower() == "true"
HOST_NAME = env.get("CONDITIONAL_HOST_NAME", "conditional.csh.rit.edu")
SERVER_NAME = env.get('CONDITIONAL_SERVER_NAME', 'conditional.csh.rit.edu')
APP_NAME = "conditional"
IP = env.get("CONDITIONAL_IP", "0.0.0.0")
PORT = env.get("CONDITIONAL_PORT", 6969)
WEBHOOK_URL = env.get("CONDITIONAL_WEBHOOK_URL", "INSERT URL HERE")

# DB Info
SQLALCHEMY_DATABASE_URI = env.get("SQLALCHEMY_DATABASE_URI", "")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# LDAP config
LDAP_RO = env.get("CONDITIONAL_LDAP_RO", "true").lower() == "true"
LDAP_BIND_DN = env.get("CONDITIONAL_LDAP_BIND_DN", "cn=conditional,ou=Apps,dc=csh,dc=rit,dc=edu")
LDAP_BIND_PW = env.get("CONDITIONAL_LDAP_BIND_PW", "")

# Sentry config
# Not required for local development, but if you set it, make sure the
# SENTRY_ENV is 'local-development'
SENTRY_DSN = env.get("CONDITIONAL_SENTRY_DSN", "")
SENTRY_CONFIG = {
    'dsn': env.get("CONDITIONAL_SENTRY_LEGACY_DSN", ""),
    'release': VERSION,
}
SENTRY_ENV = env.get("CONDITIONAL_SENTRY_ENV", "local-development")

# OIDC Config
OIDC_ISSUER = env.get("CONDITIONAL_OIDC_ISSUER", "https://sso.csh.rit.edu/auth/realms/csh")
OIDC_CLIENT_CONFIG = {
    'client_id': env.get("CONDITIONAL_OIDC_CLIENT_ID", "conditional"),
    'client_secret': env.get("CONDITIONAL_OIDC_CLIENT_SECRET", ""),
    'post_logout_redirect_uris': [env.get("CONDITIONAL_OIDC_CLIENT_LOGOUT", "http://0.0.0.0:6969/logout")]
}

# Openshift secret
SECRET_KEY = env.get("CONDITIONAL_SECRET_KEY", default=''.join(secrets.token_hex(16)))

# General config
DUES_PER_SEMESTER = env.get("CONDITIONAL_DUES_PER_SEMESTER", 80)

# Email
SEND_EMAIL = env.get("CONDITIONAL_SEND_EMAIL", False) # When false, requests to send emails are ignored
MAIL_SERVER = env.get("CONDITIONAL_MAIL_SERVER", "thoth.csh.rit.edu")
DEBUG_EMAIL = env.get("CONDITIONAL_DEBUG_EMAIL", "") # when set all email is sent to the specified email
EMAIL_PASSWORD = env.get("CONDITIONAL_MAIL_PASSWORD", "")
