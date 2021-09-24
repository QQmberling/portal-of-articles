"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
DBNAME = 'blog.db'


class Config:
    """Base config."""
    SECRET_KEY = environ.get('SECRET_KEY')
    ADMIN_PSW = environ.get('ADMIN_PSW')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DBNAME}'


class DevConfig(Config):
    ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DBNAME}'
