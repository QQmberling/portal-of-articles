from admin.admin import admin
from blog import app
from blog.database import create_db

app.register_blueprint(admin, url_prefix='/admin')


if __name__ == '__main__':

    create_db()
    app.run()
