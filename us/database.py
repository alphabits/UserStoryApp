from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from us.config import DB_USER, DB_PASS, DB_HOST, DB_NAME


connection_string = 'mysql+mysqldb://{0}:{1}@{2}/{3}'.format(
        DB_USER, DB_PASS, DB_HOST, DB_NAME)
engine = create_engine(connection_string, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
        bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


class DbModel(object):

    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    session = db_session

    def save(self):
        self.session.add(self)

    def delete(self):
        self.session.delete(self)

    def expunge(self):
        self.session.expunge(self)



def init_db():
    import us.models
    from us.database import Base, engine
    Base.metadata.create_all(bind=engine)
