from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from util.ldap import ldap_get_all_members, ldap_get_non_alumni_members, ldap_get_name

from db.models import CurrentCoops

attendance_bp = Blueprint('attendance_bp', __name__)

def get_name(m):
    first = None
    if 'givenName' in m:
        first = m['givenName'][0].decode('utf-8')
    else:
        first = ""
    last = None
    if 'sn' in m:
        last = m['sn'][0].decode('utf-8')
    else:
        last = ""
    return "{first} {last}".format(first=first, last=last)

@attendance_bp.route('/attendance/ts_members')
def get_all_members():
    members = ldap_get_all_members()

    named_members = []
    for m in members:
        uid = m['uid'][0].decode('utf-8')
        name = "{name} ({uid})".format(name=get_name(m), uid=uid)

        named_members.append(
            {
                'display': name,
                'value': uid
            })

    return jsonify({'members': named_members}), 200

@attendance_bp.route('/attendance/hm_members')
def get_non_alumni_non_coop():
    non_alumni_members = ldap_get_non_alumni_members()
    coop_members = [u.username for u in CurrentCoops.query.all()]

    named_members = []
    for m in non_alumni_members:
        uid = m['uid'][0].decode('utf-8')

        if uid in coop_members:
            continue
        name = "{name} ({uid})".format(name=get_name(m), uid=uid)

        named_members.append(
            {
                'display': name,
                'value': uid
            })

    return jsonify({'members': named_members}), 200


@attendance_bp.route('/attendance/cm_members')
def get_non_alumni():
    non_alumni_members = ldap_get_non_alumni_members()

    named_members = []
    for m in non_alumni_members:
        uid = m['uid'][0].decode('utf-8')
        name = "{name} ({uid})".format(name=get_name(m), uid=uid)

        named_members.append(
            {
                'display': name,
                'value': uid
            })

    return jsonify({'members': named_members}), 200

@attendance_bp.route('/attendance/')
def display_attendance():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    return "", 200
    # return names in 'first last (username)' format
