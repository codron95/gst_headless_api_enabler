import os
import sys
import logging
from datetime import datetime

from urllib3.exceptions import MaxRetryError

from headless_api.gst_portal_mapper import GSTPortalMapper


logger = logging.getLogger(__name__)


def destroy_sessions(expired_drivers, logs_directory=None):

    logger.setLevel(logging.INFO)

    if not logs_directory:
        logger.addHandler(logging.StreamHandler(sys.stdout))
    else:
        log_path = os.path.join(logs_directory, "memory_corrector.log")
        logger.addHandler(logging.FileHandler(log_path))

    ts_now = datetime.now()
    logger.info("Forked memory corrector at: {}".format(
        ts_now.strftime("%Y-%m-%d %H:%M")
    ))

    for token, driver in expired_drivers.items():

        try:
            gpm = GSTPortalMapper(expired_drivers[token])
        except MaxRetryError:
            pass
        else:
            gpm.cleanup()
        finally:
            logger.info("Wiped token: {}".format(token))
