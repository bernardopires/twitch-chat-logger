import Queue
import settings
import time

from irc import run_bot, IRCConnection
from bot import TwitchBot
from utils import get_top_streams, get_channel_names
from db_logger import DatabaseLogger


def main():
    STREAMS_TO_FETCH = 20
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

    channels = get_channel_names(get_top_streams(STREAMS_TO_FETCH))
    bot.connect_and_join_channels(channels)
    bot.start()
    while True:
        try:
            time.sleep(60)
            streams = get_top_streams(STREAMS_TO_FETCH)
            new_channels = get_channel_names(streams)
            channels_to_remove = list(set(channels) - set(new_channels))
            channels_to_add = list(set(new_channels) - set(channels))

            if channels_to_remove:
                command_queue.put(('part', channels_to_remove))

            if channels_to_add:
                command_queue.put(('join', channels_to_add))

            # log stream stats
            for stream in streams:
                logger.log_stream_stats(stream)

            channels = new_channels
        except KeyboardInterrupt:
            print 'Exiting gracefully...'
            bot.join()
            break

if __name__ == "__main__":
    main()
