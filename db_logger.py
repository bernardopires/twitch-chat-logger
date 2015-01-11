import psycopg2

from utils import current_time_in_milli

class DatabaseLogger:
    conn = None
    cursor = None

    def __init__(self, host, name, user, password):
        self.conn = psycopg2.connect(host=host, dbname=name, user=user, password=password)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def log(self, sender, message, channel):
        if len(message) > 512:
            message = message[:512]

        try:
            self.cursor.execute("INSERT INTO chat_log (sender, message, channel, date) VALUES (%s, %s, %s, %s)",
                                (sender, message, channel, current_time_in_milli()))
        except psycopg2.DataError as e:
            print e
            print message

