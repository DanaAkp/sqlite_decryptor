from flask import jsonify, request, abort
from flask_admin.contrib.sqla import ModelView

from app.app import app, admin, database_information
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


@app.route('/')
def hello_world():
    return 'Hello World!'


# TODO какие сущности есть, массив классов, которые есть (get_entity_list)
@app.route('/models', methods=['GET'])
def get_entity_list():
    entities = database_information.classes.keys()
    return jsonify(json_list=entities)


# TODO get_entity_inf
@app.route('/models/<string:entity_name>', methods=['GET'])
def get_entity(entity_name):
    entity = database_information.classes[entity_name]
    return jsonify(entity)


# TODO метод, который add
@app.route('/models/<string:entity_name>/create', methods=['POST'])
def create_entity(entity_name):
    entity = database_information.classes[entity_name]
    return jsonify({})


# TODO edit entity
# TODO delete entity


def check_body_request(fields):
    if not request.json:
        abort(400, 'Request body is required.')
    for field in fields:
        if field not in request.json:
            abort(400, f'Field {field.replace("_", " ")} is required.')


@app.route('/sqlite_decrypter/api/save_encrypted_db_file', methods=['GET'])
def save_encrypted_db_file():
    """Возвращает зашифрованную копию текущей активной базы данных."""
    aes = AES(database_information._password)
    encrypted_db = aes.encrypt(database_information.database_file)
    return jsonify({})  # TODO вернуть зишифрованный файл


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
        abort(400, ex.args[0])


@app.route('/sqlite_decrypter/api/clear_current_db_file', methods=['DELETE'])
def clear_current_db_file():
    """Удаление информации о текущей заугрженной в систему базе данных."""
    database_information.clear()
    return jsonify({'result': True})


@app.route('/sqlite_decrypter/api/encrypt_db_file', methods=['PUT'])  # TODO PUT, POST or GET
def encrypt_db_file():
    """Шифрует чистый (незашифрованный) файл SQLite базы данных и возвращает массив байт зашифрованного файла."""
    check_body_request(['database_file', 'password'])
    try:
        aes = AES(request.json['password'].encode('utf-8'))
        encrypted_file = aes.encrypt(bytes.fromhex(request.json['database_file']))
        return jsonify({'encrypted_file': encrypted_file.hex()})

    except Exception as ex:
        abort(400, ex.args[0])  # TODO другой номер
