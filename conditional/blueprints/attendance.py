from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from util.ldap import ldap_get_all_members, ldap_get_non_alumni_members, ldap_get_name

from db.models import CurrentCoops

attendance_bp = Blueprint('attendance_bp', __name__)

@attendance_bp.route('/attendance/ts_members')
def get_all_members():
    members = ldap_get_all_members()

    named_members = []
    for m in members:
        uid = m
        name = ldap_get_name(m)
        named_members.append("{name} ({uid})".format(name=name, uid=uid))

    return jsonify({'members': named_members}), 200

@attendance_bp.route('/attendance/hm_members')
def get_non_alumni_non_coop():
    non_alumni_members = ldap_get_non_alumni_members()
    coop_members = [u.username for u in CurrentCoops.query.all()]

    members = list(set(non_alumni_members).difference(coop_members))


    named_members = []
    for m in members:
        uid = m
        name = ldap_get_name(m)
        named_members.append("{name} ({uid})".format(name=name, uid=uid))

    return jsonify({'members': named_members}), 200


@attendance_bp.route('/attendance/cm_members')
def get_non_alumni():
    non_alumni_members = ldap_get_non_alumni_members()

    named_members = []
    for m in non_alumni_members:
        uid = m
        name = ldap_get_name(m)
        named_members.append("{name} ({uid})".format(name=name, uid=uid))

    return jsonify({'members': named_members}), 200

@attendance_bp.route('/attendance/')
def display_attendance():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    return "", 200
    # return names in 'first last (username)' format
