'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
from termcolor import colored as cs


class anyon_node(object):
    '''
    Anyon node object - element in the aj-tree
    id          id number (loc)

    cons        connections, in the form:
                        [node, edge]

    s           size, number of growth iterations
    g           growth state \ parity of s
    p           parity of node
    d           delay, iterations to wait
    w           waited, iterations already waited
    bucket      indicator to grow node size once per bucket
    calc_delay  list of children nodes with undefined delay
    '''

    def __init__(self, vertex):

        self.type = "A"
        self.vertex = vertex
        self.id = vertex.sID
        self.boundary = [[], []]
        self.cons = []
        self.s = 0
        self.p = 0
        self.d = 0
        self.w = 0
        self.calc_delay = []

    @property
    def g(self):
        return self.s % 2

    def __repr__(self):
        type = "s" if self.vertex.sID[0] == 0 else "p"
        return self.type + type + "{},{}".format(*self.vertex.sID[1:])

    def short_id(self):
        return self.__repr__()

    def tree_rep(self):
        color_id = cs(self.s, "red") + cs(self.p, "magenta") + \
            cs(self.d, "cyan") + cs(self.w, "green")
        return self.short_id() + color_id


class junction_node(anyon_node):
    '''
    Juntion type node
    inherit all methods from anyon_node
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "J"


class boundary_node(anyon_node):
    '''
    Boundary type node
    parity is defaulted to 1
    inherit all methods from anyon_node
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "B"
        self.p = 1


class empty_node(anyon_node):
    '''
    Empty type node
    inherit all methods from anyon_node
    dis         distance to closest node
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "E"
        self.dis = 0
