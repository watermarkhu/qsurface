'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

Contains decorator classes and method for:
* de cluttering the main methods from plotting and printing functions

'''

import functools

def plot_grow_node():
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, cluster, node, *args, **kwargs):
            if self.plot and self.step_node:
                self.plot.new_iter(
                    "bucket {}: {}-{} grown".format(cluster.bucket, node, cluster))

            value = func(self, cluster, node,  *args, **kwargs)

            if self.plot and self.step_node:
                self.plot.draw_plot()
            return value
        return wrapper_repeat
    return decorator_repeat


def plot_grow_boundary_node():
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, cluster, node, *args, **kwargs):
            if cluster.root_node.calc_delay and self.print_steps:
                if type(cluster.root_node.calc_delay[0]) == list:
                    calc_nodes = [node.short_id() for node, edge,
                                  ancestor in cluster.root_node.calc_delay]
                    print_tree = False
                else:
                    calc_nodes = [node.short_id()
                                  for node in cluster.root_node.calc_delay]
                    print_tree = True
                print("Computing delay root {} at nodes {} and children".format(
                    cluster.root_node.short_id(), calc_nodes))
            else:
                print_tree = False

            value = func(self, cluster, node,
                         print_tree=print_tree, *args, **kwargs)

            return value
        return wrapper_repeat
    return decorator_repeat


def init_counters_bb():
    '''
    Initializes counters for evengrow classes
    '''
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            value = func(self, *args, **kwargs)
            self.counters = dict(
                mac=0,
                ctd=0
            )
            self.c_mac, self.c_ctd = 0, 0
            return value
        return wrapper_repeat
    return decorator_repeat
