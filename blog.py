import os
from app import create_app
from app.database import create_db


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
with app.app_context():
    create_db()

if __name__ == '__main__':

    app.run()
