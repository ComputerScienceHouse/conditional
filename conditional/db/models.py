from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, \
                       Date, Text, Boolean
from db.database import Base
import time
from datetime import date, timedelta

class FreshmanAccount(Base):
    __tablename__ = 'freshman_accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    eval_date = Column(Date, nullable=False)

    def __init__(self, name):
        self.name = name
        today = date.fromtimestamp(time.time())
        self.eval_date = today + timedelta(weeks=10)

class FreshmanEvalData(Base):
    __tablename__ = 'freshman_eval_data'
    uid = Column(String(32), nullable=False)
    freshman_project = Column(Enum('Pending', 'Passed', 'Failed',
        name="freshman_project_enum"), nullable=False)
    signatures_missed = Column(Integer, nullable=False)
    social_events = Column(Text)
    other_notes = Column(Text)

    def __init__(self, uid, signatures_missed):
        self.uid = uid
        self.freshman_project = 'Pending'
        self.signatures_missed = signatures_missed
        self.social_events = ""
        self.other_notes = ""

class CommitteeMeeting(Base):
    __tablename__ = 'committee_meetings'
    id = Column(Integer, primary_key=True)
    committee = Column(Enum('Evaluations', 'History', 'Social', 'Opcomm',
        'R&D', 'House Improvements', 'Financial', name="committees_enum"),
        nullable=False)
    timestamp = Column(DateTime, nullable=False)
    active = Column(Boolean)

    def __init__(self, committee, timestamp):
        self.committee = committee
        self.timestamp = timestamp
        self.active = True

class MemberCommitteeAttendance(Base):
    __tablename__ = 'member_committee_attendance'
    uid = Column(String(32), nullable=False)
    meeting_id = Column(ForeignKey('committee_meetings.id'), nullable=False)

    def __init__(self, uid, meeting_id):
        self.uid = uid
        self.meeting_id = meeting_id

class FreshmanCommitteeAttendance(Base):
    __tablename__ = 'freshman_committee_attendance'
    fid = Column(ForeignKey('freshman_accounts.id'), nullable=False)
    meeting_id = Column(ForeignKey('committee_meetings.id'), nullable=False)

    def __init__(self, fid, meeting_id):
        self.fid = fid
        self.meeting_id = meeting_id

class TechnicalSeminar(Base):
    __tablename__ = 'technical_seminars'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    active = Column(Boolean)

    def __init__(self, name):
        self.name = name
        self.active = True

class MemberSeminarAttendance(Base):
    __tablename__ = 'member_seminar_attendance'
    uid = Column(String(32), nullable=False)
    seminar_id = Column(ForeignKey('technical_seminars.id'), nullable=False)

    def __init__(self, uid, seminar_id):
        self.uid = uid
        self.seminar_id = seminar_id 

class FreshmanSeminarAttendance(Base):
    __tablename__ = 'freshman_seminar_attendance'
    fid = Column(ForeignKey('freshman_accounts.id'), nullable=False)
    meeting_id = Column(ForeignKey('technical_seminars.id'), nullable=False)

    def __init__(self, fid, seminar_id):
        self.fid = fid
        self.seminar_id = seminar_id

class MajorProject(Base):
    __tablename__ = 'major_projects'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)
    description = Column(Text)
    status = Column(Enum('Pending', 'Passed', 'Failed', 
                          name="major_project_enum"), 
                    nullable=False)

    def __init__(self, uid, name, desc):
        self.uid = uid
        self.name = name
        self.description = desc
        self.status = 'Pending'

class HouseMeeting(Base):
    __tablename__ = 'house_meetings'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False)

    def __init__(self, date):
        self.date = date
        self.active = True

class CurrentCoops(Base):
    __tablename__ = 'current_coops'
    username = Column(String(32), nullable=False)

    def __init__(self, username):
        self.username = username
