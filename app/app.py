import os
from flask import Flask, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_login import LoginManager
from app.database_information import DatabaseInformation

app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(id):
    pass
    # return User.query.get(int(id)) TODO надо сделать БД для пользователей либо убрать, потому что


database_information = DatabaseInformation()


class AdminView(AdminIndexView):
    def is_visible(self):
        return False

    @expose('/')
    def index(self):
        return self.render('index.html')


admin = Admin(app, url='/test', template_mode='bootstrap3', index_view=AdminView(url='/test'), name='My app')


