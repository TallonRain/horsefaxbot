from ..core import HorseFaxBot, ModuleTools, BaseModule
from horsefax.telegram.services.command import Command

import random


class RollModule(BaseModule):
    def __init__(self, bot: HorseFaxBot, util: ModuleTools) -> None:
        self.bot = bot
        self.util = util
        self.util.register_command('roll', self.roll)

    def roll(self, command: Command) -> str:
        if len(command.args) == 0:
            return str(random.randrange(1, 7))
        text = command.args[0]
        data = text.split('d')
        result = 0
        try:
            if len(data) < 2:
                data.insert(0, 1)
            dice = int(data[0])
            sides = int(data[1])
            if dice > 50000:
                return "Help, I can't hold this many dice"
            if sides > 50000:
                return "Help, these dice have too many sides"
            for die in range(dice):
                result += random.randrange(1, sides + 1)
        except ValueError:
            return "Invalid input, try 6 or 1d20"

        return result
