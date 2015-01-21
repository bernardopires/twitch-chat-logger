import settings
import threading
import Queue
import socket
import logging

from irc import IRCBot, run_bot, DisconnectedException


class TwitchBot(IRCBot, threading.Thread):
    """
    A threaded IRC bot that automatically reconnects and rejoins channels if
    disconnected. Communication happens over the queue command_queue. The
    accepted commands through the queue are 'join' and 'part'.
    """
    MESSAGES_TO_IGNORE = ['/join', '/part']

    def __init__(self, name, conn, chat_logger, command_queue, log_filename=None, *args, **kwargs):
        super(TwitchBot, self).__init__(conn, *args, **kwargs)

        self.name = name
        self.chat_logger = chat_logger
        self.command_queue = command_queue
        self.disconnect = threading.Event()

        self.logger = self.conn.get_logger(name, log_filename)

    def run(self):
        """
        Receives data in a loop until the event for disconnecting is set.
        Checks the command queue for actions to be taken (joining or leaving
        channels).
        """
        patterns = self.conn.dispatch_patterns()

        while not self.disconnect.is_set():
            try:
                data = self.conn.get_data()  # returns empty string if times out
                if data:
                    self.conn.dispatch_data(data, patterns)

                command = self.command_queue.get_nowait()
                self.process_command(command)
            except DisconnectedException:
                self.logger.info('Disconnected from server. Reconnecting.')
                self.conn.close()
                self.connect_and_join_channels(self.channels)
                continue
            except Queue.Empty:
                continue

    def join(self, timeout=None):
        """
        Forces the bot to disconnect, close its socket and database
        connection.
        """
        self.conn.close()
        self.chat_logger.close()
        self.logger.info('Closed connection.')
        self.disconnect.set()
        super(TwitchBot, self).join(timeout)

    def connect_and_join_channels(self, channels):
        if not self.conn.connect():
            raise RuntimeError("Failed to connect to IRC channel.")

        for channel in channels:
            self.conn.join(channel)
        self.channels = channels

    def process_command(self, command):
        """
        Processes a command, either joining or leaving channels.
        command is expected to be a tuple of a string and a list.
        Valid commands are 'join' and 'part'.
        """
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
            return
        if message in self.MESSAGES_TO_IGNORE:
            return

        self.chat_logger.log_chat(sender, message, channel)

    def command_patterns(self):
        return (
            ('.*', self.log),
        )
