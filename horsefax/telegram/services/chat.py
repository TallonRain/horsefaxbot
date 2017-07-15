from enum import Enum
from typing import Union, Optional
from .. import Telegram
from ..types import Chat, User, Message


class ChatService:
    class ParseMode(Enum):
        NONE = None
        MARKDOWN = 'Markdown'
        HTML = 'HTML'

    def __init__(self, telegram: Telegram):
        self.telegram = telegram

    def message(self, target: Union[Chat, User, int], message: str, parsing: ParseMode=ParseMode.NONE,
                silent=False, preview=True, reply_to: Optional[Union[int, Message]]=None):
        if isinstance(target, Chat):
            target = target.id
        elif isinstance(target, User):
            target = target.id
        assert isinstance(target, int)

        if reply_to and isinstance(reply_to, Message):
            reply_to = reply_to.message_id

        command = {
            "chat_id": target,
            "text": message,
            "disable_web_page_preview": not preview,
            "disable_notification": silent,
        }
        if parsing is not self.ParseMode.NONE:
            command['parse_mode'] = parsing.value
        if reply_to is not None:
            command['reply_to'] = reply_to

        self.telegram.connection.send("sendMessage", command)
