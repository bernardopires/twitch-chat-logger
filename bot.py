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

    def run(self):
        patterns = self.conn.dispatch_patterns()

        while not self.disconnect.is_set():
            data = self.conn.get_data()
            if not data:
                print 'disconnected'
                self.conn.close()
                self.connect_and_join_channels(self.channels)
                continue

            self.conn.dispatch_data(data, patterns)

            try:
                command = self.command_queue.get(False)
                self.process_command(command)
            except Queue.Empty:
                continue

    def join(self, timeout=None):
        self.conn.close()
        self.disconnect.set()
        super(TwitchBot, self).join(timeout)

    def connect_and_join_channels(self, channels):
        if not self.conn.connect():
            pass  # throw exception

        for channel in channels:
            self.conn.join(channel)
        self.channels = channels

    def process_command(command):
        pass

    def log(self, sender, message, channel):
        if sender == settings.IRC['NICK']:
            print "%s, %s: %s " % (channel, sender, message)
            return

        self.chat_logger.log(sender, message, channel)

    def command_patterns(self):
        return (
            ('.*', self.log),
        )
