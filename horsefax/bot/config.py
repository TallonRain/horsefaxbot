from typing import Mapping
import os

_env = os.environ  # type: Mapping[str, str]

token = _env['TELEGRAM_TOKEN']
modules = _env['HORSEFAX_MODULES'].split(',')

db_url = _env['DATABASE_URL']
