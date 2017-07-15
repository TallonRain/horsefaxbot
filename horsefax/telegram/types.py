import datetime
from dateutil.tz import tzutc
from enum import Enum
from typing import Optional, Dict, Any, Callable, TypeVar, Type

__all__ = ['Message', 'TextMessage', 'AudioMessage', 'DocumentMessage', 'GameMessage', 'PhotoMessage', 'StickerMessage',
           'VideoMessage', 'VideoNoteMessage', 'UsersJoinedMessage', 'UserLeftMessage', 'NewChatTitleMessage',
           'NewChatPhotoMessage', 'DeleteChatPhotoMessage', 'GroupChatCreatedMessage', 'SupergroupChatCreatedMessage',
           'ChannelChatCreatedMessage', 'ChatMigrateToIDMessage', 'ChatMigrateFromIDMessage', 'MessagePinnedMessage',
           'InvoiceMessage', 'ContactMessage', 'LocationMessage', 'VenueMessage', 'User', 'PhotoSize', 'TextEntity',
           'Chat']

T = TypeVar('T')
S = TypeVar('S')


def _optional(constructor: Callable[[S], T], value: Optional[S], **kwargs) -> Optional[T]:
    if value:
        return constructor(value, **kwargs)
    else:
        return None


def _from_ts(t: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(t, tz=tzutc())


class Message:
    def __init__(self, p: Dict[str, Any]):
        self.message_id = p['message_id']  # type: int
        self.sender = User(p['from'])
        self.date = _from_ts(p['date'])
        self.chat = Chat(p['chat'])
        self.forward_from = _optional(User, p.get('forward_from'))
        self.forward_from_chat = _optional(Chat, p.get('forward_from_chat'))
        self.forward_from_message_id = p.get('forward_from_message_id', None)  # type: Optional[int]
        self.forward_date = _optional(_from_ts, p.get('forward_date'))
        self.reply_to_message = _optional(Message, p.get('reply_to_message'))
        self.edit_date = _optional(_from_ts, p.get('edit_date'))

    @classmethod
    def from_update(cls, update):
        mapping = {
            'text': TextMessage,
            'audio': AudioMessage,
            'document': DocumentMessage,
            'game': GameMessage,
            'photo': PhotoMessage,
            'sticker': StickerMessage,
            'video': VideoMessage,
            'video_note': VideoNoteMessage,
            'new_chat_members': UsersJoinedMessage,
            'new_chat_member': _one_user_joined_message,
            'left_chat_member': UserLeftMessage,
            'contact': ContactMessage,
            'location': LocationMessage,
            'venue': VenueMessage,
            'new_chat_title': NewChatTitleMessage,
            'new_chat_photo': NewChatPhotoMessage,
            'delete_chat_photo': DeleteChatPhotoMessage,
            'group_chat_created': GroupChatCreatedMessage,
            'supergroup_chat_created': SupergroupChatCreatedMessage,
            'channel_chat_created': ChannelChatCreatedMessage,
            'migrate_to_chat_id': ChatMigrateToIDMessage,
            'migrate_from_chat_id': ChatMigrateFromIDMessage,
            'pinned_message': MessagePinnedMessage,
            'invoice': InvoiceMessage,
        }
        for k, v in mapping.items():
            if k in update:
                return v(update)
        return Message(update)


class TextMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        self.text = p['text']  # type: str
        self.entities = [TextEntity(x) for x in p.get('entities', [])]

    def __str__(self):
        return f"{self.sender.first_name}: {self.text}"


class FileMixin:
    pass


class AudioMessage(FileMixin, Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        audio = p['audio']  # type: Dict[str, Any]
        self.file_id = audio['file_id']  # type: str
        self.duration = audio['duration']  # type: int
        self.performer = audio.get('performer', None)  # type: Optional[str]
        self.title = audio.get('title', None)  # type: Optional[str]
        self.mime_type = audio.get('mime_type', None)  # type: Optional[str]
        self.file_size = audio.get('file_size', None)  # type: Optional[int]


class DocumentMessage(FileMixin, Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        doc = p['document']  # type: Dict[str, Any]
        self.file_id = doc['file_id']
        self.thumbnail = _optional(PhotoSize, p.get('thumb'))
        self.caption = p.get('caption', None)  # type: Optional[str]
        self.file_name = doc.get('file_name', None)  # type: Optional[str]
        self.mime_type = doc.get('mime_type', None)  # type: Optional[str]
        self.file_size = doc.get('file_size', None)  # type: Optional[int]


class GameMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        game = p['game']  # type: Dict[str, Any]
        self.title = game['title']  # type: str
        self.description = game['description']  # type: str
        self.photo = [PhotoSize(x) for x in game['photo']]
        self.text = game.get('text', None)  # type: Optional[str]
        self.text_entities = [TextEntity(x) for x in game.get('message_entities', [])]
        # animation not implemented.


class PhotoMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        self.photo = [PhotoSize(x) for x in p['photo']]
        self.caption = p.get('caption', None)  # type: Optional[str]


class StickerMessage(FileMixin, Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        sticker = p['sticker']  # type: Dict[str, Any]
        self.file_id = sticker['file_id']  # type: str
        self.width = sticker['width']  # type: int
        self.height = sticker['height']  # type: int
        self.thumb = _optional(PhotoSize, sticker.get('thumb'))
        self.emoji = sticker.get('emoji', None)  # type: Optional[str]
        self.file_size = sticker.get('file_size', None)  # type: Optional[int]


class VideoMessage(FileMixin, Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        video = p['video']  # type: Dict[str, Any]
        self.caption = p.get('caption', None)  # type: Dict[str, Any]
        self.file_id = video['file_id']  # type: str
        self.width = video['width']  # type: int
        self.height = video['height']  # type: int
        self.duration = video['duration']  # type: int
        self.thumbnail = _optional(PhotoSize, video.get('thumb'))
        self.mime_type = video.get('mime_type', None)  # type: Optional[str]
        self.file_size = video.get('file_size', None)  # type: Optional[int]


class VideoNoteMessage(FileMixin, Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        video = p['video_note']  # type: Dict[str, Any]
        self.file_id = video['file_id']  # type: str
        self.length = video['length']  # type: int
        self.duration = video['duration']  # type: int
        self.thumbnail = _optional(PhotoSize, video.get('thumb'))
        self.file_size = video.get('file_size', None)  # type: int


class UsersJoinedMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        self.users = [User(x) for x in p['new_chat_members']]


class UserLeftMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        self.user = User(p['left_chat_member'])


class NewChatTitleMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        self.title = p['new_chat_title']  # type: str


class NewChatPhotoMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        self.photo = [PhotoSize(x) for x in p['new_chat_photo']]


class DeleteChatPhotoMessage(Message):
    pass


class GroupChatCreatedMessage(Message):
    pass


class SupergroupChatCreatedMessage(Message):
    pass


class ChannelChatCreatedMessage(Message):
    pass


class ChatMigrateToIDMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        self.id = p['migrate_to_chat_id']  # type: int


class ChatMigrateFromIDMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        self.id = p['migrate_from_chat_id']  # type: int


class MessagePinnedMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        self.message = Message(p['pinned_message'])


class InvoiceMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        invoice = p['invoice']  # type: Dict[str, Any]
        self.title = invoice['title']  # type: str
        self.description = invoice['description']  # type: str
        self.start_param = invoice['start_parameter']  # type: str
        self.currency = invoice['currency']  # type: str
        self.total_amount = invoice['total_amount']  # type: int


def _one_user_joined_message(message: Dict[str, Any]) -> UsersJoinedMessage:
    message = message.copy()
    message['new_chat_members'] = [message['new_chat_member']]
    del message['new_chat_member']
    return UsersJoinedMessage(message)


class ContactMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        contact = p['contact']  # type: Dict[str, Any]
        self.phone_number = contact['phone_number']  # type: str
        self.first_name = contact['first_name']  # type: str
        self.last_name = contact.get('last_name', None)  # type: Optional[str]
        self.telegram_user_id = contact.get('user_id', None)  # type: Optional[int]


class LocationMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        location = p['location']  # type: Dict[str, Any]
        self.longitude = location['longitude']  # type: int
        self.latitude = location['latitude']  # type: int


class VenueMessage(Message):
    def __init__(self, p: Dict[str, Any]):
        super().__init__(p)
        venue = p['venue']
        location = venue['location']  # type: Dict[str, Any]
        self.longitude = location['longitude']  # type: int
        self.latitude = location['latitude']  # type: int
        self.title = location['title']  # type: str
        self.address = location['address']  # type: str
        self.foursquare_id = location.get('foursquare_id')  # type: Optional[int]


class PhotoSize:
    def __init__(self, p: Dict[str, Any]):
        self.file_id = p['file_id']  # type: str
        self.width = p['width']  # type: int
        self.height = p['height']  # type: int
        self.file_size = p.get('file_size', None)  # type: Optional[int]


class TextEntity:
    class Type(Enum):
        MENTION = 'mention'
        HASHTAG = 'hashtag'
        BOT_COMMAND = 'bot_command'
        URL = 'url'
        EMAIL = 'email'
        BOLD = 'bold'
        ITALIC = 'italic'
        CODE = 'code'
        PRE = 'pre'
        TEXT_LINK = 'text_link'
        TEXT_MENTION = 'text_mention'

    def __init__(self, properties: Dict[str, Any]):
        self.type = self.Type(properties['type'])
        self.offset = properties['offset']  # type: int
        self.length = properties['length']  # type: int
        self.url = properties.get('url')  # type: Optional[str]
        self.user = _optional(User, properties.get('user'))


class User:
    def __init__(self, properties: Dict[str, Any]):
        self.id = properties['id']  # type: int
        self.first_name = properties['first_name']  # type: str
        self.last_name = properties.get('last_name', '')  # type: str
        self.username = properties.get('username', None)  # type: Optional[str]
        self.language_code = properties.get('language_code', None)  # type: Optional[str]


class Chat:
    class Type(Enum):
        PRIVATE = 'private'
        GROUP = 'group'
        SUPERGROUP = 'supergroup'
        CHANNEL = 'channel'

    def __init__(self, properties: Dict[str, Any]):
        self.id = properties['id']  # type: int
        self.type = self.Type(properties['type'])
        self.title = properties.get('title', None)  # type: Optional[str]
        self.username = properties.get('username', None)  # type: Optional[str]
        self.first_name = properties.get('first_name', None)  # type: Optional[str]
        self.last_name = properties.get('last_name', None)  # type: Optional[str]
        self.all_members_are_administrators = properties.get('all_members_are_administrators', False)  # type: bool
