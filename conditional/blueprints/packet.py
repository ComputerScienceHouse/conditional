import json
from datetime import datetime
from operator import itemgetter

import structlog
from flask import Blueprint, redirect, render_template, request, session

from conditional import auth, app, db
from conditional.util import stats as stats_module
from conditional.util.context_processors import get_freshman_name
from conditional.util.mail import send_report_mail
from conditional.util.auth import get_user, needs_auth
from conditional.util.ldap import ldap_is_eval_director
from conditional.util.packet import (
    create_new_packets,
    sync_freshman_list,
    sync_with_ldap,
)
from conditional.models.models import (
    MiscSignature,
    Packet,
    Freshman,
)

logger = structlog.get_logger()

packet_bp = Blueprint("packet_bp", __name__)


class POSTFreshman:
    def __init__(self, freshman):
        self.name = freshman["name"].strip()
        self.rit_username = freshman["rit_username"].strip()
        self.onfloor = freshman["onfloor"].strip() == "TRUE"


@packet_bp.route("/admin/packets")
@auth.oidc_auth("default")
@get_user
def admin_packets(user_dict=None):
    if not ldap_is_eval_director(user_dict["account"]):
        return redirect("/dashboard")

    open_packets = Packet.open_packets()

    # Pre-calculate and store the return values of did_sign(), signatures_received(), and signatures_required()
    for packet in open_packets:
        packet.did_sign_result = packet.did_sign(
            user_dict["username"], app.config["REALM"] == "csh"
        )
        packet.signatures_received_result = packet.signatures_received()
        packet.signatures_required_result = packet.signatures_required()

    open_packets.sort(key=packet_sort_key, reverse=True)

    return render_template(
        "admin_packets.html", open_packets=open_packets, info=user_dict
    )


@packet_bp.route("/admin/freshmen")
@auth.oidc_auth("default")
@get_user
def admin_freshmen(user_dict=None):
    if not ldap_is_eval_director(user_dict["account"]):
        return redirect("/dashboard")

    all_freshmen = Freshman.get_all()

    return render_template(
        "admin_freshmen.html", all_freshmen=all_freshmen, info=user_dict
    )


@packet_bp.route("/api/v1/freshmen", methods=["POST"])
@auth.oidc_auth("default")
@get_user
def sync_freshman(user_dict=None):
    """
    Create or update freshmen entries from a list

    Body parameters: [
        {
         rit_username: string
         name: string
         onfloor: boolean
        }
    ]
    """

    # Only allow evals to create new frosh
    if not ldap_is_eval_director(user_dict["account"]):
        redirect("/dashboard")

    freshmen_in_post = {
        freshman.rit_username: freshman for freshman in map(POSTFreshman, request.json)
    }
    sync_freshman_list(freshmen_in_post)
    return json.dumps("Done"), 200


@packet_bp.route("/api/v1/packets", methods=["POST"])
@auth.oidc_auth("default")
@get_user
def create_packet(user_dict=None):
    """
    Create a new packet.

    Body parameters: {
      start_date: the start date of the packets in MM/DD/YYYY format
      freshmen: [
        {
          rit_username: string
          name: string
          onfloor: boolean
        }
      ]
    }
    """

    # Only allow evals to create new packets
    if not ldap_is_eval_director(user_dict["account"]):
        redirect("/dashboard")

    base_date = datetime.strptime(request.json["start_date"], "%m/%d/%Y").date()

    freshmen_in_post = {
        freshman.rit_username: freshman
        for freshman in map(POSTFreshman, request.json["freshmen"])
    }

    create_new_packets(base_date, freshmen_in_post)

    return json.dumps("Done"), 201


@packet_bp.route("/api/v1/sync", methods=["POST"])
@auth.oidc_auth("default")
@get_user
def sync_ldap(user_dict=None):
    # Only allow evals to sync ldap
    if not ldap_is_eval_director(user_dict["account"]):
        redirect("/dashboard")
    sync_with_ldap()
    return json.dumps("Done"), 201


@packet_bp.route("/api/v1/packets/<username>", methods=["GET"])
@auth.oidc_auth("default")
@get_user
def get_packets_by_user(username: str, user_dict=None) -> dict:
    """
    Return a dictionary of packets for a freshman by username, giving packet start and end date by packet id
    """

    if user_dict["ritdn"] != username:
        redirect("/dashboard")
    frosh = Freshman.by_username(username)

    return {
        packet.id: {
            "start": packet.start,
            "end": packet.end,
        }
        for packet in frosh.packets
    }


@packet_bp.route("/api/v1/packets/<username>/newest", methods=["GET"])
@auth.oidc_auth("default")
@get_user
def get_newest_packet_by_user(username: str, user_dict=None) -> dict:
    """
    Return a user's newest packet
    """

    if not user_dict["is_upper"] and user_dict["ritdn"] != username:
        redirect("/dashboard")

    frosh = Freshman.by_username(username)

    packet = frosh.packets[-1]

    return {
        packet.id: {
            "start": packet.start,
            "end": packet.end,
            "required": vars(packet.signatures_required()),
            "received": vars(packet.signatures_received()),
        }
    }


@packet_bp.route("/api/v1/packet/<packet_id>", methods=["GET"])
@auth.oidc_auth("default")
@get_user
def get_packet_by_id(packet_id: int, user_dict=None) -> dict:
    """
    Return the scores of the packet in question
    """

    packet = Packet.by_id(packet_id)

    if user_dict["ritdn"] != packet.freshman.rit_username:
        redirect("/dashboard")

    return {
        "required": vars(packet.signatures_required()),
        "received": vars(packet.signatures_received()),
    }


@packet_bp.route("/api/v1/sign/<packet_id>/", methods=["POST"])
@needs_auth
def sign(packet_id, user_dict=None):
    packet = Packet.by_id(packet_id)

    if packet is not None and packet.is_open():
        if session["provider"] == "csh":
            # Check if the CSHer is an upperclassman and if so, sign that row
            for sig in filter(
                lambda sig: sig.member == user_dict["uid"], packet.upper_signatures
            ):
                sig.signed = True
                app.logger.info(
                    f"Member {user_dict['uid']} signed packet {packet_id} as an upperclassman"
                )
                return commit_sig(packet)

            # The CSHer is a misc so add a new row
            db.session.add(MiscSignature(packet=packet, member=user_dict["uid"]))
            app.logger.info(
                f"Member {user_dict['uid']} signed packet {packet_id} as a misc"
            )
            return commit_sig(packet)
        if session["provider"] == "frosh":
            # Check if the freshman is onfloor and if so, sign that row
            for sig in filter(
                lambda sig: sig.freshman_username == user_dict["uid"],
                packet.fresh_signatures,
            ):
                sig.signed = True
                app.logger.info(
                    f"Freshman {user_dict['uid']} signed packet {packet_id}"
                )
                return commit_sig(packet)

    app.logger.warning(
        f"Failed to add {user_dict['uid']}'s signature to packet {packet_id}"
    )
    return "Error: Signature not valid.  Reason: Unknown"


@packet_bp.route("/api/v1/report/", methods=["POST"])
@needs_auth
def report(user_dict=None):
    if session["provider"] != "frosh":
        return "Failure", 403

    form_results = request.form
    send_report_mail(form_results, get_freshman_name(user_dict["username"]))
    return "Success: " + get_freshman_name(user_dict["username"]) + " sent a report"


@packet_bp.route("/api/v1/stats/packet/<packet_id>")
@auth.oidc_auth("default")
@get_user
def packet_stats(packet_id, user_dict=None):
    if user_dict["ritdn"] != Packet.by_id(packet_id).freshman.rit_username:
        return redirect("/dashboard")
    return stats_module.packet_stats(packet_id)


@packet_bp.route("/api/v1/stats/upperclassman/<uid>")
@auth.oidc_auth("default")
@get_user
def upperclassman_stats(uid):
    return stats_module.upperclassman_stats(uid)


def commit_sig(packet):
    db.session.commit()

    return "Success: Signed Packet: " + packet.freshman_username


@packet_bp.route("/packet/<packet_id>/")
@needs_auth
def freshman_packet(packet_id, user_dict=None):
    packet = Packet.by_id(packet_id)

    if packet is None:
        return "Invalid packet or freshman", 404

    # The current user's freshman signature on this packet
    fresh_sig = list(
        filter(
            lambda sig: (
                sig.freshman_username == user_dict["ritdn"] if user_dict else ""
            ),
            packet.fresh_signatures,
        )
    )

    return render_template(
        "packet.html",
        info=user_dict,
        packet=packet,
        did_sign=packet.did_sign(user_dict["uid"], app.config["REALM"] == "csh"),
        required=packet.signatures_required(),
        received=packet.signatures_received(),
        upper=packet.upper_signatures,
        fresh_sig=fresh_sig,
    )


def packet_sort_key(packet):
    """
    Utility function for generating keys for sorting packets
    """
    return (
        packet.freshman.name,
        -packet.signatures_received_result.total,
        not packet.did_sign_result,
    )


@packet_bp.route("/packets/")
@needs_auth
def packets(user_dict=None):
    open_packets = Packet.open_packets()

    # Pre-calculate and store the return values of did_sign(), signatures_received(), and signatures_required()
    for packet in open_packets:
        packet.did_sign_result = packet.did_sign(
            user_dict["uid"], app.config["REALM"] == "csh"
        )
        packet.signatures_received_result = packet.signatures_received()
        packet.signatures_required_result = packet.signatures_required()

    open_packets.sort(key=packet_sort_key)

    return render_template("active_packets.html", info=user_dict, packets=open_packets)


@packet_bp.route("/")
def index():
    return """
    <p>Hello, world! 2</p>
    <a href="/packet/auth/frosh">Click here 4 frosh</a>
    <a href="/packet/auth/csh">Click here 4 upper</a>
    """


@app.route("/upperclassmen/")
@auth.oidc_auth("default")
@get_user
def upperclassmen_total(user_dict=None):
    open_packets = Packet.open_packets()

    # Sum up the signed packets per upperclassman
    upperclassmen = {}
    misc = {}
    for packet in open_packets:
        for sig in packet.upper_signatures:
            if sig.member not in upperclassmen:
                upperclassmen[sig.member] = 0

            if sig.signed:
                upperclassmen[sig.member] += 1
        for sig in packet.misc_signatures:
            misc[sig.member] = 1 + misc.get(sig.member, 0)

    return render_template(
        "upperclassmen_totals.html",
        info=user_dict,
        num_open_packets=len(open_packets),
        upperclassmen=sorted(upperclassmen.items(), key=itemgetter(1), reverse=True),
        misc=sorted(misc.items(), key=itemgetter(1), reverse=True),
    )


@app.route("/stats/packet/<packet_id>")
@auth.oidc_auth("default")
@get_user
def packet_graphs(packet_id, user_dict=None):
    stats = packet_stats(packet_id)
    fresh = []
    misc = []
    upper = []

    # Make a rolling sum of signatures over time
    def agg(l, attr, date):
        l.append((l[-1] if l else 0) + len(stats["dates"][date][attr]))

    dates = list(stats["dates"].keys())
    for date in dates:
        agg(fresh, "fresh", date)
        agg(misc, "misc", date)
        agg(upper, "upper", date)

    # Stack misc and upper on top of fresh for a nice stacked line graph
    for i in range(len(dates)):
        misc[i] = misc[i] + fresh[i]
        upper[i] = upper[i] + misc[i]

    return render_template(
        "packet_stats.html",
        info=user_dict,
        data=json.dumps(
            {
                "dates": dates,
                "accum": {
                    "fresh": fresh,
                    "misc": misc,
                    "upper": upper,
                },
                "daily": {},
            }
        ),
        fresh=stats["freshman"],
        packet=Packet.by_id(packet_id),
    )
