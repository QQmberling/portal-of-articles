import datetime
from os import path

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api

from config import config

TIMEZONE = datetime.timezone(datetime.timedelta(hours=3))  # Таймзона Москвы
PROFILE_PIC_NAME = 'Profile_pic_'  # Начало для названия картинки аватара. Пример: Profile_pic_1 - аватар первого польз.
MAIN_SIZE = (400, 400)  # Размер аватара для профиля
OTHER_SIZE = (250, 250)  # Размер аватара для страничек типа authors или post/detail
MIN_SIZE = (200, 200)
APP_ROOT = path.abspath(path.dirname(__file__))
db = SQLAlchemy()
bootstrap = Bootstrap()
api_ = Api()

login_manager = LoginManager()
login_manager.login_view = 'main.login_form'
login_manager.login_message = 'Необходимо авторизоваться.'
login_manager.login_message_category = 'danger'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    from .api import api as api_blueprint
    api_blueprint.register(api_)
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
