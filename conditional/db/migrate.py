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

    tech_sems = {}

    freshman_evals = [
        {
            'username': f.username,
            'evalDate': f.voteDate,
            'projectStatus': f.freshProjPass,
            'signaturesMissed': f.numMissedSigs,
            'socialEvents': f.socEvents,
            'techSems': f.techSems,
            'comments': f.comments,
            'result': f.result
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
            eval.eval_date = f['evalDate']
            # TODO: conditional
            if f['result'] == "pass":
                eval.freshman_eval_result = "Passed"
            elif f['result'] == "fail":
                eval.freshman_eval_result = "Failed"
            else:
                eval.freshman_eval_result = "Pending"

            if f['techSems'] != None:
                t_sems = f['techSems'].split(',')
                for sem in t_sems:
                    if not sem in tech_sems:
                        tech_sems[sem] = [f['username']]
                    else:
                        tech_sems[sem].append(f['username'])
            db_session.add(eval)
        else:
            # freshman not yet done with packet
            # TODO FIXME The FALSE dictates that they are not given onfloor
            # status
            account = models.FreshmanAccount(f['username'], False)
            account.eval_date = f['evalDate']
            if f['techSems'] != None:
                t_sems = f['techSems'].split(',')
                for sem in t_sems:
                    if not sem in tech_sems:
                        tech_sems[sem] = [f['username']]
                    else:
                        tech_sems[sem].append(f['username'])
            db_session.add(eval)
            db_session.add(account)

    print("tech sems")
    tech_sems.pop('', None)
    print(tech_sems)

    i = 0
    for t_sem in tech_sems:
        # TODO FIXME: Is there a timestamp we can migrate for seminars?
        from datetime import datetime
        sem = models.TechnicalSeminar(t_sem, datetime.now())
        db_session.add(sem)
        db_session.flush()
        db_session.refresh(sem)
        print(sem.__dict__)
        for m in tech_sems[t_sem]:
            if m.startswith("f_"):
                print(sem.id)
                a = models.FreshmanSeminarAttendance(getFid(m), sem.id)
                db_session.add(a)
            else:
                a = models.MemberSeminarAttendance(m, sem.id)
                db_session.add(a)

    db_session.flush()

    print("END: freshman evals")
    # ==========

    print("BEGIN: migrate committee meeting attendance")
    # ==========
    c_meetings = [
        (
            m.meeting_date,
            m.committee_id
        ) for m in zoo_session.query(zoo.Attendance).all()]
    c_meetings = list(set(c_meetings))
    c_meetings = list(filter(lambda x: x[0] != None, c_meetings))
    c_meetings.sort(key=lambda m: m[0])

    com_meetings = []
    for cm in c_meetings:
        m = models.CommitteeMeeting(idToCommittee(cm[1]), cm[0])
        if cm[0] is None:
            # fuck man
            continue
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
        if cm[1][0] is None:
            # fuck man
            continue
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

    condits = [
        {
            "uid": c.username,
            "desc": c.description,
            "deadline": c.deadline,
            "status": c.status
        } for c in zoo_session.query(zoo.Conditional).all()]

    for c in condits:
        condit = model.Conditional(c['uid'], c['desc'], c['deadline'])
        db_session.add(condit)

    print("END: migrate conditionals")

    # ==========

    print("BEGIN: house meetings")

    h_meetings = [hm.date for hm in zoo_session.query(zoo.HouseMeeting).all()]
    h_meetings = list(set(h_meetings))
    h_meetings.sort()
    print(h_meetings)

    house_meetings = {}
    for hm in h_meetings:
        m = models.HouseMeeting(hm)
        db_session.add(m)
        db_session.flush()
        db_session.refresh(m)
        house_meetings[hm.strftime("%Y-%m-%d")] = m.id

    print(house_meetings)

    hma = [
        {
            'uid': hm.username,
            'date': hm.date,
            'present': hm.present,
            'excused': hm.excused,
            'comments': hm.comments
        } for hm in zoo_session.query(zoo.HouseMeeting).all()]

    for a in hma:
        meeting_id = house_meetings[a['date'].strftime("%Y-%m-%d")]

        status = None
        excuse = None
        if a['present'] == 1:
            status = "Attended"
        elif a['excused'] == 1:
            status = "Excused"
        else:
            status = "Absent"

        excuse = a['comments']
        if a['uid'].startswith("f_"):
            # freshman
            fhma = models.FreshmanHouseMeetingAttendance(
                getFid(a['uid']),
                meeting_id,
                excuse,
                status)
            db_session.add(fhma)
        else:
            # member
            mhma = models.MemberHouseMeetingAttendance(
                a['uid'],
                meeting_id,
                excuse,
                status)
            db_session.add(mhma)

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

    print("BEGIN: ON FLOOR")
    import util.ldap as ldap
    from datetime import datetime
    members = [m['uid'][0].decode('utf-8') for m in ldap.ldap_get_onfloor_members()]
    for m in members:
        db_session.add(models.OnFloorStatusAssigned(m, datetime.utcnow()))
    print("END: ON FLOOR")

    print("BEGIN: SPRING EVALS")
    members = [m['uid'][0].decode('utf-8') for m in ldap.ldap_get_active_members()]
    for m in members:
        db_session.add(models.SpringEval(m))
    print("END: SPRING EVALS")
    print("BEGIN: Housing Evals")
    hevals = [
        {
            'username': he.username,
            'social_attended': he.social_attended,
            'social_hosted': he.social_hosted,
            'seminars_attended': he.seminars_attended,
            'seminars_hosted': he.seminars_hosted,
            'projects': he.projects,
            'comments': he.comments
        } for he in zoo_session.query(zoo.WinterEval).all()]

    for he in hevals:
        db_session.add(
            models.HousingEvalsSubmission(
                he['username'],
                he['social_attended'],
                he['social_hosted'],
                he['seminars_attended'],
                he['seminars_hosted'],
                he['projects'],
                he['comments']))
    print("END: Housing Evals")

    # Default EvalDB Settings
    db_session.add(models.EvalSettings())

    db_session.flush()
    db_session.commit()
