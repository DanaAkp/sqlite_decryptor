from flask import render_template

from app.app import app


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/sqlite_decrypter/<string:entity_name>')
def page_entity_by_name(entity_name):
    return render_template('list.html', entity_name=entity_name)


@app.route('/sqlite_decrypter/create/<string:entity_name>')
def page(entity_name):
    return render_template('create.html', entity_name=entity_name)


@app.route('/sqlite_decrypter/edit/<string:entity_name>/<entity_id>')
def page_edit(entity_name, entity_id):
    return render_template('edit.html', entity_name=entity_name, entity_id=entity_id)


@app.route('/sqlite_decrypter/add_new_table')
def add_new_table():
    return render_template('add_new_table.html')
