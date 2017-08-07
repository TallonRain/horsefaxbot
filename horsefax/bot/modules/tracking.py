from pony.orm import *
from pony import orm
from typing import Optional


from ..core import HorseFaxBot, ModuleTools, BaseModule
from ..db import db
from horsefax.telegram.types import (Message, User, Chat, UsersJoinedMessage, UserLeftMessage, ChatMigrateFromIDMessage,
                                     MessagePinnedMessage)


class TelegramUser(db.Entity):
    id = PrimaryKey(int)
    username = orm.Optional(str, index=True, nullable=True)
    first_name = Required(str)
    last_name = orm.Optional(str, nullable=True)
    language_code = orm.Optional(str, nullable=True)
    chats = Set('TelegramChat')

    def to_user(self):
        return User({'id': self.id,
                     'username': self.username,
                     'first_name': self.first_name,
                     'last_name': self.last_name,
                     'language_code': self.language_code})


class TelegramChat(db.Entity):
    id = PrimaryKey(int, size=64)
    type = Required(Chat.Type)
    title = orm.Optional(str, nullable=True)
    all_members_are_administrators = Required(bool)
    users = Set(TelegramUser)
    pinned_message = orm.Optional(int)


class TrackingModule(BaseModule):
    def __init__(self, bot: HorseFaxBot, util: ModuleTools) -> None:
        self.bot = bot
        self.util = util
        self.bot.telegram.register_handler("message", self.handle_message)

    @db_session
    def handle_message(self, message: Message) -> None:
        # Track members
        origin = message.sender
        self.update_user(origin)
        if message.forward_from and isinstance(message.forward_from, User):
            self.update_user(message.forward_from)
        if message.reply_to_message:
            self.handle_message(message.reply_to_message)

        # Track chats
        if message.chat.type != Chat.Type.PRIVATE:
            self.update_chat(message.chat)
            TelegramChat[message.chat.id].users.add(TelegramUser[origin.id])

        if isinstance(message, UsersJoinedMessage):
            for user in message.users:
                self.update_user(user)
                TelegramChat[message.chat.id].users.add(TelegramUser[user.id])

        if isinstance(message, UserLeftMessage):
            self.update_user(message.user)
            TelegramChat[message.chat.id].users.remove(TelegramUser[message.user.id])

        if isinstance(message, MessagePinnedMessage):
            TelegramChat[message.chat.id].pinned_message = message.message.message_id

        if isinstance(message, ChatMigrateFromIDMessage):
            TelegramChat[message.chat.id].users.add(TelegramChat[message.id].users)
            TelegramChat[message.id].delete()

    def update_chat(self, chat: Chat):
        try:
            TelegramChat[chat.id].set(title=chat.title, type=chat.type,
                                      all_members_are_administrators=chat.all_members_are_administrators)
        except ObjectNotFound:
            TelegramChat(id=chat.id, type=chat.type, title=chat.title,
                         all_members_are_administrators=chat.all_members_are_administrators)

    @db_session
    def update_user(self, user: User):
        try:
            TelegramUser[user.id].set(username=user.username, first_name=user.first_name,
                                      last_name=user.last_name, language_code=user.language_code)
        except ObjectNotFound:
            TelegramUser(id=user.id, username=user.username,
                         first_name=user.first_name, last_name=user.last_name,
                         language_code=user.language_code)

    @db_session
    def user_by_username(self, username: str) -> Optional[User]:
        user = TelegramUser.get(username=username)
        if user is None:
            return None
        return user.to_user()
