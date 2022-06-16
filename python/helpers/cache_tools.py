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


def unroll_cache(path, cache):
    for m in cache:
        yield m, decompress_pickle(read_cache_file(path, m))


def filter_ant_step(gen, cache, filter_by_cache, path):
    try:
        for value, meta in gen:


            if not filter_by_cache:
                yield value, meta
            elif  str(value) not in cache \
                    and urllib.parse.quote_plus(str(value)) not in cache:
                yield value, meta

    except Exception as e:
        raise


def apply(cls, f, gen, cache, filter_by_cache, append_cache, filename, **kwargs):
    for result in f(cls, filter_ant_step(gen, cache, filter_by_cache, filename), **kwargs):

        should_yield = True
        if append_cache:
            print("logging to file")
            should_yield = write_cache(path=filename, result=result, old_cache=cache)

        if should_yield:
            yield result


def read_cache_file(path, value):
    try:
        with open(path + "/" + value, 'rb') as f:
            content = f.read()
            return content
    except Exception as e:
        logger.warning("Value was not encoded!")
        with open(path + "/" + urllib.parse.quote_plus(value), 'rb') as f:
            content = f.read()
        return content


def read_cache(path):
    if os.path.isfile(path):
        raise IOError(f"cache {path=} is a file, but should be a dict")
    if not os.path.isdir(path):
        os.mkdir(path)
        return []

    contents = os.listdir(path)

    new_cache = [
        urllib.parse.unquote_plus(key) for key in contents
    ]

    return new_cache


def write_cache(old_cache, path, result, overwrite_cache=False):
    try:
        value, meta = result
    except:
        raise IndexError(f"{result=} is not a value-meta tuple")

    if not isinstance(value, str):
        raise IndexError(f"Not a string {value=}")

    value = urllib.parse.quote_plus(value)
    old_cache.append(value)

    fpath = path + "/" + str(value)
    if os.path.exists(fpath):
        logger.error("Double writing cache")
        return False

    with open(fpath, "wb") as f:
        f.write(compressed_pickle(meta))
    return True


def configurable_cache(
        filename,
        from_path_glob=None,
        from_cache_only=False,
        from_cache_if_exists_else_run=False,
        from_function_only=False,
        dont_append_to_cache=False
):
    filename = filename.replace(".py", "")

    def decorator(original_func):
        def new_func(cls, source, from_path_glob=from_path_glob, **kwargs):

            _cls = cls if cls and cls.flags is not None else configurable_cache
            _from_cache_only = _cls.flags.get("from_cache_only", from_cache_only)
            _from_path_glob = _cls.flags.get("from_path_glob", from_path_glob)
            _from_function_only = _cls.flags.get("from_function_only", from_function_only)
            _dont_append_to_cache = _cls.flags.get("dont_append_to_cache", dont_append_to_cache)

            yield_cache = True if not _from_function_only else False
            yield_apply = not _from_cache_only and not _from_path_glob
            append_cache = not _dont_append_to_cache and not _from_path_glob
            filter_by_cache = not _from_function_only

            if _from_path_glob:
                if yield_cache:
                    if isinstance(_from_path_glob, str):
                        _from_path_glob = [_from_path_glob]
                    cache = [fp for path in _from_path_glob for fp in glob(path)]
                    if len(cache) == 0:
                        logging.info(f"Found nothing via glob {_from_path_glob} from {os.getcwd()}")
                    yield from [(p, {}) for p in cache]
                else:
                    yield from apply(cls, original_func, source, [], filter_by_cache, append_cache, filename, **kwargs)

            else:
                cache = read_cache(filename)

                if yield_cache:
                    yield from unroll_cache(filename, cache)
                if yield_apply:
                    yield from apply(
                        cls,
                        original_func,
                        source,
                        cache,
                        filter_by_cache,
                        append_cache if filter_by_cache else False,
                        filename,
                        **kwargs
                    )

        functools.update_wrapper(new_func, original_func)

        return new_func

    return decorator


configurable_cache.flags = {}

memory_caches = {}


def uri_with_cache(fun):
    def replacement_fun(self, req, resp, *args, **kwargs):
        global memory_caches

        if args:
            logging.debug("extra args", args)
        if kwargs:
            logging.debug("extra kwargs", kwargs)

        if not (fun, req) in memory_caches:
            logging.debug(req, resp, args, kwargs)
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

    def run_cached(self, x, filename, *args, f_=None, cargs=[], ckwargs={}, **kwargs):

        if not f_:
            @configurable_cache(filename=filename, *cargs, **ckwargs)
            def f(self, values_metas, *_, **__):
                for i, m in values_metas:
                    yield i, {
                        k:
                            not v if k == "bool" else v
                        for k, v in m.items()
                    }
        else:
            f = f_

        y = list(f(None, x, *args, **kwargs))
        return x, y, f

    def check_cached(self,
                     f,
                     x,
                     y,
                     filename,
                     *args,
                     **kwargs
                     ):
        logging.debug(f"Content of {os.getcwd()=} \n{os.listdir(os.getcwd())}")

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

    def test_keyword_arg(self):
        @configurable_cache(filename="t_k")
        def f(self, values_metas, depth="4"):
            for i, m in values_metas:
                yield i, {
                    k:
                        not v if k == "bool" else v
                    for k, v in m.items()
                }

        assert len(list(self.run_test_cache(
            [("1", {}), ("2", {}), ("3", {})],
            f_=f, filename="t_k"
        ))) == 3


if __name__ == "__main__":
    unittest.main()
