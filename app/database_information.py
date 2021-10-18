from flask import jsonify, abort
from sqlalchemy import create_engine, Column, Integer, Table
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session

from app.api import column_types
from app.utils import serializer


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

    def get_columns(self, entity_name: str):
        """Возвращает набор полей данной сущности"""
        columns = list(map(lambda x: x, self.db.dialect.get_columns(self.db.connect(), entity_name)))
        return sorted(list(map(lambda x: x.get('name'), columns)))

    def add_column(self, entity_name: str, column: dict):
        if not self.db.has_table(entity_name):
            abort(400, f'Table {entity_name} not found.')

        check_body_request(['column_name', 'column_type'])
        json_data = request.get_json()

        if (sql_type := column_types.get(json_data.get('column_type'))) is None:
            abort(400, f'Type must be {list(column_types.keys())}.')

        new_column = Column(json_data.get('column_name'), sql_type)
        table = self.get_tables(entity_name)
        table.append_column(new_column)

    def delete_column(self, entity_name: str, column: str):
        if not self.db.has_table(entity_name):
            abort(400, f'Table {entity_name} not found.')

        table = self.get_tables(entity_name)

    def get_primary_key(self, entity_name: str):
        columns = self.Base.metadata.tables.get(entity_name).primary_key.columns.keys()
        if columns and len(columns) == 1:
            return {'primary_key': columns[0]}
        else:
            return list(self.db.table_names())

    def clear_db(self):
        self._session = None
        self._password = None
        self._database_file = None
        self.db = None
        self.Base = None

    def get_tables(self):
        return self.db.table_names()

    def get_table(self, entity_name):
        return self.Base.metadata.tables.get(entity_name)

    def add_table(self, name: str, columns: list):
        new_table = Table(name, self.Base.metadata)
        for i in columns:
            if not all([i.get('column_name'), i.get('column_type'), i.get('primary_key'), i.get('nullable')]):
                abort(400, 'Columns includes name, type, primary key and nullable.')
            if (sql_type := column_types.get(i.get('column_type'))) is None:
                abort(400, f'Type must be {list(column_types.keys())}.')
            col = Column(i.get('column_name'), sql_type,
                         primary_key=i.get('primary_key'), nullable=i.get('nullable'))
            new_table.append_column(col)
        new_table.create(bind=self.db)

    def delete_table(self, name: str, columns: list):
        pass

    def get_rows(self, entity: str):
        pass

    def get_row(self, entity: str, pk: object):
        entity = self.get_tables(entity)
        primary_key = self.get_primary_key(entity)
        obj = self.session.query(entity).filter(primary_key == pk).first()
        return serializer(obj, self.get_columns(entity))

    def add_row(self, entity_name: str, attr: list):
        # todo
        entity = self.get_tables(entity_name)
        attributes = self.get_columns(entity_name)
        at = dict()
        # for i in attributes:
        #     at[i] = request.json[i]
        # ins = entity.insert().values(at)
        # db_info.db.execute(ins)

    def change_row(self, entity_name: str, pk: object):
        attributes = self.get_columns(entity_name)
        check_body_request(attributes)
        entity = self.get_tables(entity_name)
        primary_key = self.get_primary_key(entity_name)
        object_ = self.session.query(entity).filter(primary_key == pk).first()
        for i in attributes:
            try:
                setattr(object_, i, request.json[i])
            except:
                continue
        self.session.commit()

        return serializer(object_, attributes)

    def delete_row(self, entity_name: str, pk: object):
        entity = self.get_tables(entity_name)
        primary_key = self.get_primary_key(entity_name)
        object_ = self.session.query(entity).filter(primary_key == pk).first()
        self.session.delete(object_)
        self.session.commit()
