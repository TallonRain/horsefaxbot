from typing import Type, Dict, Any, Optional

from .connections import TelegramConnection
from .events.mixin import EventSourceMixin
from .types import *


class Telegram(EventSourceMixin):
    def __init__(self, token: str, connection: Type[TelegramConnection]):
        self.token = token
        self.connection = connection(token, self._handle_message)
        self.user = None  # type: Optional[User]
        super().__init__()

    def connect(self):
        self.connection.connect()
        self._request_info()

    @property
    def connected(self):
        return self.connection.connected

    def _handle_message(self, update: Dict[str, Any]):
        self._broadcast_event("update", update)
        if 'message' in update:
            self._broadcast_event("message", Message.from_update(update['message']))
        elif 'edited_message' in update:
            self._broadcast_event("edited_message", Message.from_update(update['edited_message']))

    def _request_info(self):
        self.user = User(self.connection.send("getMe", {}))
