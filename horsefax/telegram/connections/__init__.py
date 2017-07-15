from abc import ABC, abstractmethod, abstractproperty
import requests
from typing import Optional, Any, Callable


MessageHandler = Callable[[dict, str], None]


class TelegramConnection(ABC):
    def __init__(self, token: str, handler: MessageHandler):
        self.token = token
        self.handler = handler

    def send(self, endpoint: str, message: dict, token: Optional[Any]=None) -> dict:
        return self.request(endpoint, json=message)

    @abstractmethod
    def connect(self) -> None:
        pass

    @property
    @abstractmethod
    def connected(self) -> bool:
        pass

    def request(self, endpoint: str, **kwargs) -> dict:
        result = requests.post(f"https://api.telegram.org/bot{self.token}/{endpoint}", **kwargs)
        result.raise_for_status()
        return result.json()['result']
