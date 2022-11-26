import collections
import functools
import json
import logging
import shutil
import types
import urllib
import zlib
from glob import glob
from typing import Callable, Iterable

import falcon
import os
import unittest
import numpy
from regex import regex

from config import config
from helpers.os_tools import filename_only

logger = logging.getLogger(__file__)
import _pickle as cPickle


def compressed_pickle(value):
    pvalue = cPickle.dumps(obj=value)
    cvalue = zlib.compress(pvalue)
    return cvalue


def decompress_pickle(value):
    try:
        pvalue = zlib.decompress(value)
        rvalue = cPickle.loads(pvalue)
        return rvalue
    except:
        logging.error(f"corrupted cache file {value=}", exc_info=True)


def unroll_cache(path, cache):
    for m in cache:
        uncompressed = decompress_pickle(read_cache_file(path, m))
        if uncompressed:
            yield m, uncompressed


def filter_ant_step(gen, cache, filter_by_cache):
    try:
        for value, meta in gen:

            if not filter_by_cache:
                yield value, meta
            elif (
                str(value) not in cache
                and urllib.parse.quote_plus(str(value)) not in cache
            ):
                yield value, meta

    except Exception as e:
        raise


def apply(cls, f, gen, cache, filter_by_cache, append_cache, filename, **kwargs):
    for result in yield_cache_instead_apply(
        cls, f, filter_ant_step(gen, cache, filter_by_cache), cache, filename, **kwargs
    ):
        write_cache(path=filename, result=result, old_cache=cache)

        yield result


def dig_generator_ground_for_next_value(gen):
    gen_or_val = next(
        (
            subgen
            for k, subgen in gen.gi_frame.f_locals.items()
            if isinstance(subgen, types.GeneratorType)
        ),
        gen.gi_frame,
    )
    if isinstance(gen_or_val, types.GeneratorType):
        return dig_generator_ground_for_next_value(gen_or_val)
    else:
        val = gen_or_val.f_locals
        if "l" in val:
            return val["l"]
        else:
            return []


def yield_cache_instead_apply(cls, f, gen, cache, cache_folder, **kwargs):
    try:
        incoming_gen = dig_generator_ground_for_next_value(gen)
        if not "itertools.cycle" in str(incoming_gen):
            values_from_future = [v for v in incoming_gen if v]
        else:
            values_from_future = []
    except Exception as e:
        raise e

    if values_from_future:
        future_yield_values = [
            (
                value,
                decompress_pickle(
                    read_cache_file(
                        cache_folder,
                        value
                        if value.endswith(".pdf")
                        else config.tex_data + urllib.parse.quote_plus(value) + ".pdf",
                    )
                ),
            )
            for value in values_from_future
            if value in cache
            or urllib.parse.quote_plus(value) in cache
            or config.tex_data + urllib.parse.quote_plus(value) + ".pdf" in cache
        ]
    else:
        future_yield_values = []
    if future_yield_values:
        yield from future_yield_values

    if not values_from_future or len(future_yield_values) != len(values_from_future):
        cache_values_to_yield = []

        def filter():
            for value, m in gen:
                if value in [k for k, v in cache_values_to_yield]:
                    continue
                if value:
                    if urllib.parse.quote_plus(value) in cache:
                        logging.info(
                            f"{value} was in cache, yielding that one instead of applying"
                        )
                        cache_values_to_yield.append(
                            (
                                value,
                                decompress_pickle(
                                    read_cache_file(
                                        cache_folder, urllib.parse.quote_plus(value, "")
                                    )
                                ),
                            )
                        )
                    elif value in cache:
                        logging.info(
                            f"{value} was in cache, yielding that one instead of applying"
                        )
                        cache_values_to_yield.append(
                            (
                                value,
                                decompress_pickle(read_cache_file(cache_folder, value)),
                            )
                        )

                    elif value in future_yield_values:
                        logging.info("value was yielded before from future cache")
                    else:
                        yield value, m
                else:
                    logging.error("Value in cache was None, retrying")
                    yield value, m

        yield from f(cls, filter(), **kwargs)
        yield from (
            (k, v) for k, v in cache_values_to_yield if k not in future_yield_values
        )


def read_cache_file(path, value):

    try:
        with open((path + "/" if path else "") + value, "rb") as f:
            content = f.read()
            return content
    except Exception as e:
        print(e)
        with open(path + "/" + urllib.parse.quote_plus(value), "rb") as f:
            content = f.read()
        return content


def read_cache(path):
    if os.path.isfile(path):
        raise IOError(f"cache {path=} is a file, but should be a dict")
    if not os.path.isdir(path):
        if not os.path.isdir(config.cache):
            try:
                os.mkdir(config.cache)
            except:
                logging.warning(
                    f"Could not create cache dir {config.cache} (probably race conditions)"
                )

        try:
            os.mkdir(path)
        except:
            logging.warning(
                f"Could not create cache dir {path} (probably race conditions)"
            )
        return []

    contents = os.listdir(path)

    new_cache = [key for key in contents]

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
    filter_path_glob=None,
    from_cache_only=False,
    from_cache_if_exists_else_run=False,
    from_function_only=False,
    dont_append_to_cache=False,
):
    filename = filename.replace(".py", "")

    def decorator(original_func):
        def new_func(
            self,
            source,
            from_path_glob=from_path_glob,
            filter_path_glob=filter_path_glob,
            **kwargs,
        ):

            self = self if self and self.flags is not None else configurable_cache
            _from_cache_only = self.flags.get("from_cache_only", from_cache_only)
            _from_path_glob = self.flags.get("from_path_glob", from_path_glob)
            _filter_path_glob = self.flags.get("filter_path_glob", filter_path_glob)

            _from_function_only = self.flags.get(
                "from_function_only", from_function_only
            )
            _dont_append_to_cache = self.flags.get(
                "dont_append_to_cache", dont_append_to_cache
            )

            yield_cache = True if not _from_function_only else False
            yield_apply = not _from_cache_only and not _from_path_glob
            append_cache = True
            filter_by_cache = not _from_function_only
            cache = read_cache(filename)

            if _from_path_glob:
                if not os.path.isdir(filename):
                    try:
                        os.mkdir(filename)
                    except:
                        logging.error(
                            f"Could not create cache file for {filename} (race conditions)"
                        )
                if yield_cache:
                    if isinstance(_from_path_glob, str) or callable(_from_path_glob):
                        _from_path_glob = [_from_path_glob]
                    cache = [
                        fp
                        for path in _from_path_glob
                        for fp in glob(path if not callable(path) else path(self))
                    ]

                    cache.sort(key=os.path.getctime)
                    cache.reverse()

                    blacklist = []
                    if not isinstance(_filter_path_glob, Iterable):
                        _filter_path_glob = [_filter_path_glob]
                    if not _filter_path_glob:
                        _filter_path_glob = []
                    for i, p in enumerate(_filter_path_glob):
                        if isinstance(p, Callable):
                            result = p(self)
                            if isinstance(result, str):
                                _filter_path_glob[i] = result
                            elif isinstance(result, Iterable):
                                result = [filename_only(r) for r in result]
                                blacklist.extend(result)
                                _filter_path_glob[i] = None
                            else:
                                logging.error(
                                    f"dont know how to handle filter return type, {result}"
                                )
                    blacklist += [
                        filename_only(os.path.basename(fp))
                        for path in _filter_path_glob
                        if path
                        for fp in glob(path)
                    ]

                    if len(cache) == 0:
                        logging.info(
                            f"Found nothing via glob {_from_path_glob} from {os.getcwd()}"
                        )

                    blacklisted = [p for p in cache if filename_only(p) in blacklist]
                    logging.warning(f"{blacklisted=} {self.flags=}")

                    yield from [
                        (p, {})
                        for p in cache
                        if not filename_only(os.path.basename(p)) in blacklist
                    ]
                else:
                    yield from apply(
                        self,
                        original_func,
                        source,
                        cache,
                        filter_by_cache,
                        append_cache,
                        filename,
                        **kwargs,
                    )

            else:

                if yield_cache:
                    yield from unroll_cache(filename, cache)
                if yield_apply:
                    yield from apply(
                        self,
                        original_func,
                        source,
                        cache,
                        filter_by_cache,
                        append_cache,
                        filename,
                        **kwargs,
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
            resp.text = json.dumps({"response": res, "status": resp.status})

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(
            {"response": memory_caches[(fun, req)], "status": resp.status}
        )

    return replacement_fun


class TestCache(unittest.TestCase):
    def run_cached(self, x, filename, *args, f_=None, cargs=[], ckwargs={}, **kwargs):

        if not f_:

            @configurable_cache(filename=filename, *cargs, **ckwargs)
            def f(self, values_metas, *_, **__):
                for i, m in values_metas:
                    yield i, {k: not v if k == "bool" else v for k, v in m.items()}

        else:
            f = f_

        y = list(f(None, x, *args, **kwargs))
        return x, y, f

    def check_cached(self, f, x, y, filename, *args, **kwargs):
        logging.debug(f"Content of {os.getcwd()=} \n{os.listdir(os.getcwd())}")

        if not "from_path_glob" in kwargs:
            assert os.path.exists(filename)

    def run_test_cache(
        self, gen, filename="test_cache", *args, test_delete_cache_before=True, **kwargs
    ):

        if test_delete_cache_before:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
            except IsADirectoryError:
                shutil.rmtree(filename)

        x, y, f = self.run_cached(gen, filename=filename, *args, **kwargs)
        self.check_cached(x, y, f, filename=filename, *args, **kwargs)
        print(y)
        return y

    def test_cache_glob(self):
        assert (
            len(
                self.run_test_cache(
                    None,
                    from_path_glob="*.py",
                )
            )
            > 3
        )

    def test_cache1_gen(self):
        assert len(list(self.run_test_cache(((str(i), {}) for i in range(1, 4))))) == 3

    def test_cache1_gen_multiple_times(self):
        assert len(list(self.run_test_cache(((str(i), {}) for i in range(1, 4))))) == 3
        assert len(list(self.run_test_cache(((str(i), {}) for i in range(1, 4))))) == 3
        assert len(list(self.run_test_cache(((str(i), {}) for i in range(1, 4))))) == 3

    def test_cached1_gen(self):
        assert len(list(self.run_test_cache(((str(i), {}) for i in range(1, 4))))) == 3
        assert (
            len(
                list(
                    self.run_test_cache(
                        ((str(i), {}) for i in range(4, 7)),
                        test_delete_cache_before=False,
                    )
                )
            )
            == 6
        )

    def test_cached1_gen_meta_numpy(self):
        assert (
            len(
                list(
                    self.run_test_cache(
                        ((str(i), {"np": numpy.zeros((1, 3))}) for i in range(1, 4))
                    )
                )
            )
            == 3
        )
        assert (
            len(
                list(
                    self.run_test_cache(
                        ((str(i), {}) for i in range(4, 7)),
                        test_delete_cache_before=False,
                    )
                )
            )
            == 6
        )

    def test_cached1_not_doing_again(self):
        assert (
            len(
                list(
                    self.run_test_cache(((str(i), {"bool": True}) for i in range(0, 3)))
                )
            )
            == 3
        )
        res = list(
            self.run_test_cache(
                ((str(i), {"bool": True}) for i in range(2, 4)),
                test_delete_cache_before=False,
            )
        )
        assert len(res) == 4
        assert all(
            (c == 1 for e, c in collections.Counter([int(k) for k, m in res]).items())
        )
        assert all((not r[1]["bool"] for r in res))

    def test_cache1_list(self):
        assert len(list(self.run_test_cache([("1", {}), ("2", {}), ("3", {})]))) == 3

    def test_cached1_list(self):
        assert len(list(self.run_test_cache([("1", {}), ("2", {}), ("3", {})]))) == 3
        assert (
            len(
                list(
                    self.run_test_cache(
                        [("4", {}), ("5", {}), ("6", {})],
                        test_delete_cache_before=False,
                    )
                )
            )
            == 6
        )

    def test_cache_only(self):
        assert len(list(self.run_test_cache([("1", {}), ("2", {}), ("3", {})]))) == 3
        assert (
            len(
                list(
                    self.run_test_cache(
                        [("4", {}), ("5", {}), ("6", {})],
                        test_delete_cache_before=False,
                        ckwargs={"from_cache_only": True},
                    )
                )
            )
            == 3
        )

    def test_function_only(self):
        assert len(list(self.run_test_cache([("1", {}), ("2", {}), ("3", {})]))) == 3
        assert (
            len(
                list(
                    self.run_test_cache(
                        [("4", {}), ("5", {}), ("6", {})],
                        test_delete_cache_before=False,
                        ckwargs={"from_function_only": True},
                    )
                )
            )
            == 3
        )

    def test_uncompress_decompress(self):
        decompress_pickle(compressed_pickle([1, 2, 3, 4])) == [1, 2, 3, 4]

    def test_keyword_arg(self):
        @configurable_cache(filename="t_k")
        def f(self, values_metas, depth="4"):
            for i, m in values_metas:
                yield i, {k: not v if k == "bool" else v for k, v in m.items()}

        assert (
            len(
                list(
                    self.run_test_cache(
                        [("1", {}), ("2", {}), ("3", {})], f_=f, filename="t_k"
                    )
                )
            )
            == 3
        )


if __name__ == "__main__":
    unittest.main()
