import Queue
import settings
import time

from irc import run_bot, IRCConnection
from bot import TwitchBot
from utils import get_top_streams, get_channel_names
from db_logger import DatabaseLogger

class TwitchManager:
    def __init__(self, streams_to_log):
        self.streams_to_log = streams_to_log
        self.db_logger = DatabaseLogger(settings.DATABASE['HOST'],
                                        settings.DATABASE['NAME'],
                                        settings.DATABASE['USER'],
                                        settings.DATABASE['PASSWORD'])

    def _initialize_bot(self):
        conn = IRCConnection(settings.IRC['SERVER'],
                             settings.IRC['PORT'],
                             settings.IRC['NICK'],
                             settings.IRC['PASSWORD'])
        bot_db_logger = DatabaseLogger(settings.DATABASE['HOST'],
                                       settings.DATABASE['NAME'],
                                       settings.DATABASE['USER'],
                                       settings.DATABASE['PASSWORD'])
        self.command_queue = Queue.Queue()
        streams = get_top_streams(self.streams_to_log)
        self.channels = get_channel_names(streams)
        self.bot = TwitchBot(conn, bot_db_logger, self.command_queue)
        self.bot.daemon = True
        self.bot.connect_and_join_channels(self.channels)
        self.bot.start()
        self._log_streams(streams)

    def _log_streams(self, streams):
        for stream in streams:
            self.db_logger.log_stream_stats(stream)

    def run_log_loop(self):
        self._initialize_bot()
        channels = self.channels
        while True:
            time.sleep(60)
            streams = get_top_streams(self.streams_to_log)
            new_channels = get_channel_names(streams)
            channels_to_remove = list(set(channels) - set(new_channels))
            channels_to_add = list(set(new_channels) - set(channels))

            if channels_to_remove:
                self.command_queue.put(('part', channels_to_remove))

            if channels_to_add:
                self.command_queue.put(('join', channels_to_add))

            self._log_streams(streams)
            channels = new_channels

    def stop_bot(self):
        self.bot.join()
