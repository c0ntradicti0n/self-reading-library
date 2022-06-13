import collections
import functools
import json
import logging
import shutil
import urllib
import zlib
from glob import glob
import falcon
import os
import unittest
import numpy

logger = logging.getLogger(__file__)
import _pickle as cPickle


def compressed_pickle(value):
    pvalue = cPickle.dumps(obj=value)
    cvalue = zlib.compress(pvalue)
    return cvalue


def decompress_pickle(value):
    try:
        pvalue = zlib.decompress(value)
        rvalue = cPickle.loads(data=pvalue)
        return rvalue
    except:
        logging.error(f"corrupted cache file {value=}")


def unroll_cache(cache):
    for result in cache.items():
        yield result


def filter_ant_step(gen, cache, key=None):
    try:
        for value, meta in gen:
            if urllib.parse.quote_plus(str(value) if not key else meta[key]) not in cache:
                yield value, meta

    except Exception:
        raise


def apply(cls, f, gen, cache, append_cache, filename):
    for result in f(cls, filter_ant_step(gen, cache)):

        should_yield = True
        if append_cache:
            should_yield = write_cache(path=filename, result=result, old_cache=cache)

        if should_yield:
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
        urllib.parse.unquote_plus(key): c for key in contents
        if (c := read_cache_file(path, key)) !=None
    }

    return new_cache


def write_cache(old_cache, path, result, overwrite_cache=False):
    try:
        value, meta = result
    except:
        raise IndexError(f"{result=} is not a value-meta tuple")

    if not isinstance(value, str):
        raise IndexError(f"{value=} is not a string")

    value = urllib.parse.quote_plus(value)
    old_cache[value] = compressed_pickle(meta)

    fpath = path + "/" + str(value)
    if os.path.exists(fpath):
        logger.error("double writing cache")
        return False

    with open(fpath, "wb") as f:
        f.write(old_cache[value])
    return True


def configurable_cache(
        filename,
        from_path_glob=None,
        from_cache_only=False,
        from_cache_if_exists_else_run=False,
        from_function_only=False,
        dont_append_to_cache=False
):
    def decorator(original_func):
        def new_func(cls, source, from_path_glob=from_path_glob):


            _cls = cls if cls and cls.flags != None else configurable_cache
            _from_cache_only = _cls.flags.get("from_cache_only", from_cache_only)
            _from_path_glob = _cls.flags.get("from_path_glob", from_path_glob)
            _from_function_only = _cls.flags.get("from_function_only", from_function_only)
            _dont_append_to_cache = _cls.flags.get("dont_append_to_cache", dont_append_to_cache)

            yield_cache = True if not _from_function_only else False
            yield_apply = not _from_cache_only and not _from_path_glob
            append_cache = not _dont_append_to_cache and not _from_path_glob

            if _from_path_glob:
                if isinstance(_from_path_glob, str):
                    _from_path_glob = [_from_path_glob]
                cache = {fp: {} for path in _from_path_glob for fp in glob(path)}
                if len(cache) == 0:
                    logging.info(f"Found nothing via glob {_from_path_glob} from {os.getcwd()}")
            else:
                cache = read_cache(filename)

            if yield_cache:
                yield from unroll_cache(cache)
            if yield_apply:
                yield from apply(cls, original_func, source, cache, append_cache, filename)

        functools.update_wrapper(new_func, original_func)

        return new_func

    return decorator
configurable_cache.flags = {}

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

    def run_cached(self, x, filename, *args, cargs=[], ckwargs={}, **kwargs):
        @configurable_cache(filename=filename, *cargs, **ckwargs)
        def f(self, values_metas, *_, **__):
            for i, m in values_metas:
                yield i, {
                    k:
                        not v if k == "bool" else v
                    for k, v in m.items()
                }

        _f = configurable_cache(filename=filename, *args, **kwargs)(f)

        y = list(f(None, x, *args, **kwargs))
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

        if not 'from_path_glob' in kwargs:
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

    def test_cache_glob(self):
        assert len(self.run_test_cache(None,
                                       from_path_glob='*.py',
                                       )) > 3

    def test_cache1_gen(self):
        assert len(list(self.run_test_cache(
            ((str(i), {}) for i in range(1, 4))
        ))) == 3

    def test_cache1_gen_multiple_times(self):
        assert len(list(self.run_test_cache(
            ((str(i), {}) for i in range(1, 4))
        ))) == 3
        assert len(list(self.run_test_cache(
            ((str(i), {}) for i in range(1, 4))
        ))) == 3
        assert len(list(self.run_test_cache(
            ((str(i), {}) for i in range(1, 4))
        ))) == 3

    def test_cached1_gen(self):
        assert len(list(self.run_test_cache(
            ((str(i), {}) for i in range(1, 4))
        ))) == 3
        assert len(list(self.run_test_cache(
            ((str(i), {}) for i in range(4, 7))
            , test_delete_cache_before=False))) == 6

    def test_cached1_gen_meta_numpy(self):
        assert len(list(self.run_test_cache(
            ((str(i), {"np": numpy.zeros((1, 3))}) for i in range(1, 4))
        ))) == 3
        assert len(list(self.run_test_cache(
            ((str(i), {}) for i in range(4, 7))
            , test_delete_cache_before=False))) == 6

    def test_cached1_not_doing_again(self):
        assert len(list(self.run_test_cache(
            ((str(i), {"bool": True}) for i in range(0, 3))
        ))) == 3
        res = list(self.run_test_cache(
            ((str(i), {"bool": True}) for i in range(2, 4))
            , test_delete_cache_before=False))
        assert len(res) == 4
        assert all((c == 1 for e, c in collections.Counter([int(k) for k, m in res]).items()))
        assert all((not r[1]['bool'] for r in res))

    def test_cache1_list(self):
        assert len(list(self.run_test_cache(
            [("1", {}), ("2", {}), ("3", {})]
        ))) == 3

    def test_cached1_list(self):
        assert len(list(self.run_test_cache(
            [("1", {}), ("2", {}), ("3", {})]
        ))) == 3
        assert len(list(self.run_test_cache(
            [("4", {}), ("5", {}), ("6", {})]
            , test_delete_cache_before=False))) == 6

    def test_cache_only(self):
        assert len(list(self.run_test_cache(
            [("1", {}), ("2", {}), ("3", {})]
        ))) == 3
        assert len(list(self.run_test_cache(
            [("4", {}), ("5", {}), ("6", {})]
            , test_delete_cache_before=False, ckwargs={'from_cache_only': True}))) == 3

    def test_function_only(self):
        assert len(list(self.run_test_cache(
            [("1", {}), ("2", {}), ("3", {})]
        ))) == 3
        assert len(list(self.run_test_cache(
            [("4", {}), ("5", {}), ("6", {})]
            , test_delete_cache_before=False, ckwargs={'from_function_only': True}))) == 3

    def test_uncompress_decompress(self):
        decompress_pickle(compressed_pickle([1, 2, 3, 4])) == [1, 2, 3, 4]


if __name__ == "__main__":
    unittest.main()
