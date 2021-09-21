from werkzeug.security import generate_password_hash
from admin.admin import admin
from general import app, TIMEZONE, db
from general.database import drop_db, create_db
from general.classes import User, UserInfo, Article, Comment
from datetime import datetime

app.register_blueprint(admin, url_prefix='/admin')


if __name__ == '__main__':

    text = """Somebody once told me
The world is gonna roll me
I ain't the sharpest tool in the shed
She was lookin kinda dumb with her finger and her thumb
In the shape of an "L" on her forehead

Well the years start coming and they don't stop coming
Fed to the rules and I hit the ground running
Didn't make sense not to live for fun
Your brain gets smart but your head gets dumb.
So much to do so much to see
So what's wrong with taking the back streets?
You'll never know if you don't go
You'll never shine if you don't glow

Chorus:
Hey now you're an All Star, get your game on, go play
Hey now you're a Rock Star, get the show on, get paid
And all that glitters is gold
Only shooting stars break the mold

It's a cool place and they say it gets colder
You're bundled up now but wait 'til you get older
But the meteor men beg to differ
Judging by the hole in the satellite picture
The ice we skate is getting pretty thin
The waters getting warm so you might as well swim
My world's on fire how about yours?
That's the way I like it and I'll never get bored

Chorus

Somebody once asked could I spare some change for gas
I need to get myself away from this place
I said yep what a concept
I could use a little fuel myself
And we could all use a little change

Well the years start coming and they don't stop coming
Fed to the rules and I hit the ground running
Didn't make sense not to live for fun
Your brain gets smart but your head gets dumb
So much to do so much to see
So what's wrong with taking the back streets
You'll never know if you don't go
You'll never shine if you don't glow

Chorus"""
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



    # comment = Comment(text='my first comment', date=datetime.now(TIMEZONE), author_id=1, article_id=1)
    # db.session.add(comment)
    # db.session.commit()



    # que = db.session.query(User, UserInfo).join(UserInfo).filter(User.id == UserInfo.id).all()
    # print(que)

    # authors = db.session.query(User.id, User.login, User.picture_name, UserInfo.about, User.date).filter(User.id == UserInfo.id).all()
    # print(authors)

    app.run(debug=True)
