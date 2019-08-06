import argparse
import logging

from web_server.web_service import run


logger = logging.getLogger(__name__)


def get_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--port', nargs='?', default=9999, type=int,
        help="port for http server to bind to"
    )
    parser.add_argument(
        '-ttl', '--time-to-live', nargs='?', default=240, type=int,
        help="time for a browser session to live"
    )
    parser.add_argument(
        '-ld', '--logs-directory', nargs='?', type=str,
        help="Custom Logs Directory that should be passed to write the logs to that location "
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = get_arguments()

    run(args.port, args.time_to_live, args.logs_directory)
