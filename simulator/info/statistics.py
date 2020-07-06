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


class stat_counter(object):

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
            if hasattr(self, 'stat_counter'):
                if name is not None:
                    key = name
                else:
                    try:
                        key = func.__name__
                    except:
                        raise TypeError("Must decorate a method")
                self.stat_counter.add_count(key)
            value = func(self, *args, **kwargs)
            return value
        return wrapper_repeat
    return decorator_repeat


def get_count_via_func(name, func_name):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            if hasattr(self, 'stat_counter'):
                count_func = getattr(self, func_name)
                count = count_func()
                self.stat_counter.set_count(name, count)
            value = func(self, *args, **kwargs)
            return value
        return wrapper_repeat
    return decorator_repeat


def timeit(name="time"):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            if hasattr(self, 'stat_counter'):
                t0 = time.process_time()
                value = func(self, *args, **kwargs)
                self.stat_counter.set_count(name, time.process_time() - t0)
            else:
                value = func(self, *args, **kwargs)
            return value
        return wrapper_repeat
    return decorator_repeat

