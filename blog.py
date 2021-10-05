import os
from app import create_app, db
from app.database import create_db
from flask_migrate import Migrate, upgrade
from app.classes import User, UserInfo, Comment, Article


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
migrate = Migrate(app, db)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, UserInfo=UserInfo, Article=Article, Comment=Comment)


with app.app_context():
    create_db()

if __name__ == '__main__':
    app.run()
