import argparse
import multiprocessing
import logging
import os
import sys

from web_server.web_service import run
from memory_corrector.memory_corrector import stale_check


logger = logging.getLogger(__name__)

def get_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--port', nargs='?', default=9999, type=int,
        help="port for http server to bind to"
    )
    parser.add_argument(
        '-mcd', '--memory-corrector-delay', nargs='?', default=30, type=int,
        help="Delay between picking up queued mail items"
    )
    parser.add_argument(
        '-ld', '--logs-directory', nargs='?', type=str,
        help="Custom Logs Directory that should be passed to write the logs to that location "
    )
    return parser.parse_args()

if __name__ == '__main__':

    args = get_arguments()

    logger.setLevel(logging.INFO)

    if not args.logs_directory:
        logger.addHandler(logging.StreamHandler(sys.stdout))
    else:
        log_path = os.path.join(args.logs_directory, "master.log")
        logger.addHandler(logging.FileHandler(log_path))

    manager = multiprocessing.Manager()
    persistent_store = manager.dict()

    web_service_p = multiprocessing.Process(
        target=run, args=(persistent_store, args.port, args.logs_directory)
    )
    web_service_p.daemon = True
    web_service_p.start()
    logger.info("Starting web service")

    stale_check_p = multiprocessing.Process(
        target=stale_check, args=(persistent_store, args.memory_corrector_delay)
    )
    stale_check_p.daemon = True
    stale_check_p.start()
    logger.info("Starting memory corrector")

    web_service_p.join()
    stale_check_p.join()
