from typing import cast
from pony.orm import *

from horsefax.telegram.services.command import Command

from ..core import HorseFaxBot, ModuleTools, BaseModule, ChatService
from ..db import db


class Collection(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    added_by = Optional(int)
    items = Set(lambda: CollectionItem)


class CollectionItem(db.Entity):
    collection = Required(Collection, index=True)
    content = Required(str)
    added_by = Optional(int)


class CollectionModule(BaseModule):
    @db_session
    def __init__(self, bot: HorseFaxBot, tools: ModuleTools) -> None:
        self.bot = bot
        self.util = tools
        self.util.register_command("newcollection", self.add_collection)
        self.util.register_command("additem", self.add_item)
        self.util.register_command("removeitem", self.remove_item)
        for collection in Collection.select():
            self.util.register_command(collection.name, self.handle_command)

    @db_session
    def add_collection(self, command: Command):
        if len(command.args) < 1:
            return "You must specify a collection name."
        if Collection.get(name=command.args[0]) is not None:
            collection = Collection(name=command.args[0], added_by=command.message.sender.id)
            self.util.register_command(cast(str, collection.name), self.handle_command)
            return f"Created collection `{collection.name}`."
        else:
            return "That collection already exists."

    @db_session
    def handle_command(self, command: Command):
        collection_name = command.command
        collection = Collection.get(name=collection_name)
        item = collection.items.random(1)
        if not item:
            return "That collection is empty."
        self.bot.message(command.message.chat, cast(str, item.content), parsing=ChatService.ParseMode.NONE)

    @db_session
    def add_item(self, command: Command):
        if len(command.args) < 2:
            return "Syntax: `/additem <collection> <thing to add>`"
        collection_name = command.args[0]
        thing = ' '.join(command.args[1:])
        collection = Collection.get(name=collection_name)
        if collection is None:
            return "That collection does not exist."
        item = collection.items.create(content=thing, added_by=command.message.sender.id)
        return f"Added. {len(collection.items)} items in `{collection.name}`."

    @db_session
    def remove_item(self, command: Command):
        if len(command.args) < 2:
            return "Syntax: `/removeitem <collection> <thing to remove>`"
        collection_name = command.args[0]
        thing = ' '.join(command.args[1:])
        collection = Collection.get(name=collection_name)
        if collection is None:
            return "That collection does not exist."
        else:
            deleted = collection.items.filter(lambda item: item.content == thing).delete()
            if deleted == 0:
                return "Couldn't find that item."
            else:
                return f"Item removed. {len(collection.items)} in /{collection.name}."
