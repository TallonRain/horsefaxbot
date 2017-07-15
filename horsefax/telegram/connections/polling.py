import requests
import threading
import time

from . import TelegramConnection, MessageHandler


class LongPollingConnection(TelegramConnection):
    def __init__(self, token: str, handler: MessageHandler):
        super().__init__(token, handler)
        self._connected = False
        self.latest_update = 0
        self.thread = threading.Thread(target=self.run)

    def connect(self):
        self.thread.start()

    @property
    def connected(self) -> bool:
        return self._connected

    def disconnect(self):
        self._connected = False

    def run(self):
        self._connected = True
        while self.connected:
            try:
                updates = self.request("getUpdates", json={"offset": self.latest_update + 1, "timeout": 60}, timeout=70)
            except requests.RequestException:
                time.sleep(10)
                continue
            if not updates:
                continue
            updates = sorted(updates, key=lambda x: x['update_id'])
            for update in updates:
                # doing this per message ensures that we don't drop messages if we crash out.
                self.latest_update = update['update_id']
                self.handler(update)
