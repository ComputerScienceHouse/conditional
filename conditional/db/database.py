from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# More global state. I'm so sorry.
engine = None
db_session = None

Base = declarative_base()


def init_db(database_url):
    global engine, db_session, Base
    engine = create_engine(database_url, convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.query = db_session.query_property()

    import db.models
    Base.metadata.create_all(bind=engine)
