from app import app
from flask import jsonify


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': error.description})


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'message': error.description})


@app.errorhandler(403)
def forbidden(error):
    return jsonify({'message': error.description})
