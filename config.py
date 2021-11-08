from os import environ, path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    SECRET_KEY = environ.get('SECRET_KEY') or 'YOU SHALL NOT GUESS'
    ADMIN_PSW = environ.get('ADMIN_PSW') or 'admin'
    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    UPLOAD_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
    MIN_PICTURE_SIZE = (200, 200)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BUNDLE_ERRORS = True
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

    AUTHORIZATIONS = {
        'Basic Auth': {
            'type': 'basic',
            'in': 'header',
            'name': 'Authorization'
        },
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        },
    }

    LOGIN_VIEW = 'main.login'
    LOGIN_MESSAGE = 'Необходимо авторизоваться.'
    LOGIN_MESSAGE_CATEGORY = 'danger'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"postgresql://{environ.get('DB_LOGIN')}:{environ.get('DB_PSW')}@localhost:5432/data-dev"


class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
    HEROKU_DB_URL = environ.get('HEROKU_POSTGRESQL_PUCE_URL')
    if HEROKU_DB_URL:
        HEROKU_DB_URL = HEROKU_DB_URL[:8] + 'ql' + HEROKU_DB_URL[8:]
    SQLALCHEMY_DATABASE_URI = HEROKU_DB_URL or \
                              f"postgresql://{environ.get('DB_LOGIN')}:{environ.get('DB_PSW')}@localhost:5432/data-test"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    HEROKU_DB_URL = environ.get('HEROKU_POSTGRESQL_PUCE_URL')
    if HEROKU_DB_URL:
        HEROKU_DB_URL = HEROKU_DB_URL[:8] + 'ql' + HEROKU_DB_URL[8:]
    SQLALCHEMY_DATABASE_URI = HEROKU_DB_URL or \
                              f"postgresql://{environ.get('DB_LOGIN')}:{environ.get('DB_PSW')}@localhost:5432/data-prod"


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
