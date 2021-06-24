import functools
import time

import ray
from joblib import delayed, Parallel




def paraloop(original_fun):

    def wrapper(self, param):

        def f(arg):
            return list(original_fun(self, [arg]))

        args = list(param)

        fut = Parallel(n_jobs=16)(delayed(f)(arg) for arg in args)
        fut = [ ff  for f in fut for ff in f if f ]
        print (fut)
        yield from fut

    functools.update_wrapper(wrapper, original_fun)

    return wrapper

