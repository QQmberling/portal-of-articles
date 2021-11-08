import os

from app import create_app, db
from app.database import create_db
from app.models import User, UserInfo, Comment, Article

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, UserInfo=UserInfo, Article=Article, Comment=Comment)


with app.app_context():
    create_db()

if __name__ == '__main__':
    app.run()
