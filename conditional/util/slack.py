from slack_sdk import WebClient
from slack_sdk.errors import SlackRequestError

from conditional import app

client = WebClient(token=app.config['SLACK_APP_TOKEN'])
active_usergroup_id = "S0C7AK4AXEV" # should figure out a better way to do this rather than hardcoding
frosh_usergroup_id = "S0C7CBNRPC4"
meetings_usergroup_id = "S0C78GDRLG2"

def get_usergroup_users(usergroup_id):
    response = client.usergroups_users_list(
        usergroup=usergroup_id
    )

    users = response['users']
    response_code = response['ok']
    if response_code == 'false':
        raise SlackRequestError(response["error"])
    
    return users

def add_usergroup_user(usergroup_id, slack_uid):
    group_users = get_usergroup_users(usergroup_id)
    group_users.append(slack_uid)

    response = client.usergroups_users_update(
        usergroup=usergroup_id,
        users=group_users
    )

    response_code = response["ok"]
    if response_code == 'false':
        raise SlackRequestError(response["error"])
    
    return response_code

def add_active_usergroup_user(slack_uid):
    return add_usergroup_user(active_usergroup_id, slack_uid)

def add_meetings_usergroup_user(slack_uid):
    return add_usergroup_user(meetings_usergroup_id, slack_uid)

def purge_usergroup_users(usergroup_id, slack_uid):
    response = client.usergroups_users_update(
        usergroup=usergroup_id,
        users=slack_uid
    )

    response_code = response["ok"]
    if response_code == 'false':
        raise SlackRequestError(response["error"])
    
    return response_code

def purge_active_usergroup(slack_uid):
    return purge_usergroup_users(active_usergroup_id, slack_uid)

def purge_frosh_usergroup(slack_uid):
    return purge_usergroup_users(frosh_usergroup_id, slack_uid)

def purge_meetings_usergroup(slack_uid):
    return purge_usergroup_users(meetings_usergroup_id, slack_uid)
    