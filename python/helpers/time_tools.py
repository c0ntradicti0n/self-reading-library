from contextlib import contextmanager
import time
import logging
logging.captureWarnings(True)


@contextmanager
def timeit_context(name, logger=print):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    logger(f"'{name}' finished in {int(elapsedTime * 1000)} ms'")