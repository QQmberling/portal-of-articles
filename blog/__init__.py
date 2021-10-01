import datetime
import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

TIMEZONE = datetime.timezone(datetime.timedelta(hours=3))  # Таймзона Москвы
PROFILE_PIC_NAME = 'Profile_pic_'  # Начало для названия картинки аватара. Пример: Profile_pic_1 - аватар первого польз.
AVATAR_SIZE_MAX = (400, 400)  # Размер аватара для профиля
AVATAR_SIZE_MIN = (250, 250)  # Размер аватара для страничек типа authors или post/detail

app = Flask(__name__)
app.config.from_object('config.ProdConfig')

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
manager = LoginManager(app)
manager.login_view = 'login_form'
manager.login_message = 'Необходимо авторизоваться.'
manager.login_message_category = 'danger'

ROOT_MAIN_PICTURES = os.path.join(app.root_path, 'static/profile_pics/')
ROOT_OTHER_PICTURES = os.path.join(app.root_path, 'static/other_profile_pics/')

from blog import classes, routes