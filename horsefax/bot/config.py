from os import environ as _env
import urllib.parse
token = _env['TELEGRAM_TOKEN']
modules = _env['HORSEFAX_MODULES'].split(',')

db_url = urllib.parse.urlparse(_env['DATABASE_URL'])  # type: urllib.parse.ParseResult

db_name = db_url.path[1:]
db_params = {
    'user': db_url.username,
    'password': db_url.password,
    'host': db_url.hostname,
    'port': db_url.port,
}
