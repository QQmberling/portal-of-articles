import os

from flask_migrate import Migrate
from app import create_app, db
from app.models import User, UserInfo, Comment, Article

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, UserInfo=UserInfo, Article=Article, Comment=Comment)


if __name__ == '__main__':
    app.run()
