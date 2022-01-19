from sqlalchemy import Table, inspect, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker


def move_table(table, source_meta, dest_meta, source, destination):
    # declare tables
    src_table = Table(table, source_meta)
    dest_table = Table(table, dest_meta)

    insp = inspect(src_table)
    for col in insp.columns:
        dest_table.append_column(col)

    dest_table.create(destination, checkfirst=True)

    # select and insert loop
    sel = src_table.select()
    res = source.connect().execute(sel)
    for row in res:
        ins = dest_table.insert(row)
        destination.execute(ins)


def connect_to_db_sqlite(path_to_file):
    return create_engine(f'sqlite:///{path_to_file}')


def connect_to_db_postgresql(password, username='postgres', host='localhost', port=5432, db_name='postgres'):
    return create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db_name}')


def move_db(source):
    """Принимает на вход исходную базу данных, которую нужно зашифровать.
    Возвращает имя файла, в который она записана для дальнейшего шифрования"""
    Base = automap_base()
    Base.prepare(source, reflect=True)
    source_meta = Base.metadata

    destination = create_engine('sqlite:///:memory:')
    dest_Base = automap_base()
    dest_Base.prepare(destination, reflect=True)
    dest_meta = Base.metadata

    session = scoped_session(sessionmaker(bind=destination))

    for table_name in source.table_names():
        move_table(table_name, source_meta, dest_meta, source, destination)
    print(destination)

    file = create_engine('sqlite:///new_test.db')
    raw_connection_source = destination.raw_connection()
    raw_connection_destination = file.raw_connection()
    raw_connection_source.backup(raw_connection_destination.connection)
    raw_connection_destination.close()
    file.dispose()
    return 'new_test.db'
