import pytest
from app.database_information import DatabaseInformation
from app.aes.aes import AES

db_info = DatabaseInformation()
password = b'1234567890123456'
aes = AES(password)
new_col = {'column_name': 'new_col', 'column_type': 'str'}


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


def test_add_column(upload_db):
    pass
