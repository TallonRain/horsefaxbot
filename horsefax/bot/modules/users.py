from pony.orm import *
orm_Optional = Optional
from typing import Optional


from ..core import HorseFaxBot, ModuleTools, BaseModule
from ..db import db
from horsefax.telegram.types import Message, User


class TelegramUser(db.Entity):
    id = PrimaryKey(int)
    username = orm_Optional(str, index=True)
    first_name = Required(str)
    last_name = orm_Optional(str)
    language_code = orm_Optional(str)

    def to_user(self):
        return User({'id': self.id,
                     'username': self.username,
                     'first_name': self.first_name,
                     'last_name': self.last_name,
                     'language_code': self.language_code})


class UsersModule(BaseModule):
    def __init__(self, bot: HorseFaxBot, util: ModuleTools) -> None:
        self.bot = bot
        self.util = util
        self.bot.telegram.register_handler("message", self.handle_message)

    def handle_message(self, message: Message) -> None:
        origin = message.sender
        self.update_user(origin)
        if message.forward_from and isinstance(message.forward_from, User):
            self.update_user(message.forward_from)
        if message.reply_to_message:
            self.handle_message(message.reply_to_message)

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
