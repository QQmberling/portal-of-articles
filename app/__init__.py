from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)

    login_manager.login_view = app.config['LOGIN_VIEW']
    login_manager.login_message = app.config['LOGIN_MESSAGE']
    login_manager.login_message_category = app.config['LOGIN_MESSAGE_CATEGORY']
    login_manager.init_app(app)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    from .api import blueprint, np_user, np_art, np_comm
    api_ = Api(blueprint,
               doc='/docs/',
               authorizations=app.config['AUTHORIZATIONS'],
               description='<h3>This API allows to interact with website and deal with everything what you can do directly at html pages.</h3>',
               )
    api_.add_namespace(np_user)
    api_.add_namespace(np_art)
    api_.add_namespace(np_comm)
    app.register_blueprint(blueprint)

    return app
