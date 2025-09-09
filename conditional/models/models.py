from typing import cast, Optional
import time
from datetime import date, timedelta, datetime
from itertools import chain
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    DateTime,
    Date,
    Text,
    Boolean,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from conditional import db

attendance_enum = Enum("Attended", "Excused", "Absent", name="attendance_enum")


class FreshmanAccount(db.Model):
    __tablename__ = "freshman_accounts"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    eval_date = Column(Date, nullable=False)
    onfloor_status = Column(Boolean)
    room_number = Column(String)
    signatures_missed = Column(Integer)
    rit_username = Column(String(10), nullable=True)

    def __init__(
        self, name, onfloor, room=None, missed=None, rit_username=None
    ):  # pylint: disable=too-many-positional-arguments
        self.name = name
        today = date.fromtimestamp(time.time())
        self.eval_date = today + timedelta(weeks=6)
        self.onfloor_status = onfloor
        self.room_number = room
        self.signatures_missed = missed
        self.rit_username = rit_username


class FreshmanEvalData(db.Model):
    __tablename__ = "freshman_eval_data"
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    freshman_project = Column(
        Enum("Pending", "Passed", "Failed", name="freshman_project_enum"), nullable=True
    )
    eval_date = Column(DateTime, nullable=False)
    signatures_missed = Column(Integer, nullable=False)
    social_events = Column(Text)
    other_notes = Column(Text)
    freshman_eval_result = Column(
        Enum("Pending", "Passed", "Failed", name="freshman_eval_enum"), nullable=False
    )
    active = Column(Boolean)

    def __init__(self, uid, signatures_missed):
        self.uid = uid
        self.freshman_project = None
        self.freshman_eval_result = "Pending"
        self.signatures_missed = signatures_missed
        self.social_events = ""
        self.other_notes = ""
        self.active = True


class CommitteeMeeting(db.Model):
    __tablename__ = "committee_meetings"
    id = Column(Integer, primary_key=True)
    committee = Column(
        Enum(
            "Evaluations",
            "History",
            "Social",
            "Opcomm",
            "R&D",
            "House Improvements",
            "Financial",
            "Public Relations",
            "Chairman",
            "Ad-Hoc",
            name="committees_enum",
        ),
        nullable=False,
    )
    timestamp = Column(DateTime, nullable=False)
    approved = Column(Boolean, nullable=False)
    active = Column(Boolean)

    def __init__(self, committee, timestamp, approved):
        self.committee = committee
        self.timestamp = timestamp
        self.approved = approved
        self.active = True


class MemberCommitteeAttendance(db.Model):
    __tablename__ = "member_committee_attendance"
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    meeting_id = Column(ForeignKey("committee_meetings.id"), nullable=False)

    def __init__(self, uid, meeting_id):
        self.uid = uid
        self.meeting_id = meeting_id


class FreshmanCommitteeAttendance(db.Model):
    __tablename__ = "freshman_committee_attendance"
    id = Column(Integer, primary_key=True)
    fid = Column(ForeignKey("freshman_accounts.id"), nullable=False)
    meeting_id = Column(ForeignKey("committee_meetings.id"), nullable=False)

    def __init__(self, fid, meeting_id):
        self.fid = fid
        self.meeting_id = meeting_id


class TechnicalSeminar(db.Model):
    __tablename__ = "technical_seminars"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    approved = Column(Boolean, nullable=False)
    active = Column(Boolean)

    def __init__(self, name, timestamp, approved):
        self.name = name
        self.timestamp = timestamp
        self.approved = approved
        self.active = True


class MemberSeminarAttendance(db.Model):
    __tablename__ = "member_seminar_attendance"
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    seminar_id = Column(ForeignKey("technical_seminars.id"), nullable=False)

    def __init__(self, uid, seminar_id):
        self.uid = uid
        self.seminar_id = seminar_id


class FreshmanSeminarAttendance(db.Model):
    __tablename__ = "freshman_seminar_attendance"
    id = Column(Integer, primary_key=True)
    fid = Column(ForeignKey("freshman_accounts.id"), nullable=False)
    seminar_id = Column(ForeignKey("technical_seminars.id"), nullable=False)

    def __init__(self, fid, seminar_id):
        self.fid = fid
        self.seminar_id = seminar_id


class MajorProject(db.Model):
    __tablename__ = "major_projects"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    uid = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)
    tldr = Column(String(128), nullable=False)
    time = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False)
    status = Column(
        Enum("Pending", "Passed", "Failed", name="major_project_enum"), nullable=False
    )

    def __init__(
        self, uid, name, tldr, time, desc
    ):  # pylint: disable=too-many-positional-arguments,redefined-outer-name
        self.uid = uid
        self.date = datetime.now()
        self.name = name
        self.tldr = tldr
        self.time = time
        self.description = desc
        self.status = "Pending"
        self.active = True


class HouseMeeting(db.Model):
    __tablename__ = "house_meetings"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False)

    def __init__(self, hm_date):
        self.date = hm_date
        self.active = True


class MemberHouseMeetingAttendance(db.Model):
    __tablename__ = "member_hm_attendance"
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    meeting_id = Column(ForeignKey("house_meetings.id"), nullable=False)
    excuse = Column(Text)
    attendance_status = Column(attendance_enum)

    def __init__(self, uid, meeting_id, excuse, status):
        self.uid = uid
        self.meeting_id = meeting_id
        self.excuse = excuse
        self.attendance_status = status


class FreshmanHouseMeetingAttendance(db.Model):
    __tablename__ = "freshman_hm_attendance"
    id = Column(Integer, primary_key=True)
    fid = Column(ForeignKey("freshman_accounts.id"), nullable=False)
    meeting_id = Column(ForeignKey("house_meetings.id"), nullable=False)
    excuse = Column(Text)
    attendance_status = Column(attendance_enum)

    def __init__(self, fid, meeting_id, excuse, status):
        self.fid = fid
        self.meeting_id = meeting_id
        self.excuse = excuse
        self.attendance_status = status


class CurrentCoops(db.Model):
    __tablename__ = "current_coops"
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    date_created = Column(Date, nullable=False)
    semester = Column(Enum("Fall", "Spring", name="co_op_enum"), nullable=False)

    def __init__(self, uid, semester):
        self.uid = uid
        self.active = True
        self.date_created = datetime.now()
        self.semester = semester


class OnFloorStatusAssigned(db.Model):
    __tablename__ = "onfloor_datetime"
    uid = Column(String(32), primary_key=True)
    onfloor_granted = Column(DateTime, primary_key=True)

    def __init__(self, uid, time_granted):
        self.uid = uid
        self.onfloor_granted = time_granted


class Conditional(db.Model):
    __tablename__ = "conditional"
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    description = Column(String(512), nullable=False)
    date_created = Column(Date, nullable=False)
    date_due = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False)
    status = Column(
        Enum("Pending", "Passed", "Failed", name="conditional_enum"), nullable=False
    )
    s_evaluation = Column(ForeignKey("spring_evals.id"))
    i_evaluation = Column(ForeignKey("freshman_eval_data.id"))

    def __init__(
        self, uid, description, due, s_eval=None, i_eval=None
    ):  # pylint: disable=too-many-positional-arguments
        self.uid = uid
        self.description = description
        self.date_due = due
        self.date_created = datetime.now()
        self.status = "Pending"
        self.active = True
        self.s_evaluation = s_eval
        self.i_evaluation = i_eval


class EvalSettings(db.Model):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    housing_form_active = Column(Boolean)
    intro_form_active = Column(Boolean)
    site_lockdown = Column(Boolean)
    accept_dues_until = Column(Date)

    def __init__(self):
        self.housing_form_active = True
        self.intro_form_active = True
        self.site_lockdown = False
        self.accept_dues_until = datetime.now()


class SpringEval(db.Model):
    __tablename__ = "spring_evals"
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    active = Column(Boolean, nullable=False)
    date_created = Column(Date, nullable=False)
    status = Column(
        Enum("Pending", "Passed", "Failed", name="spring_eval_enum"), nullable=False
    )

    def __init__(self, uid):
        self.uid = uid
        self.active = True
        self.date_created = datetime.now()
        self.status = "Pending"


class InHousingQueue(db.Model):
    __tablename__ = "in_housing_queue"
    uid = Column(String(32), primary_key=True)


http_enum = Enum(
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH",
    name="http_enum",
)


class UserLog(db.Model):
    __tablename__ = "user_log"
    id = Column(Integer, primary_key=True)
    ipaddr = Column(postgresql.INET, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    uid = Column(String(32), nullable=False)
    method = Column(http_enum)
    blueprint = Column(String(32), nullable=False)
    path = Column(String(128), nullable=False)
    description = Column(String(128), nullable=False)

    def __init__(
        self, ipaddr, user, method, blueprint, path, description
    ):  # pylint: disable=too-many-positional-arguments
        self.ipaddr = ipaddr
        self.timestamp = datetime.now()
        self.uid = user
        self.method = method
        self.blueprint = blueprint
        self.path = path
        self.description = description


# The required number of honorary member, advisor, and alumni signatures
REQUIRED_MISC_SIGNATURES = 10


class SigCounts:
    """
    Utility class for returning counts of signatures broken out by type
    """

    def __init__(self, upper: int, fresh: int, misc: int):
        # Base fields
        self.upper = upper
        self.fresh = fresh
        self.misc = misc

        # Capped version of misc so it will never be greater than REQUIRED_MISC_SIGNATURES
        self.misc_capped = (
            misc if misc <= REQUIRED_MISC_SIGNATURES else REQUIRED_MISC_SIGNATURES
        )

        # Totals (calculated using misc_capped)
        self.member_total = upper + self.misc_capped
        self.total = upper + fresh + self.misc_capped


class Freshman(db.Model):
    __tablename__ = "freshman"
    rit_username = cast(str, Column(String(10), primary_key=True))
    name = cast(str, Column(String(64), nullable=False))
    onfloor = cast(bool, Column(Boolean, nullable=False))
    fresh_signatures = cast("FreshSignature", relationship("FreshSignature"))

    # One freshman can have multiple packets if they repeat the intro process
    packets = cast("Packet", relationship("Packet", order_by="desc(Packet.id)"))

    @classmethod
    def by_username(cls, username: str) -> "Packet":
        """
        Helper method to retrieve a freshman by their RIT username
        """
        return cls.query.filter_by(rit_username=username).first()

    @classmethod
    def get_all(cls) -> list["Packet"]:
        """
        Helper method to get all freshmen easily
        """
        return cls.query.all()


class Packet(db.Model):
    __tablename__ = "packet"
    id = cast(int, Column(Integer, primary_key=True, autoincrement=True))
    freshman_username = cast(str, Column(ForeignKey("freshman.rit_username")))
    start = cast(datetime, Column(DateTime, nullable=False))
    end = cast(datetime, Column(DateTime, nullable=False))

    freshman = cast(Freshman, relationship("Freshman", back_populates="packets"))

    # The `lazy='subquery'` kwarg enables eager loading for signatures which makes signature calculations much faster
    # See the docs here for details: https://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html
    upper_signatures = cast(
        "UpperSignature",
        relationship(
            "UpperSignature",
            lazy="subquery",
            order_by="UpperSignature.signed.desc(), UpperSignature.updated",
        ),
    )
    fresh_signatures = cast(
        "FreshSignature",
        relationship(
            "FreshSignature",
            lazy="subquery",
            order_by="FreshSignature.signed.desc(), FreshSignature.updated",
        ),
    )
    misc_signatures = cast(
        "MiscSignature",
        relationship(
            "MiscSignature", lazy="subquery", order_by="MiscSignature.updated"
        ),
    )

    def is_open(self) -> bool:
        return self.start < datetime.now() < self.end

    def signatures_required(self) -> SigCounts:
        """
        :return: A SigCounts instance with the fields set to the number of signatures received by this packet
        """
        upper = len(self.upper_signatures)
        fresh = len(self.fresh_signatures)

        return SigCounts(upper, fresh, REQUIRED_MISC_SIGNATURES)

    def signatures_received(self) -> SigCounts:
        """
        :return: A SigCounts instance with the fields set to the number of required signatures for this packet
        """
        upper = sum(map(lambda sig: 1 if sig.signed else 0, self.upper_signatures))
        fresh = sum(map(lambda sig: 1 if sig.signed else 0, self.fresh_signatures))

        return SigCounts(upper, fresh, len(self.misc_signatures))

    def did_sign(self, username: str, is_csh: bool) -> bool:
        """
        :param username: The CSH or RIT username to check for
        :param is_csh: Set to True for CSH accounts and False for freshmen
        :return: Boolean value for if the given account signed this packet
        """
        if is_csh:
            for sig in filter(
                lambda sig: sig.member == username,
                chain(self.upper_signatures, self.misc_signatures),
            ):
                if isinstance(sig, MiscSignature):
                    return True
                return sig.signed
        else:
            for sig in filter(
                lambda sig: sig.freshman_username == username, self.fresh_signatures
            ):
                return sig.signed

        # The user must be a misc CSHer that hasn't signed this packet or an off-floor freshmen
        return False

    def is_100(self) -> bool:
        """
        Checks if this packet has reached 100%
        """
        return self.signatures_required().total == self.signatures_received().total

    @classmethod
    def open_packets(cls) -> list["Packet"]:
        """
        Helper method for fetching all currently open packets
        """
        return cls.query.filter(
            cls.start < datetime.now(), cls.end > datetime.now()
        ).all()

    @classmethod
    def by_id(cls, packet_id: int) -> "Packet":
        """
        Helper method for fetching 1 packet by its id
        """
        return cls.query.filter_by(id=packet_id).first()


class UpperSignature(db.Model):
    __tablename__ = "signature_upper"
    packet_id = cast(int, Column(Integer, ForeignKey("packet.id"), primary_key=True))
    member = cast(str, Column(String(36), primary_key=True))
    signed = cast(bool, Column(Boolean, default=False, nullable=False))
    eboard = cast(Optional[str], Column(String(12), nullable=True))
    active_rtp = cast(bool, Column(Boolean, default=False, nullable=False))
    three_da = cast(bool, Column(Boolean, default=False, nullable=False))
    webmaster = cast(bool, Column(Boolean, default=False, nullable=False))
    c_m = cast(bool, Column(Boolean, default=False, nullable=False))
    w_m = cast(bool, Column(Boolean, default=False, nullable=False))
    drink_admin = cast(bool, Column(Boolean, default=False, nullable=False))
    updated = cast(
        datetime,
        Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    )

    packet = cast(Packet, relationship("Packet", back_populates="upper_signatures"))


class FreshSignature(db.Model):
    __tablename__ = "signature_fresh"
    packet_id = cast(int, Column(Integer, ForeignKey("packet.id"), primary_key=True))
    freshman_username = cast(
        str, Column(ForeignKey("freshman.rit_username"), primary_key=True)
    )
    signed = cast(bool, Column(Boolean, default=False, nullable=False))
    updated = cast(
        datetime,
        Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    )

    packet = cast(Packet, relationship("Packet", back_populates="fresh_signatures"))
    freshman = cast(
        Freshman, relationship("Freshman", back_populates="fresh_signatures")
    )


class MiscSignature(db.Model):
    __tablename__ = "signature_misc"
    packet_id = cast(int, Column(Integer, ForeignKey("packet.id"), primary_key=True))
    member = cast(str, Column(String(36), primary_key=True))
    updated = cast(
        datetime,
        Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    )

    packet = cast(Packet, relationship("Packet", back_populates="misc_signatures"))


class NotificationSubscription(db.Model):
    __tablename__ = "notification_subscriptions"
    member = cast(str, Column(String(36), nullable=True))
    freshman_username = cast(
        str, Column(ForeignKey("freshman.rit_username"), nullable=True)
    )
    token = cast(str, Column(String(256), primary_key=True, nullable=False))
