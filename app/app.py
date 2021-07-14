import os
from flask import Flask
from flask_bootstrap import Bootstrap
from app.database_information import DatabaseInformation


app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))
app.static_folder = app.config['STATIC_FOLDER']


bootstrap = Bootstrap(app)


database_information = DatabaseInformation()


from app.api import *
from app.views import *

