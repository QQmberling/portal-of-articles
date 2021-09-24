from general import db


def create_db():
    db.create_all()


def drop_db():
    db.drop_all()
    print('Все таблицы успешно удалены')

    #
    # db_is_created = os.path.exists(f'general/{DBNAME}')
    # if not db_is_created:
    #     db.create_all()
