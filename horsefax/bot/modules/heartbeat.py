from ..core import HorseFaxBot, ModuleTools, BaseModule
from horsefax.telegram.services.command import Command


class HeartbeatModule(BaseModule):
    def __init__(self, bot: HorseFaxBot, util: ModuleTools) -> None:
        self.bot = bot
        self.util = util
        self.util.register_command('heartbeat', self.thump)

    def thump(self, command: Command) -> str:
        return "Thump."
