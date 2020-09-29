'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

Contains decorator classes and method for:
* debugging and counters for method calls

'''

import functools
import time
from collections import defaultdict as dd


class BenchMarker(object):

    def __init__(self):
        self.counters = dd(int)
        self.clist = dd(list)

    def add_count(self, key):
        self.counters[key] += 1 
    
    def set_count(self, key, value):
        self.counters[key] = value

    def get_counters(self):
        for key, value in self.counters.items():
            self.clist[key].append(value)
            self.counters[key] = 0
    
    def reset_clist(self):
        '''
        Reset counter list of a graph
        '''
        for key in self.clist:
            self.clist[key] = []


def add_count(name=None):
    '''
    Add a count to the specified counter
    '''
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            if self.benchmarker is not None:
                if name is not None:
                    key = name
                else:
                    try:
                        key = func.__name__
                    except:
                        raise TypeError("Must decorate a method")
                self.benchmarker.add_count(key)
            value = func(self, *args, **kwargs)
            return value
        return wrapper_repeat
    return decorator_repeat


def save_count_via_func(name, classmethod):
    '''
    Save a count via a supplied classmethod 
    '''
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            if self.benchmarker is not None:
                count_func = getattr(self, classmethod)
                count = count_func()
                self.benchmarker.set_count(name, count)
            value = func(self, *args, **kwargs)
            return value
        return wrapper_repeat
    return decorator_repeat


def timeit(name="time"):
    '''
    Find the process time the decorated method
    '''
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            if self.benchmarker is not None:
                t0 = time.process_time()
                value = func(self, *args, **kwargs)
                self.benchmarker.set_count(name, time.process_time() - t0)
            else:
                value = func(self, *args, **kwargs)
            return value
        return wrapper_repeat
    return decorator_repeat

