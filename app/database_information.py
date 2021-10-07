from flask import jsonify
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session


class DatabaseInformation:
    def __init__(self):
        self._session = None
        self._database_file = None
        self._password = None
        self.db = None
        self.Base = None

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
        self.Base = automap_base()
        self.Base.prepare(self.db, reflect=True)

        session = scoped_session(sessionmaker(bind=self.db))

        self._session = session

    @property
    def database_file(self):
        with open('test.db', 'rb') as file:
            return file.read()

    def get_attributes(self, entity_name: str):
        """Возвращает набор полей данной сущности"""
        columns = list(map(lambda x: x, self.db.dialect.get_columns(self.db.connect(), entity_name)))
        return sorted(list(map(lambda x: x.get('name'), columns)))

    def get_primary_key(self, entity_name: str):
        columns = self.Base.metadata.tables.get(entity_name).primary_key.columns.keys()
        if columns and len(columns) == 1:
            return {'primary_key': columns[0]}
        else:
            return list(self.db.table_names())

    def clear(self):
        self._session = None
        self._password = None
        self._database_file = None
        self.db = None
        self.Base = None

    def get_entity(self, entity_name):
        return self.Base.metadata.tables.get(entity_name)
