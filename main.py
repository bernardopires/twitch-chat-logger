import Queue
import settings
import time

from irc import run_bot, IRCConnection
from bot import TwitchBot
from utils import get_top_streams, get_channel_names
from db_logger import DatabaseLogger
from manager import TwitchManager


def main():
    manager = TwitchManager(streams_to_log=100)
    try:
        manager.run_log_loop()
    except KeyboardInterrupt:
        print 'Exiting gracefully...'
        manager.stop_bot()

if __name__ == "__main__":
    main()
