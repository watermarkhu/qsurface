'''
Decorator classes and metaclasses that are used to keep track certain paraters of the methods and classes used. 
'''


import functools
import time

'''
From: https://realpython.com/primer-on-python-decorators/
https://stackoverflow.com/questions/2365701/decorating-python-class-methods-how-do-i-pass-the-instance-to-the-decorator
'''

def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        # print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        if value is None:
            return run_time
        else:
            return value, run_time
    return wrapper_timer


def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug


class countcalls:
    """Count the number of calls made to the decorated function"""

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        # print(f"Call {self.calls} of {self.func.__name__!r}")
        return self.func(*args, **kwargs)


'''
https://www.python-course.eu/python3_count_function_calls.php
'''

class FuncCallCounter(type):
    """ A Metaclass which decorates all the methods of the
        subclass using call_counter as the decorator
    """

    @staticmethod
    def call_counter(func):
        """ Decorator for counting the number of function
            or method calls to the function or method func
        """
        def helper(*args, **kwargs):
            helper.calls += 1
            return func(*args, **kwargs)
        helper.calls = 0
        helper.__name__= func.__name__

        return helper

    def __new__(cls, clsname, superclasses, attributedict):
        """ Every method gets decorated with the decorator call_counter,
            which will do the actual call counting
        """
        for attr in attributedict:
            if callable(attributedict[attr]) and not attr.startswith("__"):
                attributedict[attr] = cls.call_counter(attributedict[attr])

        return type.__new__(cls, clsname, superclasses, attributedict)
