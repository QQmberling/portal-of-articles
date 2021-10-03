import os
from app import create_app, db
from app.database import create_db
from flask_migrate import Migrate, upgrade


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


with app.app_context():
    create_db()

if __name__ == '__main__':
    app.run()
