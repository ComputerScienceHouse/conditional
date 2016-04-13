from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request

import json

from util.flask import render_template
from blueprints.intro_evals import display_intro_evals
from blueprints.spring_evals import display_spring_evals

slideshow_bp = Blueprint('slideshow_bp', __name__)

@slideshow_bp.route('/slideshow/intro')
def slideshow_intro_display():
    user_name = request.headers.get('x-webauth-user')
    if not ldap_is_eval_director(user_name) and user_name != "loothelion":
        return redirect("/dashboard")

    return render_template(request,
                           'slideshow_intro.html',
                           username = user_name,
                           date = datetime.utcnow().strftime("%Y-%m-%d"),
                           members = get_non_alumni_non_coop(internal=True))

@slideshow_bp.route('/slideshow/intro/members')
def slideshow_intro_members():
    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_intro_evals(internal=True))

@slideshow_bp.route('/slideshow/spring/members')
def slideshow_spring_members():
    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_spring_evals(internal=True))
