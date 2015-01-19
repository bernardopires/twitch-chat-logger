import sys
from manager import TwitchManager
from optparse import OptionParser


def main():
    parser = OptionParser()
    parser.add_option("-n", "--streams-to-log", dest="streams_to_log", type="int",
                      help="the number of streams to log", default=100)
    parser.add_option("-f", "--log-filename", dest="log_filename",
                      help="the filename to log to", default=None)
    (options, args) = parser.parse_args()

    manager = TwitchManager(streams_to_log=options.streams_to_log, log_filename=options.log_filename)
    try:
        manager.run_log_loop()
    except KeyboardInterrupt:
        print 'Exiting gracefully...'
        manager.stop_bot()

if __name__ == "__main__":
    main()
