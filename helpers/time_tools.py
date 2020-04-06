from contextlib import contextmanager
import time
import logging
logging.captureWarnings(True)
logging.getLogger().setLevel(logging.INFO)


@contextmanager
def timeit_context(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print ('[{}] finished in {} ms'.format(name, int(elapsedTime * 1000)))