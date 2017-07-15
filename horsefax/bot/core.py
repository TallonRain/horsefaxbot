from horsefax.telegram.connections.polling import LongPollingConnection
from horsefax.telegram import Telegram
from horsefax.telegram.services.command import CommandService
from horsefax.telegram.services.chat import ChatService

import horsefax.bot.config as config


class HorseFaxBot:
    def __init__(self):
        self.telegram = Telegram(config.token, LongPollingConnection)
        self.commands = CommandService(self.telegram)
        self.chat = ChatService(self.telegram)
        self.modules = []

    def go(self):
        self.telegram.connect()
        self.load_modules()

    def load_modules(self):
        # TODO: An actual module registry
        from .modules.ping import PingModule
        self.modules = {'ping': PingModule(self)}