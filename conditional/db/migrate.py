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

def getFid(name):
    from db.models import FreshmanAccount

    print(name)
    return FreshmanAccount.query.filter(FreshmanAccount.name == name).first().id

# Begin the Great Migration!
def migrate_models():

    import db.old_models as zoo
    import db.models as models

    from db.database import db_session

    print("BEGIN: freshman evals")
    # ==========

    freshman_evals = [
        {
            'username': f.username,
            'evalDate': f.voteDate,
            'projectStatus': f.freshProjPass,
            'signaturesMissed': f.numMissedSigs,
            'socialEvents': f.socEvents,
            'comments': f.comments
        } for f in zoo_session.query(zoo.FreshmanEval).all()]

    for f in freshman_evals:
        if not f['username'].startswith('f_'):
            # freshman who have completed packet and have a CSH account
            eval = models.FreshmanEvalData(f['username'], f['signaturesMissed'])

            # FIXME: Zookeeper was only pass/fail for freshman project not pending
            if f['projectStatus'] == 1:
                eval.freshman_project = 'Passed'

            eval.social_events = f['socialEvents']
            eval.other_notes = f['comments']

            db_session.add(eval)
        else:
            # freshman not yet done with packet
            account = models.FreshmanAccount(f['username'])
            account.eval_date = f['evalDate']
            db_session.add(account)

    db_session.flush()

    print("END: freshman evals")
    # ==========

    print("BEGIN: migrate committee meeting attendance")
    # ==========
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

    for cm in c_meetings:
        if cm[1][1] == 8:
            continue
        if cm[0].startswith('f_'):
            f = models.FreshmanCommitteeAttendance(
                getFid(cm[0]),
                com_meetings.index(cm[1])
            )
            db_session.add(f)
        else:
            m = models.MemberCommitteeAttendance(cm[0], com_meetings.index(cm[1]) + 1)
            db_session.add(m)

    db_session.flush()

    print("END: migrate committee meeting attendance")
    # ==========

    print("BEGIN: migrate conditionals")
    # ==========
    # TODO implements db for conditionals
    print("END: migrate conditionals")

    # ==========

    print("BEGIN: house meetings")

    h_meetings = [hm.date for hm in zoo_session.query(zoo.HouseMeeting).all()]

    for hm in h_meetings:
        m = models.HouseMeeting(hm)
        db_session.add(m)

    # TODO actually assign house meeting attendance rather than just
    # saying that house meetings happened
    print("END: house meetings")

    # ==========

    print("BEGIN: Major Projects")

    projects = [
        {
            'username': mp.username,
            'name': mp.project_name,
            'description': mp.project_description,
            'status': mp.status
        } for mp in zoo_session.query(zoo.MajorProject).all()]

    for p in projects:
        mp = models.MajorProject(
            p['username'],
            p['name'],
            p['description']
        )

        if p['status'] == 'pass':
            mp.status = 'Passed'
        if p['status'] == 'fail':
            mp.status = 'Failed'

        db_session.add(mp)
    print("END: Major Projects")

    # ==========

    db_session.flush()
    db_session.commit()
