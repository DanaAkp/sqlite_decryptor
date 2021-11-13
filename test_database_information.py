import pytest
import pytest_dependency
from app.database_information import DatabaseInformation
from app.aes.aes import AES

db_info = DatabaseInformation()
password = b'1234567890123456'
aes = AES(password)
new_col = {'column_name': 'new_col', 'column_type': 'str'}
table_name = 'roles'
new_table = {'table_name': 'new_table',
             'columns': [{'column_name': 'id', 'column_type': 'int', 'primary_key': 'id', 'nullable': ''},
                         {'column_name': 'name', 'column_type': 'str', 'primary_key': '', 'nullable': False}]}
new_record = [4, 'role 4']


@pytest.fixture
def upload_db():
    with open('example.txt') as file:
        decrypted_file = aes.decrypt(bytes.fromhex(file.read()))
    db_info.session = (decrypted_file, password)
    tables = db_info.get_tables()
    for i in tables:
        print(i)
        print(db_info.get_primary_key(i))
        print(db_info.get_columns(i))
        print()


def test_get_primary_key(upload_db):
    assert db_info.get_primary_key(table_name)


@pytest.mark.dependency
def test_add_column():
    pytest.columns = db_info.get_columns(table_name)
    db_info.add_column(table_name=table_name, json_data=new_col)
    assert db_info.get_columns(table_name) == pytest.columns + [new_col.get('column_name')]


@pytest.mark.dependency(depends=['test_add_column'])
def test_remove_column():
    db_info.delete_column(table_name=table_name, column=new_col.get('column_name'))
    assert pytest.columns == db_info.get_columns(table_name)


@pytest.mark.dependency
def test_add_table():
    pytest.tables = db_info.get_tables()
    db_info.add_table(new_table['table_name'], new_table['columns'])
    assert db_info.get_tables() == [new_table['table_name']] + pytest.tables


@pytest.mark.dependency(depends=['test_add_table'])
def test_remove_table():
    db_info.delete_table(new_table['table_name'])
    assert db_info.get_tables() == pytest.tables


@pytest.mark.dependency
def test_add_record():
    db_info.add_row(table_name=table_name, values=new_record)
    assert db_info.get_row(table_name, 4)
