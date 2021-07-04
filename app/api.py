from flask import jsonify, request, abort
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


def check_body_request():
    if not request.json:
        abort(400, 'Request body is required.')


@app.route('/sqlite_decrypter/api/save_encrypted_db_file', methods=['GET'])
def save_encrypted_db_file():
    """Возвращает зашифрованную копию текущей активной базы данных."""
    check_body_request()
    if 'file_database' not in request.json:
        abort(400, 'Field file database is required.')

    return jsonify({})  # TODO вернуть зишифрованный файл


@app.route('/sqlite_decrypter/api/upload_encrypted_db_file', methods=['POST'])
def upload_encrypted_db_file():
    """Загружает и расшифровывает файл базы данных для дальнейшей работы с ней."""
    check_body_request()
    if 'file_database' not in request.json:
        abort(400, '')
    if 'password' not in request.json:
        abort(400, 'Field password is required.')

    for entity in database_information.classes:
        admin.add_view(entity)


@app.route('/sqlite_decrypter/api/clear_current_db_file', methods=['GET'])
def clear_current_db_file():
    """Удаление информации о текущей заугрженной в систему базе данных."""

    for entity in database_information.classes:
        admin._views.remove(entity)


@app.route('/sqlite_decrypter/api/encrypt_db_file', methods=['GET'])
def encrypt_db_file():
    """Шифрует чистый (незашифрованный) файл SQLite базы данных."""
    pass


