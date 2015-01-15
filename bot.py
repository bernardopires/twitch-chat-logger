import settings
import threading
import Queue
import socket

from irc import IRCBot, run_bot


class TwitchBot(IRCBot, threading.Thread):
    def __init__(self, conn, chat_logger, command_queue, *args, **kwargs):
        super(TwitchBot, self).__init__(conn, *args, **kwargs)

        self.chat_logger = chat_logger
        self.command_queue = command_queue
        self.disconnect = threading.Event()
        self.logger = self.conn.logger

    def run(self):
        patterns = self.conn.dispatch_patterns()

        while not self.disconnect.is_set():
            data = self.conn.get_data()
            if not data:
                self.logger.info('Disconnected from server')
                self.conn.close()
                self.connect_and_join_channels(self.channels)
                continue

            self.conn.dispatch_data(data, patterns)

            try:
                command = self.command_queue.get_nowait()
                self.process_command(command)
            except Queue.Empty:
                continue

    def join(self, timeout=None):
        self.conn.close()
        self.disconnect.set()
        super(TwitchBot, self).join(timeout)

    def connect_and_join_channels(self, channels):
        if not self.conn.connect():
            raise RuntimeError("Failed to connect to IRC channel.")

        for channel in channels:
            self.conn.join(channel)
        self.channels = channels

    def process_command(self, command):
        """ command is expected to be a tuple of a string and a list """
        if not (type(command) is tuple and len(command) == 2):
            raise ValueError("Expected command to be a tuple of a string and a list")

        action, channels = command
        self.logger.info("Received command %s (%s)" % (action, ','.join(channels)))
        if action == 'join':
            for channel in channels:
                self.conn.join(channel)
            self.channels += channels
        elif action == 'part':
            for channel in channels:
                self.conn.part(channel)
            self.channels = [c for c in self.channels if c not in channels]

    def log(self, sender, message, channel):
        if sender == settings.IRC['NICK']:
            self.logger.info("%s, %s: %s " % (channel, sender, message))

        self.chat_logger.log_chat(sender, message, channel)

    def command_patterns(self):
        return (
            ('.*', self.log),
        )
