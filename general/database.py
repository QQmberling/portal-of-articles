from general import db


def create_db():
    tables = db.engine.table_names()  # db.metadata.tables.keys() альтернатива
    if len(tables) == 0:
        db.create_all()
        print('Таблицы успешно созданы')
        return True
    else:
        return False


def drop_db():
    db.drop_all()
    print('Все таблицы успешно удалены')

    #
    # db_is_created = os.path.exists(f'general/{DBNAME}')
    # if not db_is_created:
    #     db.create_all()
