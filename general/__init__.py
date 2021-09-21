import datetime
import os

from dotenv import load_dotenv
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

load_dotenv()  # Теперь можно вытаскивать переменные из .env с помощью os.getenv('NAME_KEY')

TIMEZONE = datetime.timezone(datetime.timedelta(hours=3))  # Таймзона Москвы
MAX_CONTENT_LENGTH = 1024 * 1024
DBNAME = 'blog.db'
PROFILE_PIC_NAME = 'Profile_pic_'  # Начало для названия картинки аватара. Пример: Profile_pic_1 - аватар первого польз.
AVATAR_SIZE_MAX = (400, 400)  # Размер аватара для профиля
AVATAR_SIZE_MIN = (250, 250)  # Размер аватара для страничек типа authors или post/detail

app = Flask(__name__)
app.secret_key = os.getenv('KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DBNAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
manager = LoginManager(app)
manager.login_view = 'login_form'
manager.login_message = 'Необходимо авторизоваться.'
manager.login_message_category = 'danger'

ROOT_MAIN_PICTURES = os.path.join(app.root_path, 'static/profile_pics/')
ROOT_OTHER_PICTURES = os.path.join(app.root_path, 'static/other_profile_pics/')

from general import classes, routes