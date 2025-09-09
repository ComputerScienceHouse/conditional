from datetime import datetime, date, time, timedelta
from typing import Any, cast

import structlog

from conditional import db, logger
from conditional.models.models import (
    Freshman,
    MiscSignature,
    Packet,
    FreshSignature,
    UpperSignature,
)
from conditional.util.ldap import (
    ldap_get_eboard_role,
    ldap_get_rtps,
    ldap_get_3das,
    ldap_get_webmasters,
    ldap_get_cms,
    ldap_get_wms,
    ldap_get_drink_admins,
    ldap_get_active_members,
    ldap_is_intromember,
    ldap_is_on_coop,
)
from conditional.util.mail import send_start_packet_mail

logger = structlog.get_logger()


def sync_freshman_list(freshmen_list: dict) -> None:
    freshmen_in_db = {
        freshman.rit_username: freshman for freshman in Freshman.query.all()
    }

    for list_freshman in freshmen_list.values():
        if list_freshman.rit_username not in freshmen_in_db:
            # This is a new freshman so add them to the DB
            freshmen_in_db[list_freshman.rit_username] = Freshman(
                rit_username=list_freshman.rit_username,
                name=list_freshman.name,
                onfloor=list_freshman.onfloor,
            )
            db.session.add(freshmen_in_db[list_freshman.rit_username])
        else:
            # This freshman is already in the DB so just update them
            freshmen_in_db[list_freshman.rit_username].onfloor = list_freshman.onfloor
            freshmen_in_db[list_freshman.rit_username].name = list_freshman.name

    # Update all freshmen entries that represent people who are no longer freshmen
    for freshman in filter(
        lambda freshman: freshman.rit_username not in freshmen_list,
        freshmen_in_db.values(),
    ):
        freshman.onfloor = False

    # Update the freshmen signatures of each open or future packet
    for packet in Packet.query.filter(Packet.end > datetime.now()).all():
        # pylint: disable=cell-var-from-loop
        current_fresh_sigs = set(
            map(lambda fresh_sig: fresh_sig.freshman_username, packet.fresh_signatures)
        )
        for list_freshman in filter(
            lambda list_freshman: list_freshman.rit_username not in current_fresh_sigs
            and list_freshman.rit_username != packet.freshman_username,
            freshmen_list.values(),
        ):
            db.session.add(
                FreshSignature(
                    packet=packet, freshman=freshmen_in_db[list_freshman.rit_username]
                )
            )

    db.session.commit()


def create_new_packets(base_date: date, freshmen_list: dict) -> None:
    packet_start_time = time(hour=19)
    packet_end_time = time(hour=21)
    start = datetime.combine(base_date, packet_start_time)
    end = datetime.combine(base_date, packet_end_time) + timedelta(days=14)

    logger.info("Fetching data from LDAP...")
    all_upper = list(
        filter(
            lambda member: not ldap_is_intromember(member)
            and not ldap_is_on_coop(member),
            ldap_get_active_members(),
        )
    )

    rtp = [member.uid for member in ldap_get_rtps()]
    three_da = [member.uid for member in ldap_get_3das()]
    webmaster = [member.uid for member in ldap_get_webmasters()]
    c_m = [member.uid for member in ldap_get_cms()]
    w_m = [member.uid for member in ldap_get_wms()]
    drink = [member.uid for member in ldap_get_drink_admins()]

    # Create the new packets and the signatures for each freshman in the given CSV
    logger.info("Creating DB entries and sending emails...")
    for freshman in Freshman.query.filter(
        cast(Any, Freshman.rit_username).in_(freshmen_list)
    ).all():
        packet = Packet(freshman=freshman, start=start, end=end)
        db.session.add(packet)
        send_start_packet_mail(packet)

        for member in all_upper:
            sig = UpperSignature(packet=packet, member=member.uid)
            sig.eboard = ldap_get_eboard_role(member)
            sig.active_rtp = member.uid in rtp
            sig.three_da = member.uid in three_da
            sig.webmaster = member.uid in webmaster
            sig.c_m = member.uid in c_m
            sig.w_m = member.uid in w_m
            sig.drink_admin = member.uid in drink
            db.session.add(sig)

        for frosh in Freshman.query.filter(
            Freshman.rit_username != freshman.rit_username
        ).all():
            db.session.add(FreshSignature(packet=packet, freshman=frosh))

    db.session.commit()


def sync_with_ldap() -> None:
    logger.info("Fetching data from LDAP...")
    all_upper = {
        member.uid: member
        for member in filter(
            lambda member: not ldap_is_intromember(member)
            and not ldap_is_on_coop(member),
            ldap_get_active_members(),
        )
    }

    rtp = ldap_get_rtps()
    three_da = ldap_get_3das()
    webmaster = ldap_get_webmasters()
    c_m = ldap_get_cms()
    w_m = ldap_get_wms()
    drink = ldap_get_drink_admins()

    logger.info("Applying updates to the DB...")
    for packet in Packet.query.filter(Packet.end > datetime.now()).all():
        # Update the role state of all UpperSignatures
        for sig in filter(lambda sig: sig.member in all_upper, packet.upper_signatures):
            sig.eboard = ldap_get_eboard_role(all_upper[sig.member])
            sig.active_rtp = sig.member in rtp
            sig.three_da = sig.member in three_da
            sig.webmaster = sig.member in webmaster
            sig.c_m = sig.member in c_m
            sig.w_m = sig.member in w_m
            sig.drink_admin = sig.member in drink

        # Migrate UpperSignatures that are from accounts that are not active anymore
        for sig in filter(
            lambda sig: sig.member not in all_upper, packet.upper_signatures
        ):
            UpperSignature.query.filter_by(
                packet_id=packet.id, member=sig.member
            ).delete()
            if sig.signed:
                sig = MiscSignature(packet=packet, member=sig.member)
                db.session.add(sig)

        # Migrate MiscSignatures that are from accounts that are now active members
        for sig in filter(lambda sig: sig.member in all_upper, packet.misc_signatures):
            MiscSignature.query.filter_by(
                packet_id=packet.id, member=sig.member
            ).delete()
            sig = UpperSignature(packet=packet, member=sig.member, signed=True)
            sig.eboard = ldap_get_eboard_role(all_upper[sig.member])
            sig.active_rtp = sig.member in rtp
            sig.three_da = sig.member in three_da
            sig.webmaster = sig.member in webmaster
            sig.c_m = sig.member in c_m
            sig.w_m = sig.member in w_m
            sig.drink_admin = sig.member in drink
            db.session.add(sig)

        # Create UpperSignatures for any new active members
        # pylint: disable=cell-var-from-loop
        upper_sigs = set(map(lambda sig: sig.member, packet.upper_signatures))
        for member in filter(lambda member: member not in upper_sigs, all_upper):
            sig = UpperSignature(packet=packet, member=member)
            sig.eboard = ldap_get_eboard_role(all_upper[sig.member])
            sig.active_rtp = sig.member in rtp
            sig.three_da = sig.member in three_da
            sig.webmaster = sig.member in webmaster
            sig.c_m = sig.member in c_m
            sig.w_m = sig.member in w_m
            sig.drink_admin = sig.member in drink
            db.session.add(sig)

    db.session.commit()
