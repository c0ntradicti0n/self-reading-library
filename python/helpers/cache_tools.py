import collections
import functools
import itertools
import json
import logging
import pickle
import shutil
import types
import zlib
from glob import glob
import falcon
import os
import unittest

import numpy

from helpers.lazy import lazy

logger = logging.getLogger(__file__)


def compressed_pickle(value):
    pvalue = pickle.dumps(obj=value)
    cvalue = zlib.compress(pvalue)
    return cvalue


def decompress_pickle(value):
    try:
        pvalue = zlib.decompress(value)
        rvalue = pickle.loads(data=pvalue)
        return rvalue
    except:
        raise


def file_persistent_cached_generator(
        filename,
        key=None,
        **kwargs):
    def decorator(original_func):
        standard_flags = kwargs

        def new_func(*param):

            try:
                cwd = os.getcwd()

                flags = standard_flags.copy()
                flags.update(param[0].flags)
                load_via_glob = flags['load_via_glob'] if 'load_via_glob' in flags else None
                if_cache_then_finished = flags['if_cache_then_finished'] if 'if_cache_then_finished' in flags else False
                if_cached_then_forever = flags['if_cached_then_forever'] if 'if_cached_then_forever' in flags else False
                dont_use_cache = flags['dont_use_cache'] if 'dont_use_cache' in flags else False

                if_cache_then_finished = flags[
                    'dont_use_cache'] if 'dont_use_cache' in flags else if_cache_then_finished
                if_cached_then_forever = flags[
                    'dont_use_cache'] if 'dont_use_cache' in flags else if_cached_then_forever

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

                if len(param) > 2 and isinstance(param[1], list) and (not if_cache_then_finished and cache):
                    yield from apply_and_cache(cache, cwd, param, no_cache=True)
                elif if_cached_then_forever:
                    yield from yield_cache(cache, cwd)
                else:
                    yield from yield_cache(cache, cwd)
                    yield from apply_and_cache(cache, cwd, param, no_cache=dont_use_cache, key=key)

                os.chdir(cwd)
            except Exception as e:
                logging.error(e, exc_info=True)
                raise e

        def yield_cache(cache, cwd):

            if isinstance(cache, dict):
                for result in cache.items():
                    os.chdir(cwd)
                    yield result

            if isinstance(cache, list):
                for result in cache:
                    os.chdir(cwd)
                    yield result

        def apply_and_cache(cache, cwd, param, no_cache=False, key=None):
            if isinstance(param[1], types.GeneratorType):
                filtered_param = (param[0], filter_ant_step(param[1], cache, key=key))
            else:
                filtered_param = param

            generator = original_func(*filtered_param)

            for result in generator:
                try:

                    if key and result[1][key] in cache:
                        yield result[0], cache[result[0]]
                        continue

                    result_string = json.dumps(result) + "\n"
                    if no_cache or result_string not in cache:
                        try:
                            content, meta = result
                        except:
                            raise

                        done = False
                        while not done:
                            try:

                                if os.path.exists(filename):
                                    append_write = 'a'  # append if already exists
                                else:
                                    append_write = 'w'  # make a new file if not

                                with open(filename, append_write) as f:
                                    f.write(result_string)

                            except FileNotFoundError:
                                logging.error("multithreading file not found error...")
                                continue
                            done = True

                    yield content, meta
                except Exception as e:
                    logging.error(
                        f"{str(e)} while computing on \n {str(result)}\n in {str(original_func)}\n being in {os.getcwd()}")
                    raise e

        functools.update_wrapper(new_func, original_func)

        return new_func

    return decorator


def unroll_cache(cache):
    for result in cache.items():
        yield result


def filter_ant_step(gen, cache, key=None):
    try:
        for value, meta in gen:
            if (str(value) if not key else meta[key]) not in cache:
                yield value, meta

    except Exception:
        print(f"{gen=} {cache=} {key=}")
        raise


def apply(f, gen, cache):
    for result in f(filter_ant_step(gen, cache)):
        yield result


def read_cache_file(path, value):
    with open(path + "/" + value, 'rb') as f:
        content = f.read()
        return decompress_pickle(content)


def read_cache(path):
    if os.path.isfile(path):
        raise IOError(f"cache {path=} is a file, but should be a dict")
    if not os.path.isdir(path):
        os.mkdir(path)
        return {}

    contents = os.listdir(path)

    new_cache = {
        key: read_cache_file(path, key) for key in contents
    }

    return new_cache


def write_cache(old_cache, path, result, overwrite_cache=False):
    try:
        value, meta = result
    except:
        raise IndexError(f"{result=} is not a value-meta tuple")
    old_cache[value] = compressed_pickle(meta)

    fpath = path + "/" + str(value)
    if os.path.exists(fpath):
        logger.error(".")
        return

    with open(fpath, "wb") as f:
        f.write(old_cache[value])


def configurable_cache(
        filename,
        from_path_blob=None,
        from_cache_only=False,
        from_cache_if_exists_else_run=False,
        from_function_only=False,
        dont_append_to_cache=False
):
    def decorator(original_func):
        def new_func(source, from_path_blob=from_path_blob):
            yield_cache = True if not from_function_only else False
            yield_apply = not from_cache_only and not from_path_blob
            append_cache = not dont_append_to_cache and not from_path_blob

            if from_path_blob:
                if isinstance(from_path_blob, str):
                    from_path_blob = [from_path_blob]
                cache = {fp: {} for path in from_path_blob for fp in glob(path)}
                if len(cache) == 0:
                    logging.info(f"Found nothing via glob {from_path_blob} from {os.getcwd()}")
            else:
                cache = read_cache(filename)

            combine_gens = []
            if yield_cache:
                combine_gens += unroll_cache(cache)
            if yield_apply:
                combine_gens += apply(original_func, source, cache)

            gens = itertools.chain.from_iterable([combine_gens])

            for result in gens:
                if append_cache:
                    write_cache(path=filename, result=result, old_cache=cache)
                yield result

        functools.update_wrapper(new_func, original_func)

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
            print(req, resp, args, kwargs)
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

    def run_cached(self, x, filename,  *args,  cargs=[], ckwargs={},**kwargs):
        @configurable_cache(filename=filename, *cargs, **ckwargs)
        def f(values_metas, *_, **__):
            for i, m in values_metas:
                yield i, {
                    k:
                        not v if k == "bool" else v
                    for k, v in m.items()
                }

        _f = configurable_cache(filename=filename, *args, **kwargs)(f)

        y = list(f(x, *args, **kwargs))
        return x, y, _f

    def check_cached(self,
                     f,
                     x,
                     y,
                     filename,
                     *args,
                     **kwargs
                     ):
        print(f"content of {os.getcwd()=} \n{os.listdir(os.getcwd())}")

        if not 'from_path_blob' in kwargs:
            assert os.path.exists(filename)

    def run_test_cache(self
                       , gen, filename="test_cache", *args, test_delete_cache_before=True, **kwargs):

        if test_delete_cache_before:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
            except IsADirectoryError:
                shutil.rmtree(filename)

        x, y, f = self.run_cached(
            gen, filename=filename, *args, **kwargs
        )
        self.check_cached(
            x, y, f, filename=filename, *args, **kwargs
        )
        print(y)
        return y

    def test_cache_blob(self):
        assert len(self.run_test_cache(None,
                                    from_path_blob='*.py',
                                    )) > 3

    def test_cache1_gen(self):
        assert len(list(self.run_test_cache(
            ((i, {}) for i in range(1, 4))
        ))) == 3

    def test_cached1_gen(self):
        assert len(list(self.run_test_cache(
            ((i, {}) for i in range(1, 4))
        ))) == 3
        assert len(list(self.run_test_cache(
            ((i, {}) for i in range(4, 7))
            , test_delete_cache_before=False))) == 6

    def test_cached1_gen_meta_numpy(self):
        assert len(list(self.run_test_cache(
            ((i, {"np": numpy.zeros((1, 3))}) for i in range(1, 4))
        ))) == 3
        assert len(list(self.run_test_cache(
            ((i, {}) for i in range(4, 7))
            , test_delete_cache_before=False))) == 6

    def test_cached1_not_doing_again(self):
        assert len(list(self.run_test_cache(
            ((str(i), {"bool": True}) for i in range(0, 3))
        ))) == 3
        res = list(self.run_test_cache(
            ((str(i), {"bool": True}) for i in range(2, 4))
            , test_delete_cache_before=False))
        assert len(res) == 4
        assert all((c==1 for e, c in collections.Counter([int(k) for k, m in res]).items()))
        assert all((not r[1]['bool'] for r in res))

    def test_cache1_list(self):
        assert len(list(self.run_test_cache(
            [(1, {}), (2, {}), (3, {})]
        ))) == 3

    def test_cached1_list(self):
        assert len(list(self.run_test_cache(
            [(1, {}), (2, {}), (3, {})]
        ))) == 3
        assert len(list(self.run_test_cache(
            [(4, {}), (5, {}), (6, {})]
            , test_delete_cache_before=False))) == 6

    def test_cache_only(self):
        assert len(list(self.run_test_cache(
            [(1, {}), (2, {}), (3, {})]
        ))) == 3
        assert len(list(self.run_test_cache(
            [(4, {}), (5, {}), (6, {})]
            , test_delete_cache_before=False, ckwargs={'from_cache_only':True}))) == 3

    def test_function_only(self):
        assert len(list(self.run_test_cache(
            [(1, {}), (2, {}), (3, {})]
        ))) == 3
        assert len(list(self.run_test_cache(
            [(4, {}), (5, {}), (6, {})]
            , test_delete_cache_before=False, ckwargs={'from_function_only':True}))) == 3


    def test_uncompress_decompress(self):
        decompress_pickle(compressed_pickle([1, 2, 3, 4])) == [1, 2, 3, 4]


if __name__ == "__main__":
    unittest.main()
