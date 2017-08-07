from enum import Enum
import horsefax.bot.config as config
from pony.orm import *
from pony.orm.dbapiprovider import StrConverter


class EnumConverter(StrConverter):
    def validate(self, val):
        if not isinstance(val, Enum):
            raise ValueError(f"Must be an Enum.  Got {type(val)}")
        return val

    def py2sql(self, val):
        return val.name

    def sql2py(self, value):
        # Any enum type can be used, so py_type ensures the correct one is used to create the enum instance
        return self.py_type[value]


db = Database()


def prepare_db():
    db.bind(config.db_provider, **config.db_params)
    db.provider.converter_classes.append((Enum, EnumConverter))
    db.generate_mapping(create_tables=True)
