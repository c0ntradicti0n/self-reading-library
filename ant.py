import json
import logging
import os

from layouteagle import config
from layouteagle.helpers.nested_dict_tools import type_spec
from layouteagle.pathant.PathSpec import PathSpec, cache_flow


class Ant(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.cached:
            raise Exception(f"You may say to cache or not for inheriting class '{type(self).__name__ }'"
                            f"\n by adding kwarg 'cached: [cache_flow] = ...' ")

    def __call__(self, args):
        #print ("Input was: ", type_spec(args), args)
        print (self.cached)

        if self.cached == cache_flow.iterate:

            for arg in args:

                if type(arg) == tuple:
                    dingsbums, meta = arg
                else:
                    dingsbums = arg
                    meta = {}

                result = self.call(dingsbums, meta=meta)
                if not result:
                    logging.error(f"result of '{type(self).__name__ }' was None or nothing")
                self.cache_write(result, meta)
                yield result, meta

    def call(arg, **kwars):
        raise Exception("You must implement the 'call' method!")

    def cache_write(self, result, meta):
        try:
            filename = config.cache + type(self).__name__  + '.json'

            if os.path.exists(filename):
                append_write = 'a'  # append if already exists
            else:
                append_write = 'w'  # make a new file if not

            with open(filename, append_write) as f:
                result_string = json.dumps([result, meta])
                f.write(result_string)
        except TypeError as e:
            logging.error(f"could not write cache because of: {e}")



if __name__=="__main__":
    class test(Ant):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, cached = cache_flow.iterate, **kwargs)
        def call(self, arg, meta=None):
            print("Input was: ", type_spec(arg), arg)

            return arg + 1

    t1, t2, t3 = test(), test(), test()
    print ("path: ", list(t1(t2(t3([1])))))
    print ("list: ", list( t1([1,2,3])))




