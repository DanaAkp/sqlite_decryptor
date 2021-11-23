def move_table(table, source_meta, dest_meta, source, destination, session):
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


if __name__ == '__main__':
    from sqlalchemy import create_engine, MetaData, Table
    from sqlalchemy.ext.automap import automap_base
    from sqlalchemy.orm import sessionmaker, scoped_session
    from sqlalchemy import create_engine, Column, Table, Integer, String, Text, Date, DateTime, Boolean, BINARY, \
        MetaData, inspect


    # define engines/connections/metadata
    source = create_engine(f'postgresql://postgres:3sop3MK75qepDP0cLPd5@localhost/db_decryptor')
    Base = automap_base()
    Base.prepare(source, reflect=True)
    source_meta = Base.metadata

    destination = create_engine('sqlite:///:memory:')
    dest_Base = automap_base()
    dest_Base.prepare(destination, reflect=True)
    dest_meta = Base.metadata

    table_name = 'roles'

    session = scoped_session(sessionmaker(bind=destination))
    move_table(table_name, source_meta, dest_meta, source, destination, session)
    entity = dest_meta.tables.get(table_name)
    print()
