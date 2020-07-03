'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

Contains decorator classes and method for:
* debugging and counters for method calls

'''
import functools
import time


def init_counters():
    '''
    Initializes couters for unionfind classes
    '''
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            value = func(self, *args, **kwargs)
            self.counters = {}
            self.clist = dict(time=[])
            return value
        return wrapper_repeat
    return decorator_repeat


def counter(name):
    '''
    Add a count to the specified counter
    '''
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            self.counters[name] += 1
            value = func(self, *args, **kwargs)
            return value
        return wrapper_repeat
    return decorator_repeat


def get_counters():
    '''
    decorates decoder.decode()
    Stores iterative counters to a list and resets the counters
    '''
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):

            t0 = time.process_time()

            value = func(self, *args, **kwargs)

            self.clist["time"].append(time.process_time() - t0)

            for key, value in self.counters.items():
                self.clist[key].append(value)
                self.counters[key] = 0

            if hasattr(self, "eg"):
                for key, value in self.eg.counters.items():
                    self.clist[key].append(value)
                    self.eg.counters[key] = 0

            return value
        return wrapper_repeat
    return decorator_repeat


def reset_counters(graph):
    '''
    Reset counter list of a graph
    '''
    graph.matching_weight = []
    for key in graph.decoder.clist:
        graph.decoder.clist[key] = []




