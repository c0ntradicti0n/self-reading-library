import functools
import json
import logging
import os
from pprint import pprint


def file_persistent_cached_generator(filename, if_cache_then_finished=False, if_cached_then_forever=False):

    def decorator(original_func):

        def new_func(*param):
            cwd = os.getcwd()

            try:
                with open(filename, 'r') as f:
                    cache = list(f.readlines())

                cache = [tuple(json.loads(line)) for line in cache]
                cache = [(a if not isinstance(a, list) else tuple(a), b) for a, b in cache]
                try:
                    cache = dict(cache)
                except:
                    pass
            except (IOError, ValueError):
                cache = {}

            if isinstance(param[1], list) and (not if_cache_then_finished and cache):
                yield from apply_iterating_and_caching(cache, cwd, param, no_cache=True)
            else:
                if not if_cached_then_forever:
                    for res in cache:
                        yield from yield_cache(res, cwd)
                else:
                    for res, meta in cache:
                        print ("yielding")
                        yield res, meta

                if (not cache or not if_cache_then_finished):
                    yield from apply_iterating_and_caching(cache, cwd, param)

            os.chdir(cwd)

        def yield_cache(cache, cwd):
            for result in cache.items():
                os.chdir(cwd)
                yield result

        def apply_iterating_and_caching(cache, cwd, param, no_cache=False):
            generator = original_func(*param)#, cache=cache)


            for result in generator:

                result_string = json.dumps(result) + "\n"
                if no_cache or result_string not in cache:
                    content, meta = result

                    os.chdir(cwd)
                    with open(filename, 'a') as f:
                        f.write(result_string)
                    os.chdir(cwd)
                    yield content, meta

        functools.update_wrapper(new_func, original_func)

        return new_func

    return decorator

@file_persistent_cached_generator("test.cache")
def test(l):
    for i in l:
        yield i+1

if __name__ == "__main__":
    import os
    os.system("rm test*.cache")

    # first dummy run
    gen = test(range(10, 20, +1))
    [n for n in gen]

    # new run, returning old results also
    gen = test(range(30, 20, -1))

    result = [next(gen)  for i in range(20)]
    print (result)
    assert result == [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22]


def persist_to_file(file_name):

    def decorator(original_func):

        try:
            cache = json.load(open(file_name, 'r'))
        except (IOError, ValueError):
            cache = {}

        def new_func(*param):

            hash = str(list(
                {
                    k if any(isinstance(k, t) for t in [int, str, float]) else type(k):
                        v if any(isinstance(v, t) for t in [int, str, float]) else type(v)
                    for k, v in kv.__dict__.items()} if hasattr(kv, "__dict__") else str(kv)
                for kv in param))

            if hash not in cache:
                return_val = original_func(*param)
                cache[hash] = return_val

                json.dump(cache, open(file_name, 'w'))
                logging.info(f"Dumping {hash} to cache file {file_name}" )

            return cache[hash]

        return new_func

    return decorator
