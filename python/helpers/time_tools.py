import os
from contextlib import contextmanager
import time
import logging

logging.captureWarnings(True)


@contextmanager
def timeit_context(name, logger=logging.getLogger(__name__)):
    start_time = time.time()
    yield
    elapsed_time = time.time() - start_time
    logger.info(f"... {int(elapsed_time * 1000)} ms for '{name}'")


def wait_for_change(path, f, logger=logging.getLogger(__name__)):
    o_time = os.path.getmtime(path)
    while True:
        if os.path.getmtime(path) > o_time:
            logger.info(f"{path} changed, working!")
            try:
                f()
            except Exception as e:
                logger.error(f"Exception on event for {path}", exc_info=True)
            o_time = os.path.getmtime(path)
        time.sleep(1)
