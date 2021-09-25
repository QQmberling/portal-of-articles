from admin.admin import admin
from general import app
from general.database import create_db

app.register_blueprint(admin, url_prefix='/admin')


if __name__ == '__main__':

    create_db()
    app.run()
