from horsefax.bot.core import HorseFaxBot

bot = HorseFaxBot()
bot.go()

# TODO: some sane way to run the bot forever.
import threading
[x.join() for x in threading.enumerate() if x != threading.current_thread()]