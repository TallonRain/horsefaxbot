import importlib
from typing import Union, Optional, List, cast, Callable, Any

from horsefax.telegram.connections.polling import LongPollingConnection
from horsefax.telegram import Telegram
from horsefax.telegram.types import *
from horsefax.telegram.services.command import CommandService, Command
from horsefax.telegram.services.chat import ChatService

import horsefax.bot.config as config


class HorseFaxBot:
    def __init__(self):
        self.telegram = Telegram(config.token, LongPollingConnection)
        self.commands = CommandService(self.telegram)
        self.chat = ChatService(self.telegram)
        self.modules = {}

    def go(self):
        self.telegram.connect()
        self.load_modules()

    def load_modules(self):
        for module_name in config.modules:
            module = importlib.import_module(f".modules.{module_name}", package='.'.join(__name__.split('.')[:-1]))
            things = dir(module)
            print(things)
            for thing in things:
                thing = getattr(module, thing)
                if isinstance(thing, type) and issubclass(thing, BaseModule) and thing != BaseModule:
                    print(f"loading {module_name}")
                    self.modules[module_name] = thing(self, ModuleTools(self))

    def message(self, target: Union[Chat, User, int], message: str,
                parsing: ChatService.ParseMode = ChatService.ParseMode.MARKDOWN,
                silent=False, preview=True, reply_to: Optional[Union[int, Message]] = None):
        self.chat.message(target, message, parsing=parsing, silent=silent, preview=preview, reply_to=reply_to)


class ModuleTools:
    def __init__(self, bot: HorseFaxBot):
        self.bot = bot
        self.cs_handles = {}

    def register_command(self, command: str, handler: Callable[[Command], None]):
        if command in self.cs_handles:
            self.unregister_command(command)
        handle = self.bot.commands.register_handler(command, handler)
        self.cs_handles[command] = handle
        return handle

    def unregister_command(self, command: str):
        if command in self.cs_handles:
            self.bot.commands.unregister_handler(self.cs_handles[command])
        del self.cs_handles[command]

    def unregister_all(self):
        for handle in self.cs_handles.values():
            self.bot.commands.unregister_handler(handle)
        self.cs_handles.clear()


class BaseModule:
    pass
