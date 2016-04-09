from db.migrate import free_the_zoo
import sys
import json
from util.ldap import ldap_init

if __name__ == '__main__':
    json_config = None

    with open(sys.argv[1]) as config_file:
        json_config = json.load(config_file)

    ldap_config = json_config['ldap']
    ldap_init(ldap_config['ro'],
              ldap_config['url'],
              ldap_config['bind_dn'],
              ldap_config['bind_pw'],
              ldap_config['user_ou'],
              ldap_config['group_ou'],
              ldap_config['committee_ou'])
    free_the_zoo(json_config['zoo']['url'], json_config['db']['url'])
