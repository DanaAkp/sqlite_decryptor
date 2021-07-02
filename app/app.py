import os
from flask import Flask
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from flask_admin import Admin, AdminIndexView, expose

app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))

# db = SQLAlchemy(app)
db = create_engine('sqlite:///develop.db')
Base = automap_base()
Base.prepare(db, reflect=True)
classes = Base.classes


class AdminView(AdminIndexView):
    def is_visible(self):
        return False

    @expose('/')
    def index(self):
        return 'index.html'


admin = Admin(app, url='/test', index_view=AdminView(), name='My app')
session = scoped_session(sessionmaker(bind=db))

for class_entity in classes:
    admin.add_view(ModelView(class_entity, session))


@app.route('/')
def hello_world():
    return 'Hello World!'


