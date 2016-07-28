from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, \
                       Date, Text, Boolean
from db.database import Base
import time
from datetime import date, timedelta, datetime

attendance_enum = Enum('Attended', 'Excused', 'Absent', name='attendance_enum')

class FreshmanAccount(Base):
    __tablename__ = 'freshman_accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    eval_date = Column(Date, nullable=False)
    onfloor_status = Column(Boolean)
    room_number = Column(Integer)

    def __init__(self, name, onfloor, room=None):
        self.name = name
        today = date.fromtimestamp(time.time())
        self.eval_date = today + timedelta(weeks=10)
        self.onfloor_status = onfloor
        self.room_number = room

class FreshmanEvalData(Base):
    __tablename__ = 'freshman_eval_data'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    freshman_project = Column(Enum('Pending', 'Passed', 'Failed',
        name="freshman_project_enum"), nullable=False)
    eval_date = Column(DateTime, nullable=False)
    signatures_missed = Column(Integer, nullable=False)
    social_events = Column(Text)
    other_notes = Column(Text)
    freshman_eval_result = Column(Enum('Pending', 'Passed', 'Failed',
        name="freshman_eval_enum"), nullable=False)
    active = Column(Boolean)

    def __init__(self, uid, signatures_missed):
        self.uid = uid
        self.freshman_project = 'Pending'
        self.freshman_eval_result = 'Pending'
        self.signatures_missed = signatures_missed
        self.social_events = ""
        self.other_notes = ""
        self.active = True

class CommitteeMeeting(Base):
    __tablename__ = 'committee_meetings'
    id = Column(Integer, primary_key=True)
    committee = Column(Enum('Evaluations', 'History', 'Social', 'Opcomm',
        'R&D', 'House Improvements', 'Financial', 'Chairman', name="committees_enum"),
        nullable=False)
    timestamp = Column(DateTime, nullable=False)
    active = Column(Boolean)

    def __init__(self, committee, timestamp):
        self.committee = committee
        self.timestamp = timestamp
        self.active = True

class MemberCommitteeAttendance(Base):
    __tablename__ = 'member_committee_attendance'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    meeting_id = Column(ForeignKey('committee_meetings.id'), nullable=False)

    def __init__(self, uid, meeting_id):
        self.uid = uid
        self.meeting_id = meeting_id

class FreshmanCommitteeAttendance(Base):
    __tablename__ = 'freshman_committee_attendance'
    id = Column(Integer, primary_key=True)
    fid = Column(ForeignKey('freshman_accounts.id'), nullable=False)
    meeting_id = Column(ForeignKey('committee_meetings.id'), nullable=False)

    def __init__(self, fid, meeting_id):
        self.fid = fid
        self.meeting_id = meeting_id

class TechnicalSeminar(Base):
    __tablename__ = 'technical_seminars'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    active = Column(Boolean)

    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp
        self.active = True

class MemberSeminarAttendance(Base):
    __tablename__ = 'member_seminar_attendance'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    seminar_id = Column(ForeignKey('technical_seminars.id'), nullable=False)

    def __init__(self, uid, seminar_id):
        self.uid = uid
        self.seminar_id = seminar_id

class FreshmanSeminarAttendance(Base):
    __tablename__ = 'freshman_seminar_attendance'
    id = Column(Integer, primary_key=True)
    fid = Column(ForeignKey('freshman_accounts.id'), nullable=False)
    seminar_id = Column(ForeignKey('technical_seminars.id'), nullable=False)

    def __init__(self, fid, seminar_id):
        self.fid = fid
        self.seminar_id = seminar_id

class MajorProject(Base):
    __tablename__ = 'major_projects'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)
    description = Column(Text)
    active = Column(Boolean, nullable=False)
    status = Column(Enum('Pending', 'Passed', 'Failed',
                          name="major_project_enum"),
                    nullable=False)

    def __init__(self, uid, name, desc):
        self.uid = uid
        self.name = name
        self.description = desc
        self.status = 'Pending'
        self.active = True

class HouseMeeting(Base):
    __tablename__ = 'house_meetings'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False)

    def __init__(self, date):
        self.date = date
        self.active = True

class MemberHouseMeetingAttendance(Base):
    __tablename__ = 'member_hm_attendance'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    meeting_id = Column(ForeignKey('house_meetings.id'), nullable=False)
    excuse = Column(Text)
    attendance_status = Column(attendance_enum)

    def __init__(self, uid, meeting_id, excuse, status):
        self.uid = uid
        self.meeting_id = meeting_id
        self.excuse = excuse
        self.attendance_status = status

class FreshmanHouseMeetingAttendance(Base):
    __tablename__ = 'freshman_hm_attendance'
    id = Column(Integer, primary_key=True)
    fid = Column(ForeignKey('freshman_accounts.id'), nullable=False)
    meeting_id = Column(ForeignKey('house_meetings.id'), nullable=False)
    excuse = Column(Text)
    attendance_status = Column(attendance_enum)

    def __init__(self, fid, meeting_id, excuse, status):
        self.fid = fid
        self.meeting_id = meeting_id
        self.excuse = excuse
        self.attendance_status = status

class CurrentCoops(Base):
    __tablename__ = 'current_coops'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    active = Column(Boolean, nullable=False)
    date_created = Column(Date, nullable=False)

    def __init__(self, uid):
        self.uid = uid
        self.active = True
        self.date_created = datetime.now()

class OnFloorStatusAssigned(Base):
    __tablename__ = 'onfloor_datetime'
    uid = Column(String(32), primary_key=True)
    onfloor_granted = Column(DateTime, primary_key=True)

    def __init__(self, uid, datetime):
        self.uid = uid
        self.onfloor_granted = datetime

class Conditional(Base):
    __tablename__ = 'conditional'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    description = Column(String(512), nullable=False)
    date_created = Column(Date, nullable=False)
    date_due = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False)
    status = Column(Enum('Pending', 'Passed', 'Failed',
                          name="conditional_enum"),
                          nullable=False)

    def __init__(self, uid, description, due):
        self.uid = uid
        self.description = description
        self.date_due = due
        self.date_created = datetime.utcnow()
        self.status = "Pending"
        self.active = True

class EvalSettings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    housing_form_active = Column(Boolean)
    intro_form_active = Column(Boolean)
    site_lockdown = Column(Boolean)

    def __init__(self):
        self.housing_form_active = True
        self.intro_form_active = True
        self.site_lockdown = False

class SpringEval(Base):
    __tablename__ = 'spring_evals'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    active = Column(Boolean, nullable=False)
    date_created = Column(Date, nullable=False)
    status = Column(Enum('Pending', 'Passed', 'Failed',
                          name="spring_eval_enum"),
                          nullable=False)

    def __init__(self, uid):
        self.uid = uid
        self.active = True
        self.date_created = datetime.now()
        self.status = "Pending"

class HousingEvalsSubmission(Base):
    __tablename__ = 'housing_evals'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    social_attended = Column(Text, nullable=False)
    social_hosted = Column(Text, nullable=False)
    technical_attended = Column(Text, nullable=False)
    technical_hosted = Column(Text, nullable=False)
    projects = Column(Text, nullable=False)
    comments = Column(Text, nullable=False)
    points = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False)
    date_created = Column(Date, nullable=False)

    def __init__(self, uid, social_attended,
        social_hosted, technical_attended,
        technical_hosted, projects, comments):

        self.uid = uid
        self.social_attended = social_attended
        self.social_hosted = social_hosted
        self.technical_attended = technical_attended
        self.technical_hosted = technical_hosted
        self.projects = projects
        self.comments = comments
        self.points = 0
        self.active = True
        self.date_created = datetime.now()
