from ..core import HorseFaxBot, ModuleTools, BaseModule
from horsefax.telegram.services.command import Command


class CuteModule(BaseModule):
    def __init__(self, bot: HorseFaxBot, util: ModuleTools):
        self.bot = bot
        self.util = util
        self.util.register_command('cute', self.cute)

    def cute(self, command: Command):
        self.bot.message(command.message.chat, "https://derpicdn.net/img/view/2012/1/2/0.jpg")
