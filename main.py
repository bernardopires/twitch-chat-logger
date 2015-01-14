import Queue
import settings
import time

from irc import run_bot, IRCConnection
from bot import TwitchBot
from utils import get_top_channels
from db_logger import DatabaseLogger

def main():
    conn = IRCConnection(settings.IRC['SERVER'],
                         settings.IRC['PORT'],
                         settings.IRC['NICK'],
                         settings.IRC['PASSWORD'])
    logger = DatabaseLogger(settings.DATABASE['HOST'],
                            settings.DATABASE['NAME'],
                            settings.DATABASE['USER'],
                            settings.DATABASE['PASSWORD'])
    command_queue = Queue.Queue()
    bot = TwitchBot(conn, logger, command_queue)
    bot.daemon = True

    channels = get_top_channels(20)
    bot.connect_and_join_channels(channels)
    bot.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print 'Exiting gracefully...'
            bot.join()
            break

if __name__ == "__main__":
    main()
