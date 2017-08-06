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

    @db_session
    def handle_message(self, message: Message) -> None:
        origin = message.sender
        try:
            TelegramUser[origin.id].set(username=origin.username, first_name=origin.first_name,
                                        last_name=origin.last_name, language_code=origin.language_code)
        except ObjectNotFound:
            TelegramUser(id=origin.id, username=origin.username,
                         first_name=origin.first_name, last_name=origin.last_name,
                         language_code=origin.language_code)

    @db_session
    def user_by_username(self, username: str) -> Optional[User]:
        user = TelegramUser.get(username=username)
        if user is None:
            return None
        return user.to_user()
