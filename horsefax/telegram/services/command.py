from typing import Tuple, List

from .. import Telegram
from ..events.mixin import EventSourceMixin
from ..types import Message, TextMessage


class Command:
    def __init__(self, message: TextMessage, command: str, args: List[str]):
        self.message = message
        self.command = command
        self.args = args


class CommandService(EventSourceMixin):
    def __init__(self, telegram: Telegram):
        super().__init__()
        self.telegram = telegram
        self.telegram.register_handler("message", self.handle_message)

    def handle_message(self, message: Message):
        if not isinstance(message, TextMessage):
            return
        text = message.text
        if len(text) == 0:
            return
        if text[0] != '/':
            return
        parts = text.split()
        command = parts[0][1:]
        if '@' in command:
            command, target = command.split('@', maxsplit=1)
            if target != self.telegram.user.username:
                return

        self._broadcast_event(command, Command(message, command, parts[1:]))
