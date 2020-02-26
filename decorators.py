'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

Contains decorator classes and method for:
* de cluttering the main methods from plotting and printing functions
* debugging and counters for method calls

'''

import functools
import time
import printing as pr


class plot(object):
    '''
    This class only contains decorators that are used to warp functions in the unionfind decoder. The wrappers add plotting and printing functionality. This has the goal of keeping the code of the decoder easy to read.
    '''

    def iter(name, cname, dname=None, flip=True):
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


    def iter_grow_bucket():
        def decorator_repeat(func):
            @functools.wraps(func)
            def wrapper_repeat(self, bucket, bucket_i, *args, **kwargs):
                if self.print_steps:
                    self.mstr = {}
                    pr.printlog(
                    "\n############################ GROW ############################" + f"\nGrowing bucket {bucket_i} of {self.maxbucket}: {bucket}" + f"\nRemaining buckets: {self.buckets[bucket_i + 1 : self.maxbucket + 1]}, {self.wastebucket}\n"
                    )
                elif self.plot:
                    print(f"Growing bucket #{bucket_i}/{self.maxbucket}")
                if self.plot and self.plot_bucket:
                    self.plot.new_iter(f"Bucket {bucket_i} grown")
                value = func(self, bucket, bucket_i, *args, **kwargs)
                if self.plot and self.plot_bucket:
                    self.plot.draw_plot()
                return value
            return wrapper_repeat
        return decorator_repeat


    def iter_fuse_bucket():
        def decorator_repeat(func):
            @functools.wraps(func)
            def wrapper_repeat(self, bucket_i, *args, **kwargs):
                if self.plot and self.plot_bucket:
                    self.plot.new_iter(f"Bucket {bucket_i} fused")
                value = func(self, bucket_i *args, **kwargs)
                if self.print_steps:
                    pr.printlog("")
                    for cID, string in self.mstr.items():
                        pr.printlog(f"B:\n{string}\nA:\n{pr.print_graph(self.graph, [self.graph.C[cID]], include_even=1, return_string=True)}\n")
                if self.plot and self.plot_bucket:
                    self.plot.draw_plot()
                return value
            return wrapper_repeat
        return decorator_repeat


    def iter_grow_boundary():
        def decorator_repeat(func):
            @functools.wraps(func)
            def wrapper_repeat(self, cluster, *args, **kwargs):
                if self.plot and self.plot_cluster:
                    self.plot.new_iter("bucket {}: {} grown".format(cluster.bucket, cluster))
                value = func(self, cluster, *args, **kwargs)
                if self.plot and self.plot_cluster:
                    self.plot.draw_plot()
                return value
            return wrapper_repeat
        return decorator_repeat

    def iter_grow_cluster():
        def decorator_repeat(func):
            @functools.wraps(func)
            def wrapper_repeat(self, cluster, *args, **kwargs):
                if self.plot and self.plot_cluster: self.plot.new_iter("bucket {}: {} grown".format(cluster.bucket, cluster))

                value = func(self, cluster, *args, **kwargs)

                if self.plot and self.plot_cluster:
                    self.plot.draw_plot()
                return value
            return wrapper_repeat
        return decorator_repeat


    def iter_grow_boundary_node():
        def decorator_repeat(func):
            @functools.wraps(func)
            def wrapper_repeat(self, cluster, node, *args, **kwargs):
                if cluster.root_node.calc_delay and self.print_steps:
                    if type(cluster.root_node.calc_delay) == list:
                        calc_nodes = [node.short_id() for node, edge, ancestor in cluster.root_node.calc_delay]
                        print_tree = False
                    else:
                        calc_nodes = [node.short_id() for node in cluster.root_node.calc_delay]
                        print_tree = True
                    print("Computing delay root {} at nodes {} and children".format(cluster.root_node.short_id(), calc_nodes))
                else:
                    print_tree = False

                value = func(self, cluster, node, print_tree=print_tree, *args, **kwargs)

                return value
            return wrapper_repeat
        return decorator_repeat


    def iter_grow_node():
        def decorator_repeat(func):
            @functools.wraps(func)
            def wrapper_repeat(self, cluster, node, *args, **kwargs):
                if self.plot and self.plot_node: self.plot.new_iter("bucket {}: {}-{} grown".format(cluster.bucket, node, cluster))

                value = func(self, cluster, node,  *args, **kwargs)

                if self.plot and self.plot_node: self.plot.draw_plot()
                return value
            return wrapper_repeat
        return decorator_repeat


class debug(object):
    '''
    Decorator class for counting the uses of class methods
    '''
    def init_counters_uf():
        '''
        Initializes couters for unionfind classes
        '''
        def decorator_repeat(func):
            @functools.wraps(func)
            def wrapper_repeat(self, *args, **kwargs):
                value = func(self, *args, **kwargs)
                self.c_gbu, self.c_gbo, self.c_ufu, self.c_uff = 0, 0, 0, 0
                self.gbu ,self.gbo, self.ufu, self.uff, self.time = [], [], [], [], []
                self.mac, self.ctd = [], []
                return value
            return wrapper_repeat
        return decorator_repeat

    def init_counters_eg():
        '''
        Initializes counters for evengrow classes
        '''
        def decorator_repeat(func):
            @functools.wraps(func)
            def wrapper_repeat(self, *args, **kwargs):
                value = func(self, *args, **kwargs)
                self.c_mac, self.c_ctd = 0, 0
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
                counter = getattr(self, name)
                setattr(self, name, counter + 1)
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
                self.t0 = time.time()

                value = func(self, *args, **kwargs)

                self.time.append(time.time() - self.t0)
                self.gbu.append(self.c_gbu)
                self.gbo.append(self.c_gbo)
                self.ufu.append(self.c_ufu)
                self.uff.append(self.c_uff)
                self.c_gbu, self.c_gbo, self.c_ufu, self.c_uff = 0, 0, 0, 0

                if hasattr(self, "eg"):
                    self.mac.append(self.eg.c_mac)
                    self.ctd.append(self.eg.c_ctd)
                    self.eg.c_mac, self.eg.c_ctd = 0, 0

                return value
            return wrapper_repeat
        return decorator_repeat
