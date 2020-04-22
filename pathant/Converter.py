import functools

from pathant.converters import converters


class converter(object):
    def __init__(self,  _from, _to, *args, **kwargs):
        self._from = _from
        self._to = _to
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        self.func = func(*self.args, **self.kwargs, path_spec=self)
        functools.update_wrapper(self, self.func)
        converters.append((self._from, self._to, self.func))


        return self.func
