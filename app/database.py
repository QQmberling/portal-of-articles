from app import db


def create_db():
    tables = db.engine.table_names()  # db.metadata.tables.keys() альтернатива
    print('Загружены таблицы: ', tables)
    if len(tables) == 0:
        db.create_all()
        print('Таблиц в базе не обнаружено, созданы новые')
        return True
    else:
        return False


def drop_db():
    db.drop_all()
    print('Все таблицы успешно удалены')

    #
    # db_is_created = os.path.exists(f'app/{DBNAME}')
    # if not db_is_created:
    #     db.create_all()
