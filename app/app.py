import os
from flask import Flask, url_for
from flask_admin import Admin, AdminIndexView, expose
from app.database_information import DatabaseInformation

app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))


database_information = DatabaseInformation()


class AdminView(AdminIndexView):
    def is_visible(self):
        return False

    @expose('/')
    def index(self):
        return self.render('index.html')


admin = Admin(app, url='/test', template_mode='bootstrap3', index_view=AdminView(url='/test'), name='My app')


