from typing import cast
from pony.orm import *

from horsefax.telegram.services.command import Command

from ...core import HorseFaxBot, ModuleTools, BaseModule, ChatService
from ...db import db


class Madlib(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    added_by = Optional(int)
    revisions = Set(lambda: MadlibRevision)


class MadlibRevision(db.Entity):
    id = PrimaryKey(int, auto=True)
    madlib = Required(Madlib)
    content = Optional(str, nullable=True)
    by = Optional(int)


class MadlibModule(BaseModule):
    @db_session
    def __init__(self, bot: HorseFaxBot, tools: ModuleTools) -> None:
        self.bot = bot
        self.util = tools
        self.util.register_command("addcommand", self.add_command)
        self.util.register_command("removecommand", self.remove_command)
        for madlib in Madlib.select():
            self.util.register_command(madlib.name, self.handle_command)

    @db_session
    def add_command(self, command: Command):
        if len(command.args) < 2:
            return "Syntax: `/addcommand <name> <output>`"
        madlib = Madlib.get(name=command.args[0])
        if madlib is None:
            madlib = Madlib(name=command.args[0], added_by=command.message.sender.id)
            self.util.register_command(cast(str, madlib.name), self.handle_command)
        revision = MadlibRevision(madlib=madlib, content=' '.join(command.args[1:]), by=command.message.sender.id)
        return f"Created command /{madlib.name}."

    @db_session
    def handle_command(self, command: Command):
        madlib_name = command.command
        madlib = Madlib.get(name=madlib_name)
        last_revision = madlib.revisions.order_by(desc(MadlibRevision.id)).first()
        if last_revision.content is None:
            return
        self.bot.message(command.message.chat, cast(str, last_revision.content), parsing=ChatService.ParseMode.NONE)

    @db_session
    def remove_command(self, command: Command):
        if len(command.args) < 1:
            return "Syntax: `/removecommand <command>`"
        madlib_name = command.args[0]
        madlib = Madlib.get(name=madlib_name)
        if madlib is None:
            return "That command does not exist."
        else:
            MadlibRevision(madlib=madlib, content=None, by=command.message.sender.id)
            return f"Deleted command `/{madlib.name}`."
