from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session


class DatabaseInformation:
    def __init__(self):
        self._session = None
        self._database_file = None
        self._password = None
        self.classes = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        db_file, password = value
        self._password = password
        self._database_file = db_file
        # TODO добавить без создания файла или удалять его после использования
        with open('test.db', 'wb') as file:
            file.write(db_file)

        self.db = create_engine('sqlite:///test.db')
        Base = automap_base()
        Base.prepare(self.db, reflect=True)
        self.classes = Base.classes

        session = scoped_session(sessionmaker(bind=self.db))
        self._session = session

    @property
    def database_file(self):
        with open('test.db', 'rb') as file:
            return file.read()

    def get_entity_information(self, entity_name: str):
        """Возвращает набор полей данной сущнос"""
        columns = list(map(lambda x: x, self.classes[entity_name].__dict__['__table__'].columns))
        return sorted(list(map(lambda x: x.name, columns)))

    def get_primary_key(self, entity_name:str):
        columns = self.classes[entity_name].__dict__['__table__'].columns
        for i in columns:
            if i.primary_key:
                return i

    def clear(self):
        self._session = None
        self.classes = None
        self._password = None
        self._database_file = None
