from flask import jsonify, request, abort

from app.app import app, database_information
from app.aes.aes import AES


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': error.description})


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'message': error.description})


@app.errorhandler(403)
def forbidden(error):
    return jsonify({'message': error.description})


def serializer(object_to_serialize, attributes):
    result = {}
    for i in attributes:
        result.setdefault(i, str(object_to_serialize.__getattribute__(i)))
    return result


@app.route('/models', methods=['GET'])
def get_entity_list():
    """Возвращает список сущностей базы данных."""
    if database_information.classes is None:
        abort(500, 'Database file does not uploaded yet.')
    entities = database_information.classes.keys()
    return jsonify(json_list=entities)


@app.route('/models/attributes/<string:entity_name>', methods=['GET'])
def get_entity(entity_name):
    """Возвращает список аттрибутов данной сущности."""
    attributes = database_information.get_entity_information(entity_name)
    return jsonify(json_list=attributes)


@app.route('/models/<string:entity_name>', methods=['GET'])
def get_records(entity_name):
    """Возвращает список записей для данной сущности. """
    entity = database_information.classes[entity_name]
    attributes = database_information.get_entity_information(entity_name)
    records = database_information.session.query(entity).all()
    buf = list(map(lambda x: serializer(x, attributes), records))
    return jsonify(json_list=buf)


@app.route('/models/<string:entity_name>/<int:entity_id>', methods=['GET'])
def get_object(entity_name, entity_id):
    entity = database_information.classes[entity_name]
    object_ = database_information.session.query(entity).filter_by(id=entity_id).first()
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


def check_body_request(fields):
    if not request.json:
        abort(400, 'Request body is required.')
    for field in fields:
        if field not in request.json:
            abort(400, f'Field {field.replace("_", " ")} is required.')


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
