from datetime import datetime

from werkzeug.security import generate_password_hash

from admin.admin import admin
from general import app, TIMEZONE, db
from general.classes import User, UserInfo, Article
from general.database import drop_db, create_db

app.register_blueprint(admin, url_prefix='/admin')


if __name__ == '__main__':

    with open('text.txt') as file:
        text = file.read()

    drop_db()
    create_db()

    user = User(login='admin', password=generate_password_hash('admin'), date=datetime.now(TIMEZONE))
    db.session.add(user)
    db.session.commit()

    # print(type(datetime.now(TIMEZONE).strftime("%H:%M:%S - %Y:%m:%d")))
    user_info = UserInfo(id=user.id, first_name='Igor', last_name='Pershin', about='I AM NUMBER ONE')
    db.session.add(user_info)
    db.session.commit()

    article = Article(title='Standart Title', intro='Pretty Standart Intro', date=datetime.now(TIMEZONE), author_id=1, text=text)
    db.session.add(article)
    db.session.commit()

    user = User(login='not admin', password=generate_password_hash('admin'), date=datetime.now(TIMEZONE))
    db.session.add(user)
    db.session.commit()

    user_info = UserInfo(id=user.id, first_name='not Igor', last_name='not Pershin', about='I AM NUMBER TWO')
    db.session.add(user_info)
    db.session.commit()

    article = Article(title='Second Title', intro='Second Standart Intro', date=datetime.now(TIMEZONE), author_id=2, text=text, able_to_comment=False)
    db.session.add(article)
    db.session.commit()

    app.run(debug=True)
