import functools
import itertools
import json
import logging
from glob import glob
import falcon
import os
import unittest


def file_persistent_cached_generator(
        filename,
        **kwargs):
    def decorator(original_func):
        standard_flags = kwargs

        def new_func(*param):

            cwd = os.getcwd()

            flags = standard_flags.copy()
            flags.update(param[0].flags)
            load_via_glob = flags['load_via_glob'] if 'load_via_glob' in flags else None
            if_cache_then_finished = flags['if_cache_then_finished'] if 'if_cache_then_finished' in flags else False
            if_cached_then_forever = flags['if_cached_then_forever'] if 'if_cached_then_forever' in flags else False
            dont_use_cache = flags['dont_use_cache'] if 'dont_use_cache' in flags else False

            if_cache_then_finished = flags['dont_use_cache'] if 'dont_use_cache' in flags else if_cache_then_finished
            if_cached_then_forever = flags['dont_use_cache'] if 'dont_use_cache' in flags else if_cached_then_forever

            if dont_use_cache:
                cache = {}
            else:
                try:
                    with open(filename, 'r') as f:
                        cache = list(f.readlines())

                    if load_via_glob:
                        if isinstance(load_via_glob, str):
                            load_via_glob = [load_via_glob]
                        cache = [f'["{fp}", {"{}"} ]' for path in load_via_glob for fp in glob(path)]

                    cache = [tuple(json.loads(line)) for line in cache]
                    cache = [(a if not isinstance(a, list) else tuple(a), b) for a, b in cache]
                    try:
                        cache = dict(cache)
                    except:
                        pass
                except (IOError, ValueError):
                    cache = {}

            if isinstance(param[1], list) and (not if_cache_then_finished and cache):
                yield from apply_and_cache(cache, cwd, param, no_cache=True)
            else:
                if not if_cached_then_forever:
                    yield from yield_cache(cache, cwd)
                else:
                    for res, meta in cache:
                        yield res, meta

                if (not cache or not if_cache_then_finished):
                    yield from apply_and_cache(cache, cwd, param, no_cache=dont_use_cache)

            os.chdir(cwd)

        def yield_cache(cache, cwd):

            if isinstance(cache, dict):
                for result in cache.items():
                    os.chdir(cwd)
                    yield result

            if isinstance(cache, list):
                for result in cache:
                    os.chdir(cwd)
                    yield result

        def apply_and_cache(cache, cwd, param, no_cache=False):
            generator = original_func(*param)

            for result in generator:
                try:
                    result_string = json.dumps(result) + "\n"
                    if no_cache or result_string not in cache:
                        content, meta = result

                        os.chdir(cwd)

                        if os.path.exists(filename):
                            append_write = 'a'  # append if already exists
                        else:
                            append_write = 'w'  # make a new file if not

                        with open(filename, append_write) as f:
                            f.write(result_string)
                        os.chdir(cwd)
                    yield content, meta
                except Exception as e:
                    logging.error(
                        f"{str(e)} while computing on \n {str(result)}\n in {str(original_func)}\n being in {os.getcwd()}")
                    raise e

        functools.update_wrapper(new_func, original_func)

        return new_func

    return decorator


def unroll_cache(cache, cwd):
    for result in cache.items():
        os.chdir(cwd)
        yield result


def apply(cache, cwd, param):
    generator = original_func(*param)  # , cache=cache)

    for result in generator:
        try:
            result_string = json.dumps(result) + "\n"
            content, meta = result
            yield content, meta
        except Exception as e:
            logging.error(
                f"{str(e)} while computing on \n {str(result)}\n in {str(original_func)}\n being in {os.getcwd()}")
            raise e

def write_cache(path, gen, cwd, overwrite_cache = False):
    if os.path.exists(path):
        append_write = 'a'  # append if already exists
    else:
        append_write = 'w'  # make a new file if not

    if overwrite_cache:
        append_write = "w"
    for result in gen:
        os.chdir(cwd)

        with open(path, append_write) as f:
            f.write(result_string)
        os.chdir(cwd)

        yield result
        append_write = 'a'

def configurable_cache(
        filename,
        overwrite_cache = None,
        load_via_glob=None,
        cache_only=False,
        dont_add_to_cache=False,
        dont_use_more_then_cache=False,
        apply_only=False,
        cycle_cache_or_compute=False
):
    def decorator(original_func):
        def new_func(*param, load_via_glob=load_via_glob):
            # consts
            cwd = os.getcwd()
            new_func.cache_path = cwd + "/" + filename

            # flags
            if load_via_glob or cache_only or dont_use_more_then_cache:
                yield_cache = True
                yield_apply = False

            if load_via_glob:
                write_down_cache = True
            else:
                write_down_cache = False
            # load
            try:
                with open(new_func.cache_path, 'r') as f:
                    cache = list(f.readlines())
            except FileNotFoundError:
                logging.warning(f"No cache found for {new_func.cache_path}, creating new one")
                cache = {}

            if load_via_glob:
                if isinstance(load_via_glob, str):
                    load_via_glob = [load_via_glob]
                cache = [f'["{fp}", {"{}"} ]' for path in load_via_glob for fp in glob(path)]
                if len(cache) == 0:
                    logging.info(f"Found nothing via glob {load_via_glob} from {cwd}")

            cache = [tuple(json.loads(line)) for line in cache]
            cache = [(a if not isinstance(a, list) else tuple(a), b) for a, b in cache]
            try:
                cache = dict(cache)
            except:
                pass

            if len(param) <= 1:
                logging.warning(f"Second attribute 'meta' was not given for {original_func}")

            # flags 2

            if cycle_cache_or_compute:
                if cache:
                    yield_cache = True
                    yield_apply = False
                else:
                    yield_cache = False
                    yield_apply = True



            if not yield_apply and not yield_cache:
                raise AssertionError("Some kind of cache result must be calculated! Bad "
                                     "handling of flags occurred")
            # produce
            gens = []

            if yield_cache:
                gens += unroll_cache(cache, cwd)
            if yield_apply:
                gens += apply(cache, cwd, param, no_cache=False)


            gens = itertools.chain.from_iterable(gens)

            if write_down_cache:
                gen = write_cache(gen = gens, cwd=cwd, path=new_func.cache_path)

            yield from gen
            os.chdir(cwd)

        functools.update_wrapper(new_func, original_func)

        return new_func

    return decorator


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
                logging.warning(f"Dumping {hash} to cache file {file_name}")

            return cache[hash]

        return new_func

    return decorator


memory_caches = {}


def uri_with_cache(fun):
    def replacement_fun(self, req, resp, *args, **kwargs):
        global memory_caches

        if args:
            print("extra args", args)
        if kwargs:
            print("extra kwargs", kwargs)

        if not (fun, req) in memory_caches:
            print(req, resp, *args, **kwargs)
            memory_caches[fun] = "working..."
            res = fun(self, req, resp)
            memory_caches[(fun, req)] = res
            if res == None:
                fun.cache = "No result was returned"
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({"response": res, "status": resp.status})

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"response": memory_caches[(fun, req)], "status": resp.status})

    return replacement_fun


class TestCache(unittest.TestCase):

    def run_cached(self, x, *args, f=None, fargs=[], fkwargs={}, **kwargs):
        if not f:
            @configurable_cache("test.cache", *args, **kwargs)
            def f(values_metas, *fargs, **fkwrags):
                for i in values_metas:
                    yield i + 1, m
        else:
            f = configurable_cache("test.cache", *args, **kwargs)(f)

        y = list(f(x, *fargs, **fkwargs))
        return y, f

    def check_cached(self,
                      f,
                      x,
                      y,
                      exists=True,
                      all_values_in=True,
                      cargs=[],
                      ckwargs={}
                      ):

        if "load_via_glob" in ckwargs:
           pass

        if "cache_only" in ckwargs:
            pass

        if "dont_add_to_cache" in ckwargs:
            pass

        if "apply_only" in ckwargs:
            pass

        if "cycle_cache_or_compute" in ckwargs:
            pass

        if exists:
            assert os.path.isfile(f.cache_path)

            try:
                with open(f.cache_path, "r") as fc:
                    content  = fc.read()
            except FileNotFoundError as e:
                raise e
            try:
                cache = json.loads(content)
            except Exception as e:
                raise AssertionError(f"Cache '{f.cache_path}' with content \n\t'{str(content[:100])}' \n\tnot in readable format " + str(e))

            assert (isinstance(cache, dict))

            if contains_values:
                assert all((m in cache for m in contains_values))
        else:
            assert not os.path.exists(f.cache_path)

            assert len(z) == len(x)

    def run_test_cache(self
                   ,x, *cargs, f=None, fargs=[], fkwargs={}, **ckwargs):
        y, f = self.run_cached(
            *cargs,
            f=f,
            x=x,
            fargs=fargs,
            fkwargs=fkwargs,
            **ckwargs
        )
        self.check_cached(
            f=f,
            x=x,
            y=y,
            exists=True,
            all_values_in=True,
            cargs=cargs,
            ckwargs=ckwargs
        )

    def test_cache_via_glob(self):
        assert (self.run_test_cache([1, 2, 3],
                                 load_via_glob='../test/*.pdf',
                                 )) > 3

    def test_cache1(self):
        assert len(list(self.run_test_cache(
            [(1, {}), (2, {}), (3, {})],
            load_via_glob='../../test/*.pdf',
        ))) > 3


if __name__ == "__main__":
    unittest.main()
