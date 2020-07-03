'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

Contains decorator classes and method for:
* de cluttering the main methods from plotting and printing functions

'''

import functools
import time
from simulator.info import printing as pr


def plot_iter(name, cname, dname=None, flip=True):
    '''
    General type plot iter decorator
    '''
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            attr = getattr(self, cname)
            criteria = not attr if flip else attr
            if self.plot and criteria:
                self.plot.new_iter(name)
            value = func(self, *args, **kwargs)
            if self.plot and criteria:
                if dname:
                    getattr(self.plot, dname)()
                self.plot.draw_plot()
            return value
        return wrapper_repeat
    return decorator_repeat


def plot_grow_bucket():
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, bucket, bucket_i, *args, **kwargs):
            if self.print_steps:
                self.mstr = {}
                pr.printlog(
                    "\n############################ GROW ############################" + 
                    f"\nGrowing bucket {bucket_i} of {self.maxbucket}: {bucket}" + 
                    f"\nRemaining buckets: {self.buckets[bucket_i + 1 : self.maxbucket + 1]}, {self.wastebucket}\n"
                )
            elif self.plot:
                print(f"Growing bucket #{bucket_i}/{self.maxbucket}")
            if self.plot and self.step_bucket:
                self.plot.new_iter(f"Bucket {bucket_i} grown")
            value = func(self, bucket, bucket_i, *args, **kwargs)
            if self.plot and self.step_bucket:
                self.plot.draw_plot()
            return value
        return wrapper_repeat
    return decorator_repeat


def plot_fuse_bucket():
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, bucket_i, *args, **kwargs):
            if self.plot and self.step_bucket:
                self.plot.new_iter(f"Bucket {bucket_i} fused")
            value = func(self, bucket_i *args, **kwargs)
            if self.print_steps:
                pr.printlog("")
                for cID, string in self.mstr.items():
                    pr.printlog(f"B:\n{string}\nA:\n{pr.print_graph(self.graph, [self.graph.C[cID]], include_even=1, return_string=True)}\n")
            if self.plot and self.step_bucket:
                self.plot.draw_plot()
            return value
        return wrapper_repeat
    return decorator_repeat


def plot_grow_boundary():
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, cluster, *args, **kwargs):
            if self.plot and self.step_cluster:
                self.plot.new_iter("bucket {}: {} grown".format(cluster.bucket, cluster))
            value = func(self, cluster, *args, **kwargs)
            if self.plot and self.step_cluster:
                self.plot.draw_plot()
            return value
        return wrapper_repeat
    return decorator_repeat


def plot_grow_cluster():
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, cluster, *args, **kwargs):
            if self.plot and self.step_cluster: self.plot.new_iter("bucket {}: {} grown".format(cluster.bucket, cluster))

            value = func(self, cluster, *args, **kwargs)

            if self.plot and self.step_cluster:
                self.plot.draw_plot()
            return value
        return wrapper_repeat
    return decorator_repeat


def plot_peel_clusters():
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            if self.plot:
                self.plot.new_iter("Clusters peeled")
            value = func(self, *args, **kwargs)
            if self.plot:
                if not self.step_peel:
                    self.plot.plot_removed()
                self.plot.draw_plot()
            return value
        return wrapper_repeat
    return decorator_repeat


def init_counters_uf():
    '''
    Initializes couters for unionfind classes
    '''
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            value = func(self, *args, **kwargs)

            self.counters = dict(
                gbu=0,
                gbo=0,
                ufu=0,
                uff=0,
            )
            self.c_gbu, self.c_gbo, self.c_ufu, self.c_uff = 0, 0, 0, 0

            self.clist = dict(
                time=[],
                gbu=[],
                gbo=[],
                ufu=[],
                uff=[],
                mac=[],
                ctd=[],
            )
            return value
        return wrapper_repeat
    return decorator_repeat
