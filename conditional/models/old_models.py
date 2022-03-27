from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum, DateTime, \
    Date, Text

Base = declarative_base()

class Attendance(Base):
    __tablename__ = 'attendance'
    username = Column(String(100), nullable=False, primary_key=True)
    meeting_date = Column(Date, nullable=False, primary_key=True)
    directorship_id = Column(Integer, nullable=False, primary_key=True)


class Directorship(Base):
    __tablename__ = 'directorships'
    ID = Column(Integer, primary_key=True, nullable=False)
    directorship_name = Column(Text, nullable=False)
    directorship_head = Column(Text, nullable=False)


class Conditional(Base):
    __tablename__ = 'conditionals'
    username = Column(String(100), nullable=False, primary_key=True)
    description = Column(String(2000), nullable=False)
    deadline = Column(Date, nullable=False)
    status = Column(Enum('pending', 'pass', 'fail'), nullable=False)


class FreshmanEval(Base):
    __tablename__ = 'freshman_evals'
    username = Column(String(100), nullable=False, primary_key=True)
    packetDueDate = Column(Date, nullable=False)
    voteDate = Column(Date, nullable=False)
    numMissedSigs = Column(Integer, nullable=False)
    missedSigs = Column(String(3000), nullable=False)
    numTechSems = Column(Integer, nullable=False)
    techSems = Column(String(2000), nullable=False)
    numSocEvents = Column(Integer, nullable=False)
    socEvents = Column(String(2000), nullable=False)
    freshProjPass = Column(Integer, nullable=False)
    freshProjComments = Column(String(3000), nullable=False)
    comments = Column(String(3000), nullable=False)
    deadline = Column(Date, nullable=False)
    result = Column(Enum('pending', 'conditional', 'pass', 'fail'), nullable=False)


class HouseMeeting(Base):
    __tablename__ = 'house_meetings'
    username = Column(String(100), nullable=False, primary_key=True)
    date = Column(Date, nullable=False, primary_key=True)
    present = Column(Integer, nullable=False)
    excused = Column(Integer, nullable=False)
    comments = Column(String(2000), nullable=False)


class MajorProject(Base):
    __tablename__ = 'major_project'
    username = Column(String(100), nullable=False, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    project_directorship = Column(Text)
    project_name = Column(String(200), nullable=False, primary_key=True)
    project_description = Column(Text)
    status = Column(Enum('pending', 'pass', 'fail'), nullable=False)


class Member(Base):
    __tablename__ = 'members'
    username = Column(String(100), nullable=False, primary_key=True)
    active = Column(Integer, nullable=False)
    on_floor = Column(Integer, nullable=False)
    voting = Column(Integer, nullable=False)
    alumniable = Column(Integer, nullable=False)
    housing_points = Column(Integer, nullable=False)
    directorship_mtgs = Column(Integer, nullable=False)


class Queue(Base):
    __tablename__ = 'queue'
    username = Column(String(100), nullable=False, primary_key=True)
    timestamp = Column(DateTime, nullable=False)


class Roster(Base):
    __tablename__ = 'roster'
    year = Column(Enum('current', 'next'), nullable=False, primary_key=True)
    room_number = Column(Integer)
    roomate1 = Column(String(100), nullable=False)
    roomate2 = Column(String(100), nullable=False)


class SpringEval(Base):
    __tablename__ = 'spring_evals'
    username = Column(String(100), nullable=False, primary_key=True)
    result = Column(Enum('pending', 'conditional', 'pass', 'fail'), nullable=False)
    comments = Column(String(2000), nullable=False)
    date_added = Column(DateTime, nullable=False)


class WinterEval(Base):
    __tablename__ = 'winter_evals'
    username = Column(String(100), nullable=False, primary_key=True)
    social_attended = Column(String(2000), nullable=False)
    social_hosted = Column(String(2000), nullable=False)
    seminars_attended = Column(String(2000), nullable=False)
    seminars_hosted = Column(String(2000), nullable=False)
    projects = Column(String(2000), nullable=False)
    comments = Column(String(2000), nullable=False)
    points = Column(Integer)
