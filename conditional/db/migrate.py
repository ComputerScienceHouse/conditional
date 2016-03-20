from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from collections import Counter

from db.database import init_db


old_engine = None
zoo_session = None
old_Base = declarative_base()

# Takes in param of SqlAlchemy Database Connection String
def free_the_zoo(zoo_url, db_url):

    init_zoo_db(zoo_url)

    init_db(db_url)

    migrate_models()

# Connect to Zookeeper
def init_zoo_db(database_url):
    global old_Base, old_engine, zoo_session
    old_engine = create_engine(database_url, convert_unicode=True)
    zoo_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=old_engine))
    import db.old_models
    old_Base.metadata.create_all(bind=old_engine)

def idToCommittee(id):
    committees = [
        'Evaluations',
        'Financial',
        'History',
        'House Improvements',
        'Opcomm',
        'R&D',
        'Social',
        'Social',
        'Chairman'
        ]
    return committees[id]
# Begin the Great Migration!
def migrate_models():

    import db.old_models as zoo
    import db.models as models

    from db.database import db_session
    #members = [m.username for m in zoo_session.query(zoo.Member).all()]
    #print(members)

    c_meetings = [
        (
            m.meeting_date,
            m.committee_id
        ) for m in zoo_session.query(zoo.Attendance).order_by(zoo.Attendance.meeting_date).all()]
    c_meetings = set(c_meetings)

    com_meetings = []
    for cm in c_meetings:
        if cm[1] == 8:
            # We don't account for Chairman Attendance
            # TODO assign arbitrarily for Spring Evals 2016
            continue
        m = models.CommitteeMeeting(idToCommittee(cm[1]), cm[0])
        db_session.add(m)
        db_session.flush()
        db_session.refresh(m)

        com_meetings.append(cm)

    c_meetings = [
        (
            m.username,
                (
                    m.meeting_date,
                    m.committee_id
                )
        ) for m in zoo_session.query(zoo.Attendance).all()]

    print(com_meetings)
    for cm in c_meetings:
        if cm[1][1] == 8:
            continue
        m = models.MemberCommitteeAttendance(cm[0], com_meetings.index(cm[1]) + 1)
        db_session.add(m)

    db_session.flush()
    db_session.commit()
    print(len(c_meetings))
