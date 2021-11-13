from flask import abort
from sqlalchemy import create_engine, Column, Table, Integer, String, Text, Date, DateTime, Boolean, BINARY, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session

from app.utils import serializer, check_body_request


column_types = {'int': Integer, 'str': String, 'date_time': DateTime, 'date': Date, 'bool': Boolean,
                'bin': BINARY, 'text': Text}


class DatabaseInformation:
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
        columns = self.Base.metadata.tables.get(table_name).primary_key.columns.keys()
        if columns and len(columns) == 1:
            return {'primary_key': columns[0]}
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
            if not all([i.get('column_name'), i.get('column_type'), i.get('primary_key'), i.get('nullable')]):
                abort(400, 'Columns includes name, type, primary key and nullable.')
            if (sql_type := column_types.get(i.get('column_type'))) is None:
                abort(400, f'Type must be {list(column_types.keys())}.')
            col = Column(i.get('column_name'), sql_type,
                         primary_key=i.get('primary_key'), nullable=i.get('nullable'))
            new_table.append_column(col)
        new_table.create(bind=self.db)

    def delete_table(self, table_name: str):
        metadata = MetaData(self.db, reflect=True)
        table = metadata.tables.get(table_name)
        if table is not None:
            self.Base.metadata.drop_all(self.db, [table], checkfirst=True)
    # endregion

    # region Rows
    def get_rows(self, table_name: str):
        """Возвращает все записи данной таблицы."""
        pass

    def get_row(self, table_name: str, pk: object):
        """Возвращает одну записи данной таблицы по ее ключевому полю."""
        table_name = self.get_tables(table_name)
        primary_key = self.get_primary_key(table_name)
        obj = self.session.query(table_name).filter(primary_key == pk).first()
        return serializer(obj, self.get_columns(table_name))

    def add_row(self, table_name: str, values: list):
        # todo
        entity = self.get_tables(table_name)
        attributes = self.get_columns(table_name)
        at = dict()
        # for i in attributes:
        #     at[i] = request.json[i]
        # ins = entity.insert().values(at)
        # db_info.db.execute(ins)

    def change_row(self, table_name: str, pk: object, json_data: dict):
        """Метод для изменения записи данной таблицы по ее ключевому полю."""
        attributes = self.get_columns(table_name)
        check_body_request(attributes)
        entity = self.get_tables(table_name)
        primary_key = self.get_primary_key(table_name)
        object_ = self.session.query(entity).filter(primary_key == pk).first()
        for i in attributes:
            try:
                setattr(object_, i, json_data[i])
            except:
                continue
        self.session.commit()
        # SESSION.query(students).filter(Student.Name == 'Sam').update({'AGE': None})

        return serializer(object_, attributes)

    def delete_row(self, table_name: str, pk: object):
        entity = self.get_tables(table_name)
        primary_key = self.get_primary_key(table_name)
        object_ = self.session.query(entity).filter(primary_key == pk).first()
        self.session.delete(object_)
        self.session.commit()
    # endregion
