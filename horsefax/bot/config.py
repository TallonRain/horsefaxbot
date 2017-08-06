from os import environ as _env
import urllib.parse

token = _env['TELEGRAM_TOKEN']
modules = _env['HORSEFAX_MODULES'].split(',')

db_url = urllib.parse.urlparse(_env['DATABASE_URL'])  # type: urllib.parse.ParseResult

db_provider = db_url.scheme
if db_provider == 'postgres':
    db_params = {
        'database': db_url.path[1:],
        'user': db_url.username,
        'password': db_url.password,
        'host': db_url.hostname,
        'port': db_url.port,
    }
elif db_provider == 'mysql':
    db_params = {
        'db': db_url.path[1:],
        'user': db_url.username,
        'passwd': db_url.password,
        'host': db_url.hostname,
        'port': db_url.port
    }
elif db_provider == 'sqlite':
    db_params = {
        'filename': db_url.hostname,
        'create_db': True
    }
