from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session


class DatabaseInformation:
    def __init__(self):
        self._session = None
        self._database_file = None
        self._password = None
        self.classes = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        db_file, password = value
        self._password = password
        self._database_file = db_file
        # TODO добавить без создания файла или удалять его после использования
        with open('test.db', 'wb') as file:
            file.write(db_file)

        self.db = create_engine('sqlite:///test.db')
        Base = automap_base()
        Base.prepare(self.db, reflect=True)
        self.classes = Base.classes

        session = scoped_session(sessionmaker(bind=self.db))
        self._session = session

    @property
    def database_file(self):
        with open('test.db', 'rb') as file:
            return file.read()

    def get_entity_information(self, entity_name: str):
        """Возвращает набор полей данной сущнос"""
        buf = ['__abstract__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__',
               '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__',
               '__mapper__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
               '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__table__', '__weakref__',
               '_sa_class_manager', '_sa_decl_prepare', '_sa_raise_deferred_config', '_sa_registry',
               'classes', 'metadata', 'prepare', 'registry']
        return set(dir(self.classes[entity_name])) - set(buf)

    def clear(self):
        self._session = None
        self.classes = None
        self._password = None
        self._database_file = None
