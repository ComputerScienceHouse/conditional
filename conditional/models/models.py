import time
from datetime import date, timedelta, datetime
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, \
    Date, Text, Boolean
from sqlalchemy.dialects import postgresql
from conditional import db

attendance_enum = Enum('Attended', 'Excused', 'Absent', name='attendance_enum')


class FreshmanAccount(db.Model):
    __tablename__ = 'freshman_accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    eval_date = Column(Date, nullable=False)
    onfloor_status = Column(Boolean)
    room_number = Column(String)
    signatures_missed = Column(Integer)

    def __init__(self, name, onfloor, room=None, missed=None):
        self.name = name
        today = date.fromtimestamp(time.time())
        self.eval_date = today + timedelta(weeks=10)
        self.onfloor_status = onfloor
        self.room_number = room
        self.signatures_missed = missed


class FreshmanEvalData(db.Model):
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


class CommitteeMeeting(db.Model):
    __tablename__ = 'committee_meetings'
    id = Column(Integer, primary_key=True)
    committee = Column(Enum('Evaluations', 'History', 'Social', 'Opcomm',
                            'R&D', 'House Improvements', 'Financial', 'Chairman', name="committees_enum"),
                       nullable=False)
    timestamp = Column(DateTime, nullable=False)
    approved = Column(Boolean, nullable=False)
    active = Column(Boolean)

    def __init__(self, committee, timestamp, approved):
        self.committee = committee
        self.timestamp = timestamp
        self.approved = approved
        self.active = True


class MemberCommitteeAttendance(db.Model):
    __tablename__ = 'member_committee_attendance'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    meeting_id = Column(ForeignKey('committee_meetings.id'), nullable=False)

    def __init__(self, uid, meeting_id):
        self.uid = uid
        self.meeting_id = meeting_id


class FreshmanCommitteeAttendance(db.Model):
    __tablename__ = 'freshman_committee_attendance'
    id = Column(Integer, primary_key=True)
    fid = Column(ForeignKey('freshman_accounts.id'), nullable=False)
    meeting_id = Column(ForeignKey('committee_meetings.id'), nullable=False)

    def __init__(self, fid, meeting_id):
        self.fid = fid
        self.meeting_id = meeting_id


class TechnicalSeminar(db.Model):
    __tablename__ = 'technical_seminars'
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
    __tablename__ = 'member_seminar_attendance'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    seminar_id = Column(ForeignKey('technical_seminars.id'), nullable=False)

    def __init__(self, uid, seminar_id):
        self.uid = uid
        self.seminar_id = seminar_id


class FreshmanSeminarAttendance(db.Model):
    __tablename__ = 'freshman_seminar_attendance'
    id = Column(Integer, primary_key=True)
    fid = Column(ForeignKey('freshman_accounts.id'), nullable=False)
    seminar_id = Column(ForeignKey('technical_seminars.id'), nullable=False)

    def __init__(self, fid, seminar_id):
        self.fid = fid
        self.seminar_id = seminar_id


class MajorProject(db.Model):
    __tablename__ = 'major_projects'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    uid = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)
    description = Column(Text)
    active = Column(Boolean, nullable=False)
    status = Column(Enum('Pending', 'Passed', 'Failed',
                         name="major_project_enum"),
                    nullable=False)

    def __init__(self, uid, name, desc):
        self.uid = uid
        self.date = datetime.now()
        self.name = name
        self.description = desc
        self.status = 'Pending'
        self.active = True


class HouseMeeting(db.Model):
    __tablename__ = 'house_meetings'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    active = Column(Boolean, nullable=False)

    def __init__(self, hm_date):
        self.date = hm_date
        self.active = True


class MemberHouseMeetingAttendance(db.Model):
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


class FreshmanHouseMeetingAttendance(db.Model):
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


class CurrentCoops(db.Model):
    __tablename__ = 'current_coops'
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), nullable=False)
    date_created = Column(Date, nullable=False)
    semester = Column(Enum('Fall', 'Spring', name="co_op_enum"), nullable=False)

    def __init__(self, uid, semester):
        self.uid = uid
        self.active = True
        self.date_created = datetime.now()
        self.semester = semester


class OnFloorStatusAssigned(db.Model):
    __tablename__ = 'onfloor_datetime'
    uid = Column(String(32), primary_key=True)
    onfloor_granted = Column(DateTime, primary_key=True)

    def __init__(self, uid, time_granted):
        self.uid = uid
        self.onfloor_granted = time_granted


class Conditional(db.Model):
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
    s_evaluation = Column(ForeignKey('spring_evals.id'))
    i_evaluation = Column(ForeignKey('freshman_eval_data.id'))

    def __init__(self, uid, description, due, s_eval=None, i_eval=None):
        self.uid = uid
        self.description = description
        self.date_due = due
        self.date_created = datetime.now()
        self.status = "Pending"
        self.active = True
        self.s_evaluation = s_eval
        self.i_evaluation = i_eval


class EvalSettings(db.Model):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    housing_form_active = Column(Boolean)
    intro_form_active = Column(Boolean)
    site_lockdown = Column(Boolean)

    def __init__(self):
        self.housing_form_active = True
        self.intro_form_active = True
        self.site_lockdown = False


class SpringEval(db.Model):
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


class InHousingQueue(db.Model):
    __tablename__ = 'in_housing_queue'
    uid = Column(String(32), primary_key=True)

http_enum = Enum('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH', name='http_enum')

class UserLog(db.Model):
    __tablename__ = 'user_log'
    id = Column(Integer, primary_key=True)
    ipaddr = Column(postgresql.INET, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    uid = Column(String(32), nullable=False)
    method = Column(http_enum)
    blueprint = Column(String(32), nullable=False)
    path = Column(String(128), nullable=False)
    description = Column(String(128), nullable=False)

    def __init__(self, ipaddr, user, method, blueprint, path, description):
        self.ipaddr = ipaddr
        self.timestamp = datetime.now()
        self.uid = user
        self.method = method
        self.blueprint = blueprint
        self.path = path
        self.description = description
