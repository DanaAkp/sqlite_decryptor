import datetime

from flask import abort
from sqlalchemy import create_engine, Column, Table, Integer, String, Text, Date, DateTime, Boolean, BINARY, MetaData, \
    inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session

from app.utils import serializer, check_body_request

column_types = {'int': Integer, 'str': String, 'date_time': DateTime, 'date': Date, 'bool': Boolean,
                'bin': BINARY, 'text': Text}

sqlalchemy_type = {Integer: int, String: str, Date: datetime.date, DateTime: datetime.datetime, Boolean: bool,
                   BINARY: bin, Text: str}


class DatabaseInformation:
    def __init__(self):
        self.db = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        db_file, password = value
        self._password = password
        self._database_file = db_file

        with open('test.db', 'wb') as file:
            file.write(db_file)
        self.db = create_engine('sqlite:///test.db')
        self.Base = automap_base()
        self.Base.prepare(self.db, reflect=True)

        session = scoped_session(sessionmaker(bind=self.db))
        self.inspect = inspect(self.db)

        self._session = session

    @property
    def database_file(self):
        with open('test.db', 'rb') as file:
            return file.read()

    def clear_db(self):
        self._session = None
        self._password = None
        self._database_file = None
        self.db = None
        self.Base = None

    # region Column
    def get_columns(self, table_name: str):
        """Возвращает отсортированный список полей данной таблицы"""
        columns = list(map(lambda x: x, self.db.dialect.get_columns(self.db.connect(), table_name)))
        return sorted(list(map(lambda x: x.get('name'), columns)))

    def add_column(self, table_name: str, json_data: dict):
        if (sql_type := column_types.get(json_data.get('column_type'))) is None:
            abort(400, f'Type must be {list(column_types.keys())}.')

        new_column = Column(json_data.get('column_name'), sql_type)
        column_name = new_column.compile(dialect=self.db.dialect)
        column_type = new_column.type.compile(self.db.dialect)
        self.db.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type))
        # table = self.get_table(table_name)
        # table.append_column(new_column)

    def delete_column(self, table_name: str, column: str):
        if not self.db.has_table(table_name):
            abort(400, f'Table {table_name} not found.')

        self.db.execute(f'ALTER TABLE {table_name} DROP COLUMN {column}')

    def get_primary_key(self, table_name: str):
        """Возвращает название ключевого поля, если оно есть и лист в противном случае."""
        columns = self.get_table(table_name).primary_key.columns
        if columns and len(columns) == 1:
            return columns[0]
        else:
            return list(map(lambda x: x.name, self.Base.metadata.tables.get(table_name).columns))

    # endregion

    # region Table
    def get_tables(self):
        """Возвращает список имен всех таблиц."""
        return self.db.table_names()

    def get_table(self, table_name):
        """Возвращает таблицу базы данных, с которой можно проводить операции добавления и удаления полей."""
        return self.Base.metadata.tables.get(table_name)

    def add_table(self, table_name: str, columns: list):
        """Метод для добавления новой таблицы в базу данных."""
        new_table = Table(table_name, self.Base.metadata)
        for i in columns:
            if not all([i.get('column_name'), i.get('column_type')]):
                abort(400, 'Columns includes name, type, primary key and nullable.')
            if (sql_type := column_types.get(i.get('column_type'))) is None:
                abort(400, f'Type must be {list(column_types.keys())}.')
            col = Column(i.get('column_name'), sql_type,
                         primary_key=i.get('primary_key'), nullable=i.get('nullable'))
            new_table.append_column(col)
        new_table.create(bind=self.db)
        self.Base.prepare()

    def delete_table(self, table_name: str):
        table = self.Base.metadata.tables.get(table_name)
        if table is not None:
            self.Base.metadata.drop_all(self.db, [table], checkfirst=True)

    def get_column_type(self, table_name, column_name):
        columns_table = self.inspect.get_columns(table_name)
        for c in columns_table:
            if c['name'] == column_name:
                for t in sqlalchemy_type:
                    if isinstance(c['type'], t):
                        return sqlalchemy_type[t]
    # endregion

    # region Rows
    def get_rows(self, table_name: str):
        """Возвращает все записи данной таблицы."""
        table = self.get_table(table_name)
        objects = self.session.query(table).all()
        columns = self.get_columns(table_name)
        return [serializer(obj, columns) for obj in objects]

    def get_row(self, table_name: str, pk: object):
        """Возвращает одну записи данной таблицы по ее ключевому полю."""
        table = self.get_table(table_name)
        primary_key = self.get_primary_key(table_name)
        if obj := self.session.query(table).filter(primary_key == pk).first():
            return serializer(obj, self.get_columns(table_name))
        return None

    def add_row(self, table_name: str, values: list):
        entity = self.get_table(table_name)
        ins = entity.insert().values(values)
        self.db.execute(ins)

    def change_row(self, table_name: str, pk: object, json_data: dict):
        """Метод для изменения записи данной таблицы по ее ключевому полю."""
        entity = self.get_table(table_name)
        primary_key = self.get_primary_key(table_name)
        for i in json_data:
            type_ = self.get_column_type(table_name, i)
            json_data[i] = type_(json_data[i])

        self.session.query(entity).filter(primary_key == pk).update(json_data)
        self.session.commit()

        return self.get_row(table_name, pk)

    def delete_row(self, table_name: str, pk: object):
        entity = self.get_table(table_name)
        primary_key = self.get_primary_key(table_name)
        self.session.query(entity).filter(primary_key == pk).delete()
        self.session.commit()
    # endregion
