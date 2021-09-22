import os
from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap
from app.database_information import DatabaseInformation
from flask_restx import Api


app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))
app.static_folder = app.config['STATIC_FOLDER']


blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, doc='/doc/')

app.register_blueprint(blueprint)


bootstrap = Bootstrap(app)


database_information = DatabaseInformation()


from app.api import *
from app.views import *

