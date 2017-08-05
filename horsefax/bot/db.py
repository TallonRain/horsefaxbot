import horsefax.bot.config as config
from peewee import *
from peewee import BaseModel as PeeweeModelMetaclass
from playhouse.db_url import connect

db = connect(config.db_url)

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
    db.create_tables(_models, safe=True)

db_random_fn = fn.Rand if isinstance(db, MySQLDatabase) else fn.Random
