import horsefax.bot.config as config
from peewee import *
from peewee import BaseModel as PeeweeModelMetaclass


db = SqliteDatabase(None)

_models = []


class RegisteringModelType(PeeweeModelMetaclass):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        if name != 'BaseModel':
            _models.append(cls)


class BaseModel(Model, metaclass=RegisteringModelType):
    class Meta:
        database = db


def prepare_db():
    db.init(config.db_path)
    db.connect()
    db.execute_sql("PRAGMA foreign_keys=ON")
    db.create_tables(_models, safe=True)
