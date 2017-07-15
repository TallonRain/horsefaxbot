from ..core import HorseFaxBot
from horsefax.telegram.services.command import Command
from horsefax.telegram.services.chat import ChatService


class PingModule:
    def __init__(self, bot: HorseFaxBot):
        self.bot = bot
        # TODO: Some way to undo this at the module level.
        self.bot.commands.register_handler('ping', self.ping)

    def ping(self, command: Command):
        self.bot.chat.message(command.message.chat, "`Pong!`", parsing=ChatService.ParseMode.MARKDOWN)
