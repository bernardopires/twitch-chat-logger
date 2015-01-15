import psycopg2

from utils import current_time_in_milli


class DatabaseLogger:
    conn = None
    cursor = None

    def __init__(self, host, name, user, password):
        self.conn = psycopg2.connect(host=host, dbname=name, user=user, password=password)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def log_chat(self, sender, message, channel):
        if len(message) > 512:
            message = message[:512]

        try:
            self.cursor.execute("INSERT INTO chat_log (sender, message, channel, date) VALUES (%s, %s, %s, %s)",
                                (sender, message, channel, current_time_in_milli()))
        except psycopg2.DataError as e:
            print e
            print message

    def log_stream_stats(self, stream):
        if 'status' not in stream['channel']:
            stream['channel']['status'] = None
        if 'game' not in stream['channel']:
            stream['channel']['game'] = None

        self.cursor.execute("INSERT INTO stream_log (channel, title, game, viewers, date) "
                            "VALUES (%s, %s, %s, %s, %s)",
                            (stream['channel']['name'],
                                stream['channel']['status'],
                                stream['channel']['game'],
                                int(stream['viewers']),
                                current_time_in_milli()))
