import sys
import logging
import time
from datetime import datetime

from headless_api.gst_portal_mapper import GSTPortalMapper
from headless_api.entities import BrowserSession


logger = logging.getLogger(__name__)


def stale_check(ps, check_interval=30, logs_directory=None):

    logger.setLevel(logging.INFO)

    if not logs_directory:
        logger.addHandler(logging.StreamHandler(sys.stdout))
    else:
        log_path = os.path.join(logs_directory, "memory_corrector.log")
        logger.addHandler(logging.FileHandler(log_path))

    while 1:
        ts_now = datetime.now()
        logger.info("Running stale check at: {}".format(
            ts_now.strftime("%Y-%m-%d %H:%M")
        ))

        for token, data in ps.items():
            ts = data['ts']

            t_delta = ts_now - ts
            if t_delta.total_seconds() > 900:
                session_url = data['session_url']
                browser_session = BrowserSession(
                    session_url,
                    token
                )
                gpm = GSTPortalMapper(browser_session)
                gpm.cleanup()
                del ps[token]
                logger.info("Wiped token: {}".format(token))

        time.sleep(check_interval)
