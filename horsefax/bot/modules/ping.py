from ..core import HorseFaxBot, ModuleTools, BaseModule
from horsefax.telegram.services.command import Command


class PingModule(BaseModule):
    def __init__(self, bot: HorseFaxBot, util: ModuleTools):
        self.bot = bot
        self.util = util
        self.util.register_command('ping', self.ping)

    def ping(self, command: Command):
        self.bot.message(command.message.chat, "`Pong!`")
