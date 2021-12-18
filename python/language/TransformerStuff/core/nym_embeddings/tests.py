from contextlib import contextmanager
from random import shuffle
from time import time

from nym_embeddings import memoizedstringsynsettisation


@contextmanager
def timing(description: str) -> None:
    start = time()
    yield
    ellapsed_time = time() - start

    print(f"{description}: {ellapsed_time}")


sample = """Note While this decorator makes it easy to create well behaved totally ordered types, it does come at the cost of slower execution and more complex stack traces for the derived comparison methods. If performance benchmarking indicates this is a bottleneck for a given application, implementing all six rich comparison methods instead is likely to provide an easy speed boost."""

with timing("lemmatize 1"):
    memoizedstringsynsettisation.lazy_lemmatize(sample)

with timing("lemmatize 2"):
    memoizedstringsynsettisation.lazy_lemmatize(sample)

with open("hamlet.txt") as f:
    texts = f.readlines()

with timing("lemmatize list 1"):
    synseted_texts = [memoizedstringsynsettisation.lazy_lemmatize(t) for t in texts]

shuffle(texts)
with timing("lemmatize list 2"):
    synseted_texts = [memoizedstringsynsettisation.lazy_lemmatize(t) for t in texts]

from guppy3 import hpy
print(hpy.heap())