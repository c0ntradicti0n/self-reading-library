
import json
import logging

def file_persistent_cached_generator(filename):

    def decorator(original_func):

        def new_func(*param):

            try:
                with open(filename, 'r') as f:
                    cache = list(f.readlines())
            except (IOError, ValueError):
                cache = []

            for result in cache:
                yield json.loads(result)

            generator = original_func(*param)

            for result in generator:
                with open(filename, 'a') as f:
                    f.write( json.dumps(result) + "\n")
                yield result

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
    gen = test(range(20, 10, -1))

    result = [next(gen)  for i in range(20)]
    print (result)
    assert result == [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12]


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
