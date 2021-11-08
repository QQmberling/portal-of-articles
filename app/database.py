from app import db


def create_db():
    # tables = db.metadata.tables.keys()
    tables = db.engine.table_names()
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
