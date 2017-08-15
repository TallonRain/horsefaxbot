from pony.orm import *
import pony.orm
from typing import cast, Optional

from horsefax.telegram.services.command import Command

from ..core import HorseFaxBot, ModuleTools, BaseModule, ChatService
from ..db import db
from .tracking import TelegramUser


class PingGroup(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    added_by = pony.orm.Optional(int)
    members = Set(TelegramUser)


class CollectionModule(BaseModule):
    def __init__(self, bot: HorseFaxBot, tools: ModuleTools) -> None:
        self.bot = bot
        self.util = tools
        self.util.register_command("addgroup", self.add_group)
        self.util.register_command("joingroup", self.join_group)
        self.util.register_command("leavegroup", self.leave_group)
        self.util.register_command("removegroup", self.remove_group)
        self.util.register_command("listgroups", self.list_groups)
        self.util.register_command("ping", self.ping_group)

    @db_session
    def add_group(self, command: Command) -> str:
        if len(command.args) != 1:
            return "Syntax: `/addgroup <group name>`"
        name = command.args[0].lower()
        if PingGroup.get(name=name) is None:
            group = PingGroup(name=name, added_by=command.message.sender.id)
            return f"Created group `{group.name}`. Join it using `/joingroup {group.name}`."
        else:
            return f"The group {name} already exists. Join it using `/joingroup {group.name}`."

    @db_session
    def join_group(self, command: Command) -> str:
        if len(command.args) != 1:
            return "Syntax: `/joingroup <group name>`"
        name = command.args[0].lower()
        group = PingGroup.get(name=name)
        if group is None:
            return f"No such group: `{name}`."
        user = TelegramUser[command.message.sender.id]
        if user in group.members:
            return f"You are already a member of the group `{name}`."
        if user.username is None:
            return "You cannot join a group unless you have a set a username in Telegram."
        group.members.add(user)
        return f"Joined {group.name}, which now has {len(group.members)} member(s)."

    @db_session
    def ping_group(self, command: Command) -> Optional[str]:
        if len(command.args) < 2:
            return "Syntax: `/ping <group name> <message>`"
        message = ' '.join(command.args[1:])
        group_name = command.args[0].lower()
        group = PingGroup.get(name=group_name)
        if group is None:
            return f"The group `{group_name}` does not exist."

        if len(group.members) == 0:
            return f"The group `{group.name}` has np members."
        output = f"{' '.join(f'@{x}' for x in group.members.username if x)}: {message}"
        self.bot.message(command.message.chat, output, parsing=ChatService.ParseMode.NONE)

    @db_session
    def leave_group(self, command: Command) -> str:
        if len(command.args) != 1:
            return "Syntax: `/leavegroup <group name>`"
        name = command.args[0].lower()
        group = PingGroup.get(name=name)
        if group is None:
            return f"No such group: `{name}`."
        user = TelegramUser[command.message.sender.id]
        if user not in group.members:
            return f"You are not a member of the group `{group.name}`."
        group.members.remove(user)
        return f"Removed you from {group.name}, which now has {len(group.members)} member(s)."

    @db_session
    def remove_group(self, command: Command) -> str:
        if len(command.args) != 1:
            return "Syntax: `/removegroup <group name>`"
        name = command.args[0].lower()
        group = PingGroup.get(name=name)
        if group is None:
            return f"No such group: `{name}`."
        member_count = len(group.members)
        group.delete()
        return f"Deleted group {name}, which had {member_count} member(s)."

    @db_session
    def list_groups(self, command: Command) -> str:
        return f"The following groups exist: " \
               f"{', '.join(f'`{x.name}`' for x in PingGroup.select().order_by(PingGroup.name))}"
