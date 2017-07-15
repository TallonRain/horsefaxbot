import threading

from . import TelegramConnection, MessageHandler


class LongPollingConnection(TelegramConnection):
    def __init__(self, token: str, handler: MessageHandler):
        super().__init__(token, handler)
        self.connected = False
        self.latest_update = 0
        self.thread = threading.Thread(target=self.run)

    def connect(self):
        self.thread.start()

    def run(self):
        self.connected = True
        while self.connected:
            updates = self.request("getUpdates", json={"offset": self.latest_update + 1, "timeout": 60}, timeout=60)
            if not updates:
                continue
            updates = sorted(updates, key=lambda x: x['update_id'])
            self.latest_update = updates[-1]['update_id']
            for update in updates:
                self.handler(update)
