from flask import jsonify, request, abort
from flask_restx import Resource

from app.app import api, app, db_info
from app.aes.aes import AES
from app.utils import check_body_request, serializer
from sqlalchemy import Table, Column, Integer, String, Text, Date, DateTime, Boolean, BINARY


column_types = {'int': Integer, 'str': String, 'date_time': DateTime, 'date': Date, 'bool': Boolean,
                'bin': BINARY, 'text': Text}


@api.route('/models', methods=['GET', 'POST'])
@api.route('/models/<string:name_table>', methods=['DELETE'])
class ModelsController(Resource):
    def get(self):
        """Возвращает список сущностей базы данных."""
        if db_info.db is None:
            abort(500, 'Database file does not uploaded yet.')
        entities = db_info.db.table_names()
        return jsonify(json_list=entities)

    def post(self):
        """Метод для создания новых таблиц."""
        check_body_request(['table_name', 'columns'])
        json_data = request.get_json()
        new_table = Table(json_data.get('table_name'), db_info.Base.metadata)
        for i in json_data.get('columns'):
            if not all([i.get('column_name'), i.get('column_type'), i.get('primary_key'), i.get('nullable')]):
                abort(400, 'Columns includes name, type, primary key and nullable.')
            if (sql_type := column_types.get(i.get('column_type'))) is None:
                abort(400, f'Type must be {list(column_types.keys())}.')
            col = Column(i.get('column_name'), sql_type,
                         primary_key=i.get('primary_key'), nullable=i.get('nullable'))
            new_table.append_column(col)
        new_table.create(bind=db_info.db)
        return {'result': True}

    def delete(self, name_table):
        """Метод для удаления таблиц."""
        if not db_info.db.has_table(name_table):
            abort(404, f'Not found table "{name_table}"')
        table = db_info.Base.metadata.tables.get(name_table)
        table.drop(bind=db_info.db)
        return {'result': True}


@api.route('/models/<string:entity_name>', methods=['GET', 'POST'])
class RecordsController(Resource):
    def get(self, entity_name):
        """Возвращает список записей для данной сущности. """
        entity = db_info.get_entity(entity_name)
        attributes = db_info.get_attributes(entity_name)
        records = db_info.session.query(entity).all()
        buf = list(map(lambda x: serializer(x, attributes), records))
        return jsonify(json_list=buf)

    def post(self, entity_name):
        """Метод для добавления новой записи в таблицу."""
        attributes = db_info.get_attributes(entity_name)
        check_body_request(attributes)

        entity = db_info.Base.classes[entity_name]
        new_object = entity()
        for i in attributes:
            try:
                setattr(new_object, i, request.json[i])
            except:
                continue
        db_info.session.add(new_object)
        db_info.session.commit()
        # entity = db_info.get_entity(entity_name)
        # at = dict()
        # for i in attributes:
        #     at[i] = request.json[i]
        # ins = entity.insert().values(at)
        # db_info.db.execute(ins)

        return serializer(new_object, attributes), 201


@api.route('/models/attributes/<string:entity_name>', methods=['GET'])
class AttributesController(Resource):
    def get(self, entity_name):
        """Возвращает список аттрибутов данной сущности."""
        attributes = db_info.get_attributes(entity_name)
        return jsonify(json_list=attributes)


@api.route('/models/primary_key/<string:entity_name>', methods=['GET'])
class PrimaryKeyController(Resource):
    def get(self, entity_name):
        """Возвращает название ключевого поля."""
        return db_info.get_primary_key(entity_name)


@api.route('/models/<string:entity_name>/<entity_id>', methods=['GET', 'PUT', 'DELETE'])
class ObjectEntityController(Resource):
    def get(self, entity_name, entity_id):
        """Метод для получения записи таблицы по ее идентификатору."""
        entity = db_info.get_entity(entity_name)
        primary_key = db_info.get_primary_key(entity_name)
        object_ = db_info.session.query(entity).filter(primary_key == entity_id).first()
        return serializer(object_, db_info.get_attributes(entity_name))

    def put(self, entity_name, entity_id):
        """Метод для обновления записи таблицы по ее идентификатору."""
        attributes = db_info.get_attributes(entity_name)
        check_body_request(attributes)
        entity = db_info.get_entity(entity_name)
        primary_key = db_info.get_primary_key(entity_name)
        object_ = db_info.session.query(entity).filter(primary_key == entity_id).first()
        for i in attributes:
            try:
                setattr(object_, i, request.json[i])
            except:
                continue
        db_info.session.commit()

        return serializer(object_, attributes)

    def delete(self, entity_name, entity_id):
        """Метод для удаления записи таблицы по ее идентификатору."""
        entity = db_info.get_entity(entity_name)
        primary_key = db_info.get_primary_key(entity_name)
        object_ = db_info.session.query(entity).filter(primary_key == entity_id).first()
        db_info.session.delete(object_)
        db_info.session.commit()
        return {'result': True}


@api.route('/sql_decrypter')
class SQLDecrypter(Resource):
    def get(self):
        """Возвращает зашифрованную копию текущей активной базы данных."""
        aes = AES(db_info._password.encode('utf-8'))
        encrypted_db = aes.encrypt(db_info.database_file)
        return {'encrypted_file': encrypted_db.hex()}

    def post(self):
        """Загружает и расшифровывает файл базы данных для дальнейшей работы с ней."""
        check_body_request(['database_file', 'password'])
        try:
            aes = AES(request.json['password'].encode('utf-8'))
            decrypted_file = aes.decrypt(bytes.fromhex(request.json['database_file']))
            db_info.session = (decrypted_file, request.json['password'])
            return {'result': True}
        except Exception as ex:
            abort(400, ex.args[0])

    def delete(self):
        """Удаление информации о текущей заугрженной в систему базе данных."""
        db_info.clear()
        return {'result': True}


@api.route('/sql_encryptor')
class SQLEncryptor(Resource):
    def post(self):
        """Шифрует чистый (незашифрованный) файл SQLite базы данных и возвращает массив байт зашифрованного файла."""
        check_body_request(['database_file', 'password'])
        try:
            aes = AES(request.json['password'].encode('utf-8'))
            encrypted_file = aes.encrypt(bytes.fromhex(request.json['database_file']))
            return {'encrypted_file': encrypted_file.hex()}

        except Exception as ex:
            abort(400, ex.args[0])


@api.route('/columns/<string:table_name>', methods=['POST'])
@api.route('/columns/<string:table_name>/<string:column_name>', methods=['PUT', 'DELETE'])
class ColumnsController(Resource):
    def post(self, table_name):
        # TODO проверить
        """Метод для добавления новых колонок в таблицу"""
        if not db_info.db.has_table(table_name):
            abort(400, f'Table {table_name} not found.')

        check_body_request(['column_name', 'column_type'])
        json_data = request.get_json()

        if (sql_type := column_types.get(json_data.get('column_type'))) is None:
            abort(400, f'Type must be {list(column_types.keys())}.')

        new_column = Column(json_data.get('column_name'), sql_type)
        table = db_info.get_entity(table_name)
        table.append_column(new_column)
        return {'result': True}, 201

    # TODO
    # def put(self, table_name, column_name):
    #     """Метод для изменения колонки таблицы."""
    #     if not database_information.db.has_table(table_name):
    #         abort(400, f'Table {table_name} not found.')
    #
    #     check_body_request(['column_name', 'column_type'])
    #     json_data = request.get_json()
    #
    #     if (sql_type := column_types.get(json_data.get('column_type'))) is None:
    #         abort(400, f'Type must be {list(column_types.keys())}.')
    #
    #     table = database_information.classes['Debtors'].__table__
    #
    #     return {'result': True}, 201

    def delete(self, table_name, column_name):
        # TODO
        """Метод для удаления колонки таблицы."""
        if not db_info.db.has_table(table_name):
            abort(400, f'Table {table_name} not found.')

        table = db_info.get_entity(table_name)
        return {'result': True}


@api.route('/database/<string:database_name>')
class DatabaseController(Resource):
    # todo
    def post(self, database_name):
        pass
