import os
from app import create_app
from app.database import create_db


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()
create_db()
app.run()
