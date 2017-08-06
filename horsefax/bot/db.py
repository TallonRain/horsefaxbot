import horsefax.bot.config as config
from pony.orm import *

db = Database()


def prepare_db():
    db.bind(config.db_provider, **config.db_params)
    db.generate_mapping(create_tables=True)
