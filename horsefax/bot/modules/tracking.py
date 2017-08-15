import datetime
from pony.orm import *
from pony import orm
from typing import Optional, Dict, Union


from ..core import HorseFaxBot, ModuleTools, BaseModule
from ..db import db
from horsefax.telegram.types import (Message, User, Chat, UsersJoinedMessage, UserLeftMessage, ChatMigrateFromIDMessage,
                                     MessagePinnedMessage, TextMessage, TextEntity, PhotoMessage, StickerMessage,
                                     VideoMessage, VideoNoteMessage, DocumentMessage, AudioMessage, PhotoSize)


class TelegramUser(db.Entity):
    id = PrimaryKey(int)
    username = orm.Optional(str, index=True, nullable=True)
    first_name = Required(str)
    last_name = orm.Optional(str, nullable=True)
    language_code = orm.Optional(str, nullable=True)
    chats = Set('TelegramChat')
    sent_messages = Set('TelegramMessage', reverse="sender")
    forwarded_messages = Set('TelegramMessage', reverse="forward_from")

    # for groups module
    ping_groups = Set('PingGroup')

    def to_user(self):
        return User({'id': self.id,
                     'username': self.username,
                     'first_name': self.first_name,
                     'last_name': self.last_name,
                     'language_code': self.language_code})


class TelegramChat(db.Entity):
    id = PrimaryKey(int, size=64)
    type = Required(Chat.Type, index=True)
    title = orm.Optional(str, nullable=True)
    all_members_are_administrators = Required(bool)
    users = Set(TelegramUser)
    pinned_message = orm.Optional(int)
    messages = Set('TelegramMessage', reverse="chat")


class TelegramMessage(db.Entity):
    id = Required(int)
    chat = Required(TelegramChat)
    sender = Required(TelegramUser, reverse="sent_messages")
    date = Required(datetime.datetime, index=True)
    forward_from = orm.Optional(TelegramUser, reverse="forwarded_messages")
    reply_to = orm.Optional('TelegramMessage')
    replies = Set('TelegramMessage')
    edit_date = orm.Optional(datetime.datetime)
    PrimaryKey(chat, id)


class TelegramTextMessage(TelegramMessage):
    text = Required(str)
    entities = Required(Json)


class FileMessage(TelegramMessage):
    file_id = Required(str)
    mime_type = orm.Optional(str, nullable=True)
    file_size = orm.Optional(int)
    caption = orm.Optional(str, nullable=True)
    thumbnail = orm.Optional(str, nullable=True)


class VisualMessage(FileMessage):
    width = Required(int)
    height = Required(int)


class LongMessage(FileMessage):
    duration = Required(int)


class TelegramPhotoMessage(VisualMessage):
    pass


class TelegramStickerMessage(VisualMessage):
    emoji = orm.Optional(str, nullable=True)


class TelegramVideoMessage(LongMessage, VisualMessage):
    pass


class TelegramVideoNoteMessage(LongMessage, VisualMessage):
    pass

class TelegramDocumentMessage(FileMessage):
    file_name = orm.Optional(str, nullable=True)

class TelegramAudioMessage(LongMessage):
    performer = orm.Optional(str, nullable=True)
    title = orm.Optional(str, nullable=True)


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

        if isinstance(message, TextMessage):
            for entity in message.entities:
                if entity.user is not None:
                    self.update_user(entity.user)

        # Track chats
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
            TelegramChat[message.id].users.clear()

        if TelegramMessage.get(id=message.message_id):
            return
        # Handle logging
        log_params = {'id': message.message_id,
                      'sender': TelegramUser[message.sender.id],
                      'date': message.date,
                      'chat': TelegramChat[message.chat.id],
                      'forward_from': TelegramUser[message.forward_from.id] if message.forward_from else None,
                      'reply_to': TelegramMessage.get(id=message.reply_to_message.message_id) if message.reply_to_message is not None else None,
                      'edit_date': message.edit_date}
        if isinstance(message, TextMessage):
            TelegramTextMessage(text=message.text,
                                entities=[self._json_from_entity(x) for x in message.entities],
                                **log_params)
        elif isinstance(message, PhotoMessage):
            big_photo = max(message.photo, key=lambda x: x.width * x.height)  # type: PhotoSize
            if len(message.photo) > 1:
                small_photo = min(message.photo, key=lambda x: x.width * x.height)  # type: PhotoSize
                thumb = small_photo.file_id
            else:
                thumb = None
            TelegramPhotoMessage(file_id=big_photo.file_id, file_size=big_photo.file_size, width=big_photo.width,
                                 height=big_photo.height, caption=message.caption, mime_type="image/jpeg",
                                 thumbnail=thumb, **log_params)
        elif isinstance(message, StickerMessage):
            TelegramStickerMessage(file_id=message.file_id, file_size=message.file_size, mime_type="image/webp",
                                   width=message.width, height=message.height, emoji=message.emoji, **log_params)
        elif isinstance(message, VideoMessage):
            TelegramVideoMessage(file_id=message.file_id, file_size=message.file_size, mime_type=message.mime_type,
                                 width=message.width, height=message.height, duration=message.duration,
                                 thumbnail=message.thumbnail.file_id if message.thumbnail else None,
                                 caption=message.caption, **log_params)
        elif isinstance(message, VideoNoteMessage):
            TelegramVideoNoteMessage(file_id=message.file_id, file_size=message.file_size, mime_type="video/mp4",
                                     width=message.length, height=message.length,
                                     thumbnail=message.thumbnail.file_id if message.thumbnail else None,
                                     duration=message.duration, **log_params)
        elif isinstance(message, DocumentMessage):
            TelegramDocumentMessage(file_id=message.file_id, file_size=message.file_size, mime_type=message.mime_type,
                                    thumbnail=message.thumbnail.file_id if message.thumbnail else None,
                                    caption=message.caption, file_name=message.file_name, **log_params)
        elif isinstance(message, AudioMessage):
            TelegramAudioMessage(file_id=message.file_id, file_size=message.file_size, mime_type=message.mime_type,
                                 performer=message.performer, title=message.title, **log_params)

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

    def _json_from_entity(self, entity: TextEntity) -> Dict[str, Union[str, int]]:
        ret = {
            'type': entity.type.value,
            'offset': entity.offset,
            'length': entity.length,
        }
        if entity.url:
            ret['url'] = entity.url
        if entity.user:
            ret['user'] = entity.user.id
        return ret
