from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker

from app.database_information import DatabaseInformation


class PostgresDatabaseInformation(DatabaseInformation):
    @property
    def session(self):
        return self._session

    def connect_to_db(self, user, password, host, ):
        pass

    @session.setter
    def session(self, value):
        db_file, password = value
        self._password = password
        self._database_file = db_file
        # TODO добавить без создания файла или удалять его после использования
        self.db = create_engine(f'postgresql://postgres:3sop3MK75qepDP0cLPd5@localhost/db_decryptor')

        # with open('test.db', 'wb') as file:
        #     file.write(db_file)
        # self.db = create_engine('sqlite:///test.db')
        self.Base = automap_base()
        self.Base.prepare(self.db, reflect=True)

        session = scoped_session(sessionmaker(bind=self.db))
        self.inspect = inspect(self.db)

        self._session = session