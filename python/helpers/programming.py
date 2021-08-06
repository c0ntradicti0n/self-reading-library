import threading
from _thread import *
import sys
import logging

def quit_function(fn_name):
    # print to stderr, unbuffered in Python 2.
    logging.error(f'Time scoped function {fn_name} took too long')
    sys.stderr.flush() # Python 3 stderr is likely buffered.
    interrupt_main() # raises KeyboardInterrupt

def exit_after(s):
    '''
    use as decorator to exit process if
    function takes longer than s seconds
    '''
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, quit_function, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                timer.cancel()
            return result
        return inner
    return outer


def hygienic(decorator):
    def new_decorator(original):
        wrapped = decorator(original)
        wrapped.__name__ = original.__name__
        wrapped.__doc__ = original.__doc__
        wrapped.__module__ = original.__module__
        return wrapped
    return new_decorator

def overrides(interface_class):
    """
    Function override annotation.
    Corollary to @abc.abstractmethod where the override is not of an
    abstractmethod.
    Modified from answer https://stackoverflow.com/a/8313042/471376
    """
    def confirm_override(method):
        if method.__name__ not in dir(interface_class):
            raise NotImplementedError('function "%s" is an @override but that'
                                      ' function is not implemented in base'
                                      ' class %s'
                                      % (method.__name__,
                                         interface_class)
                                      )

        def func():
            pass

        attr = getattr(interface_class, method.__name__)
        if type(attr) is not type(func):
            raise NotImplementedError('function "%s" is an @override'
                                      ' but that is implemented as type %s'
                                      ' in base class %s, expected implemented'
                                      ' type %s'
                                      % (method.__name__,
                                         type(attr),
                                         interface_class,
                                         type(func))
                                      )
        return method
    return confirm_override


import warnings
import functools

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func