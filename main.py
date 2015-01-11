import settings

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
    bot = TwitchBot(conn, logger)

    channels = get_top_channels(25)
    while True:
        if not conn.connect():
            break

        for channel in channels:
            conn.join(channel)

        conn.enter_event_loop()

if __name__ == "__main__":
    main()
