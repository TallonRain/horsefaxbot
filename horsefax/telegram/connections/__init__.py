from abc import ABC, abstractmethod, abstractproperty
import requests
from typing import Optional, Any, Callable


MessageHandler = Callable[[dict], None]


class TelegramConnection(ABC):
    def __init__(self, token: str, handler: MessageHandler) -> None:
        self.token = token
        self.handler = handler
        self.session = requests.Session()

    def send(self, endpoint: str, message: dict) -> dict:
        return self.request(endpoint, json=message)

    @abstractmethod
    def connect(self) -> None:
        pass

    @property
    @abstractmethod
    def connected(self) -> bool:
        pass

    def request(self, endpoint: str, **kwargs) -> dict:
        result = self.session.post(f"https://api.telegram.org/bot{self.token}/{endpoint}", **kwargs)
        result.raise_for_status()
        return result.json()['result']
