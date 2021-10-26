"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Base config."""
    SECRET_KEY = environ.get('SECRET_KEY') or 'YOU SHALL NOT GUESS'
    ADMIN_PSW = environ.get('ADMIN_PSW') or 'admin'
    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = environ.get('DEVELOPMENT_DATABASE_URL') or 'sqlite:///' + path.join(basedir, 'data-dev.db')
    TESTING = True


class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('TESTING_DATABASE_URL') or 'sqlite://'


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or 'sqlite:///' + path.join(basedir, 'data.db')
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}



