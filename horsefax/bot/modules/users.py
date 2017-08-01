from peewee import *
from typing import Optional

from ..core import HorseFaxBot, ModuleTools, BaseModule
from ..db import BaseModel
from horsefax.telegram.types import Message, User


class TelegramUser(BaseModel):
    id = IntegerField(primary_key=True)
    username = CharField(null=True, index=True)
    first_name = CharField()
    last_name = CharField(null=True)
    language_code = CharField(null=True)

    def to_user(self):
        return User({'id': self.id,
                     'username': self.username,
                     'first_name': self.first_name,
                     'last_name': self.last_name,
                     'language_code': self.language_code})


class UsersModule(BaseModule):
    def __init__(self, bot: HorseFaxBot, util: ModuleTools):
        self.bot = bot
        self.util = util
        self.bot.telegram.register_handler("message", self.handle_message)

    def handle_message(self, message: Message):
        origin = message.sender
        user = TelegramUser(id=origin.id, username=origin.username,
                            first_name=origin.first_name, last_name=origin.last_name,
                            language_code=origin.language_code)
        try:
            user.save(force_insert=True)
        except IntegrityError:
            user.save(force_insert=False)

    def user_by_username(self, username: str) -> Optional[User]:
        try:
            return TelegramUser.get(username=username).to_user()
        except DoesNotExist:
            return None
