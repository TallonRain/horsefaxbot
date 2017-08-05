import importlib
from typing import Union, Optional, Dict, List, cast, Callable, Any

from horsefax.telegram.connections.polling import LongPollingConnection
from horsefax.telegram import Telegram
from horsefax.telegram.types import *
from horsefax.telegram.services.command import CommandService, Command
from horsefax.telegram.services.chat import ChatService
from .db import prepare_db

import horsefax.bot.config as config


class HorseFaxBot:
    def __init__(self) -> None:
        self.telegram = Telegram(config.token, LongPollingConnection)
        self.commands = CommandService(self.telegram)
        self.chat = ChatService(self.telegram)
        self.modules = {}  # type: Dict[str, BaseModule]
        self._module_modules = {}  # type: Dict[str, Any]

    def go(self):
        self.prepare_modules()
        prepare_db()
        self.load_modules()
        self.telegram.connect()

    def prepare_modules(self):
        for module_name in config.modules:
            self._module_modules[module_name] = importlib.import_module(f".modules.{module_name}", package='.'.join(__name__.split('.')[:-1]))

    def load_modules(self):
        for module_name, module in self._module_modules.items():
            things = dir(module)
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
    def __init__(self, bot: HorseFaxBot) -> None:
        self.bot = bot
        self.cs_handles = {}  # type: Dict[str, Any]

    def register_command(self, command: str, handler: Callable[[Command], Optional[str]]):
        if command in self.cs_handles:
            self.unregister_command(command)
        handle = self.bot.commands.register_handler(command, lambda x: self.command_handler(handler, x))
        self.cs_handles[command] = handle
        return handle

    def command_handler(self, handler, command: Command) -> None:
        result = handler(command)
        if result is not None:
            self.bot.message(command.message.chat, result)

    def unregister_command(self, command: str) -> None:
        if command in self.cs_handles:
            self.bot.commands.unregister_handler(self.cs_handles[command])
        del self.cs_handles[command]

    def unregister_all(self) -> None:
        for handle in self.cs_handles.values():
            self.bot.commands.unregister_handler(handle)
        self.cs_handles.clear()


class BaseModule:
    pass
