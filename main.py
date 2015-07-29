import argparse
import sys
from manager import TwitchManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--streams-to-log", dest="streams_to_log", type=int,
                      help="the number of streams to log", default=100)
    parser.add_argument("-f", "--log-filename", dest="log_filename",
                      help="the filename to log to", default=None)
    args = parser.parse_args()

    manager = TwitchManager(streams_to_log=args.streams_to_log, log_filename=args.log_filename)
    try:
        manager.run_log_loop()
    except KeyboardInterrupt:
        print 'Exiting gracefully...'
        manager.stop_bot()

if __name__ == "__main__":
    main()
