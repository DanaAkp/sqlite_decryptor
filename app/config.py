import os


class Config(object):
    SECRET_KEY = ':N(4w4AV8L@6s$TA-9U4in/ZiL'

    ROOT_PATH = os.path.dirname(__file__)
    PUBLIC_PATH = 'public_html' if os.path.isdir('public_html') \
        else os.path.join(ROOT_PATH, os.path.pardir, os.path.pardir, 'web')
    DATA_PATH = os.path.join(ROOT_PATH, 'data')
    STATIC_FOLDER = os.path.join(ROOT_PATH, 'static')
    MEDIA_IMAGES_PATH = os.path.join('media', 'images')

    SQLALCHEMY_DATABASE_URI = "sqlite:///%s/develop.db" % DATA_PATH


class DevelopmentConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
