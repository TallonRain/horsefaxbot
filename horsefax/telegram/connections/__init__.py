from abc import ABC, abstractmethod
from typing import Optional, Any, Callable

MessageHandler = Callable[[dict, str], None]


class TelegramConnection(ABC):
    def __init__(self, token: str, handler: MessageHandler):
        self.token = token
        self.handler = handler

    @abstractmethod
    def send(self, message: dict, token: Optional[Any]=None):
        pass
