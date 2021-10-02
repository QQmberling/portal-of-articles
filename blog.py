import os
from app import create_app
from app.database import create_db


if __name__ == '__main__':

    APP = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with APP.app_context():
        create_db()
        APP.run()
