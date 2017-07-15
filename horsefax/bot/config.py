from configparser import ConfigParser

_parser = ConfigParser()
_parser.read('horsefax.conf')

token = _parser['Telegram']['token']
