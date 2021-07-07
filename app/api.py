from flask import jsonify, request, abort
from flask_admin.contrib.sqla import ModelView

from app.app import app, admin, database_information


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': error.description})


@app.errorhandler(400)
def not_found(error):
    return jsonify({'message': error.description})


@app.errorhandler(403)
def not_found(error):
    return jsonify({'message': error.description})


@app.route('/')
def hello_world():
    return 'Hello World!'


def check_body_request(fields):
    if not request.json:
        abort(400, 'Request body is required.')
    for field in fields:
        if field not in request.json:
            abort(400, f'Field {field.replace("_", " ")} is required.')


@app.route('/sqlite_decrypter/api/save_encrypted_db_file', methods=['GET'])
def save_encrypted_db_file():
    """Возвращает зашифрованную копию текущей активной базы данных."""
    check_body_request(['database_file', 'password'])

    return jsonify({})  # TODO вернуть зишифрованный файл


@app.route('/sqlite_decrypter/api/upload_encrypted_db_file', methods=['POST'])
def upload_encrypted_db_file():
    """Загружает и расшифровывает файл базы данных для дальнейшей работы с ней."""
    check_body_request(['database_file', 'password'])
    # TODO проверять пароль
    # TODO расшифровать request.json['file_database']

    database_information.session = (bytes.fromhex(request.json['file_database']), request.json['password'])
    for entity in database_information.classes:
        admin.add_view(ModelView(entity, database_information.session))
    return jsonify({'result': True})


@app.route('/sqlite_decrypter/api/clear_current_db_file', methods=['DELETE'])
def clear_current_db_file():
    """Удаление информации о текущей заугрженной в систему базе данных."""
    admin._views.clear()
    admin._menu_links.clear()
    admin._menu.clear()
    app.blueprints.clear()
    # TODO очистить app.url_map или создать функцию create_app и использовать ее
    return jsonify({'result': True})


@app.route('/sqlite_decrypter/api/encrypt_db_file', methods=['PUT'])  # TODO PUT, POST or GET
def encrypt_db_file():
    """Шифрует чистый (незашифрованный) файл SQLite базы данных и возвращает массив байт зашифрованного файла."""
    check_body_request(['database_file', 'password'])

    return jsonify({''})
