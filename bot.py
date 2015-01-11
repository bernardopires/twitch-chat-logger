import settings

from irc import IRCBot, run_bot


class TwitchBot(IRCBot):
    chat_logger = None

    def __init__(self, conn, chat_logger, *args, **kwargs):
        super(TwitchBot, self).__init__(conn, *args, **kwargs)
        self.chat_logger = chat_logger

    def log(self, sender, message, channel):
        if sender == settings.IRC['NICK']:
            print "%s, %s: %s " % (channel, sender, message)
            return

        self.chat_logger.log(sender, message, channel)

    def command_patterns(self):
        return (
            ('.*', self.log),
        )

