from flask import jsonify, request, abort

from app.app import app, database_information
from app.aes.aes import AES
from app.utils import check_body_request, serializer
from sqlalchemy import Table, Column, Integer, String, Text, Date, DateTime, Boolean, BINARY


@app.route('/models', methods=['GET'])
def get_entity_list():
    """Возвращает список сущностей базы данных."""
    if database_information.classes is None:
        abort(500, 'Database file does not uploaded yet.')
    entities = database_information.db.table_names()
    return jsonify(json_list=entities)


@app.route('/models', methods=['POST'])
def create_table():
    if not request.is_json:
        abort(400, 'Request must include json.')
    check_body_request(['table_name', 'columns'])
    json_data = request.get_json()
    column_types = {'int': Integer, 'str': String, 'date_time': DateTime, 'date': Date, 'bool': Boolean,
                    'bin': BINARY, 'text': Text}
    new_table = Table(json_data.get('table_name'), database_information.Base.metadata)
    for i in json_data.get('columns'):
        if not all([i.get('column_name'), i.get('column_type'), i.get('primary_key'), i.get('nullable')]):
            abort(400, 'Columns includes name, type, primary key and nullable.')
        if (sql_type := column_types.get(i.get('column_type'))) is None:
            abort(400, f'Type must be {list(column_types.keys())}.')
        col = Column(i.get('column_name'), sql_type,
                     primary_key=i.get('primary_key'), nullable=i.get('nullable'))
        new_table.append_column(col)
    new_table.create(bind=database_information.db)
    return {'result': True}


@app.route('/models/<string:name_table>', methods=['DELETE'])
def delete_table(name_table):
    if not database_information.db.has_table(name_table):
        abort(404, f'Not found table "{name_table}"')
    table = database_information.Base.metadata.tables.get(name_table)
    table.drop(bind=database_information.db)
    return {'result': True}


@app.route('/models/attributes/<string:entity_name>', methods=['GET'])
def get_entity(entity_name):
    """Возвращает список аттрибутов данной сущности."""
    attributes = database_information.get_entity_information(entity_name)
    return jsonify(json_list=attributes)


@app.route('/models/primary_key/<string:entity_name>', methods=['GET'])
def get_primary_key(entity_name):
    """Возвращает название ключевого поля."""
    return jsonify({'primary_key': database_information.get_primary_key(entity_name).name})


@app.route('/models/<string:entity_name>', methods=['GET'])
def get_records(entity_name):
    """Возвращает список записей для данной сущности. """
    entity = database_information.classes[entity_name]
    attributes = database_information.get_entity_information(entity_name)
    records = database_information.session.query(entity).all()
    buf = list(map(lambda x: serializer(x, attributes), records))
    return jsonify(json_list=buf)


@app.route('/models/<string:entity_name>/<entity_id>', methods=['GET'])
def get_object(entity_name, entity_id):
    entity = database_information.classes[entity_name]
    primary_key = database_information.get_primary_key(entity_name)
    object_ = database_information.session.query(entity).filter(primary_key == entity_id).first()
    return jsonify(serializer(object_, database_information.get_entity_information(entity_name)))


@app.route('/models/<string:entity_name>', methods=['POST'])
def create_entity(entity_name):
    attributes = database_information.get_entity_information(entity_name)
    check_body_request(attributes)

    entity = database_information.classes[entity_name]
    new_object = entity()
    for i in attributes:
        try:
            setattr(new_object, i, request.json[i])
        except:
            continue
    database_information.session.add(new_object)
    database_information.session.commit()

    return jsonify(serializer(new_object, attributes)), 201


@app.route('/models/<string:entity_name>/<int:entity_id>', methods=['PUT'])
def update_entity(entity_name, entity_id):
    attributes = database_information.get_entity_information(entity_name)
    check_body_request(attributes)
    entity = database_information.classes[entity_name]
    object_ = database_information.session.query(entity).filter_by(id=entity_id).first()
    for i in attributes:
        try:
            setattr(object_, i, request.json[i])
        except:
            continue
    database_information.session.commit()

    return jsonify(serializer(object_, attributes))


@app.route('/models/<string:entity_name>/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_name, entity_id):
    entity = database_information.classes[entity_name]
    object_ = database_information.session.query(entity).filter_by(id=entity_id).first()
    database_information.session.delete(object_)
    database_information.session.commit()
    return jsonify({'result': True})


# region SQLDecrypter
@app.route('/sqlite_decrypter/api/save_encrypted_db_file', methods=['GET'])
def save_encrypted_db_file():
    """Возвращает зашифрованную копию текущей активной базы данных."""
    aes = AES(database_information._password.encode('utf-8'))
    encrypted_db = aes.encrypt(database_information.database_file)
    return jsonify({'encrypted_file': encrypted_db.hex()})


@app.route('/sqlite_decrypter/api/upload_encrypted_db_file', methods=['POST'])
def upload_encrypted_db_file():
    """Загружает и расшифровывает файл базы данных для дальнейшей работы с ней."""
    check_body_request(['database_file', 'password'])
    # TODO проверять пароль
    try:
        aes = AES(request.json['password'].encode('utf-8'))
        decrypted_file = aes.decrypt(bytes.fromhex(request.json['database_file']))
        database_information.session = (decrypted_file, request.json['password'])
        return jsonify({'result': True})
    except Exception as ex:
        abort(400, ex.args[0])  # TODO другой номер


@app.route('/sqlite_decrypter/api/clear_current_db_file', methods=['DELETE'])
def clear_current_db_file():
    """Удаление информации о текущей заугрженной в систему базе данных."""
    database_information.clear()
    return jsonify({'result': True})


@app.route('/sqlite_decrypter/api/encrypt_db_file', methods=['POST'])  # TODO POST
def encrypt_db_file():
    """Шифрует чистый (незашифрованный) файл SQLite базы данных и возвращает массив байт зашифрованного файла."""
    check_body_request(['database_file', 'password'])
    try:
        aes = AES(request.json['password'].encode('utf-8'))
        encrypted_file = aes.encrypt(bytes.fromhex(request.json['database_file']))
        return jsonify({'encrypted_file': encrypted_file.hex()})

    except Exception as ex:
        abort(400, ex.args[0])  # TODO другой номер
# endregion
