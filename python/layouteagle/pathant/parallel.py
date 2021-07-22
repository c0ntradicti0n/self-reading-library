import functools
from joblib import delayed, Parallel
from layouteagle import config


def paraloop(original_fun):
    def wrapper(self, param):
        def f(arg):
            return list(original_fun(self, [arg]))

        args = list(param)

        fut = Parallel(n_jobs=config.jobs)(delayed(f)(arg) for arg in args)
        fut = [ff for f in fut for ff in f if f]
        print(fut)
        yield from fut

    functools.update_wrapper(wrapper, original_fun)

    return wrapper
