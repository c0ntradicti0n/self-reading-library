import functools
from joblib import delayed, Parallel
from layouteagle import config
from helpers.programming import exit_after
from tqdm import tqdm

def paraloop(original_fun):
    def wrapper(self, param):
        def f(arg):
            @exit_after(config.max_time_per_call)
            def ff(arg):

                return list(original_fun(self, [arg]))

            try:
                return ff(arg)

            except KeyboardInterrupt as e:
                 if config.ARGS.skip_on_timeout:
                     return [None]
                 raise e


        args = list(param)

        fut = Parallel(n_jobs=config.jobs)(delayed(f)(arg) for arg in tqdm(args))

        fut = [ff for f in fut for ff in f if ff and f]
        print(fut)
        yield from fut

    functools.update_wrapper(wrapper, original_fun)

    return wrapper
