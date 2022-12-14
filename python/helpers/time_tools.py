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
