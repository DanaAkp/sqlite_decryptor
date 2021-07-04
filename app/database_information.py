from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session


class DatabaseInformation:
    def __init__(self):
        self._session = None
        self._file_database = None
        self._password = None
        self.classes = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, file_db, password):
        self._password = password
        self._file_database = file_db
        db = create_engine(file_db)
        Base = automap_base()
        Base.prepare(db, reflect=True)
        self.classes = Base.classes

        session = scoped_session(sessionmaker(bind=db))
        self._session = session

