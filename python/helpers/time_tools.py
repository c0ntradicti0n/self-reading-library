import os
from contextlib import contextmanager
import time
import logging

logging.captureWarnings(True)


@contextmanager
def timeit_context(name, logger=logging.getLogger(__name__).info):
    start_time = time.time()
    yield
    elapsed_time = time.time() - start_time
    logger(f"... {int(elapsed_time * 1000)} ms for '{name}'")


def wait_for_change(path, f, logger=logging.getLogger(__name__), on_first=False):
    o_time = os.path.getmtime(path)
    while True:
        if os.path.getmtime(path) > o_time or on_first:
            logger.info(f"{path} changed, working!")
            try:
                o_time = os.path.getmtime(path)
                f()
            except Exception as e:
                logger.error(f"Exception on event for {path}", exc_info=True)
            on_first = False
        time.sleep(1)


import multiprocessing.pool
import functools

# https://stackoverflow.com/a/35139284
# https://stackoverflow.com/users/42897/rich
def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""

    def timeout_decorator(item):
        """Wrap the original function."""

        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)

        return func_wrapper

    return timeout_decorator
