import Queue
import settings
import time

from irc import run_bot, IRCConnection
from bot import TwitchBot
from utils import get_top_streams, get_channel_names
from db_logger import DatabaseLogger


class TwitchManager:
    """
    Manages a series of irc chat bots that log the most popular channels on
    Twitch.TV. The list of most popular channels is updated every 60 seconds.
    """
    CHANNELS_PER_BOT = 20
    SECONDS_BETWEEN_UPDATE_STREAMS = 60
    SECONDS_BETWEEN_CREATE_BOTS = 15

    def __init__(self, streams_to_log):
        self.bots = []
        self.streams_to_log = streams_to_log
        self.db_logger = DatabaseLogger(settings.DATABASE['HOST'],
                                        settings.DATABASE['NAME'],
                                        settings.DATABASE['USER'],
                                        settings.DATABASE['PASSWORD'])

    def _create_bot(self, name, channels):
        conn = IRCConnection(settings.IRC['SERVER'],
                             settings.IRC['PORT'],
                             settings.IRC['NICK'],
                             settings.IRC['PASSWORD'])
        bot_db_logger = DatabaseLogger(settings.DATABASE['HOST'],
                                       settings.DATABASE['NAME'],
                                       settings.DATABASE['USER'],
                                       settings.DATABASE['PASSWORD'])
        bot = TwitchBot(name, conn, bot_db_logger, Queue.Queue())
        bot.daemon = True
        bot.connect_and_join_channels(channels)
        bot.start()
        return bot

    def _create_bots(self, streams_to_log):
        """
        Creates bots to log all the desired streams.

        Twitch limits how many channels can be joined per connection, so we
        create just enough bots to log all the desired streams. There's also
        a timeout between opening connections otherwise Twitch disconnects
        all bots.
        """
        streams = get_top_streams(streams_to_log)
        channels = get_channel_names(streams)

        channels_joined = 0
        while channels_joined < streams_to_log:
            # create a new bot
            self.bots.append(
                self._create_bot('Bot %i' % len(self.bots),
                                 channels[channels_joined:channels_joined + self.CHANNELS_PER_BOT]))
            channels_joined += self.CHANNELS_PER_BOT
            time.sleep(self.SECONDS_BETWEEN_CREATE_BOTS)

        self._log_streams(streams)

    def _update_bot_channels(self, bot, new_channels):
        channels_to_remove = list(set(bot.channels) - set(new_channels))
        channels_to_add = list(set(new_channels) - set(bot.channels))

        if channels_to_remove:
            bot.command_queue.put(('part', channels_to_remove))

        if channels_to_add:
            bot.command_queue.put(('join', channels_to_add))

    def _log_streams(self, streams):
        for stream in streams:
            self.db_logger.log_stream_stats(stream)

    def run_log_loop(self):
        """
        Creates the logger bots and update which stream they log every 60
        seconds.
        """
        self._create_bots(self.streams_to_log)

        while True:
            time.sleep(self.SECONDS_BETWEEN_UPDATE_STREAMS)
            streams = get_top_streams(self.streams_to_log)
            channels = get_channel_names(streams)

            i, channels_joined = 0, 0
            while channels_joined < self.streams_to_log:
                self._update_bot_channels(self.bots[i],
                                          channels[channels_joined:channels_joined + self.CHANNELS_PER_BOT])
                i += 1
                channels_joined += self.CHANNELS_PER_BOT

            self._log_streams(streams)

    def stop_bot(self):
        for bot in self.bots:
            bot.join()
