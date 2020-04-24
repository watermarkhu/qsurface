'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

Objects and methods for the directed graph version of the Balanced Bloom algorithm

A undirected graph refers to that each node in the graph has a paramter cons (connections) refereing to the edges and nodes connected to this node.
During a merge of two tree's, these connections needs simply to be added in each of the nodes.

merge between M0 and M1:

    R0          R1
   /  \        /  \
  N0   M0 --- M1   N1

Connections before:

R0: [N0, M0],  N0: [R0],  M0: [R0]
R1: [N1, M1],  N1: [R1],  M1: [R1]

Tree after merge:

    R0
   /  \
  N0   M0
        \
         M1
          \
           R1
            \
             N1

Connection after:

R0: [N0, M0],  N0: [R0],  M0: [R0, M1]
R1: [N1, M1],  N1: [R1],  M1: [R1, M0]


# TODO: Proper calculation of delay for erasures/empty nodes in the graph
'''

from termcolor import colored as cs
from ...info.decorators import debug


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

        self.type       = "A"
        self.vertex     = vertex
        self.id         = vertex.sID
        self.boundary   = [[], []]
        self.cons       = []
        self.s          = 0
        self.p          = 0
        self.d          = 0
        self.w          = 0
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
        color_id = cs(self.s, "red") + cs(self.p, "magenta") + cs(self.d, "cyan") + cs(self.w, "green")
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


class nodeset(object):

    @debug.init_counters_bb()
    def __init__(self, fbloom=.5):
        self.fbloom = fbloom

    def anyon_node(self, vertex):
        return anyon_node(vertex)

    def boundary_node(self, vertex):
        return boundary_node(vertex)


    def comp_tree_p_of_node(self, node, ancestor=None):
        '''
        Recursive function to find the parity of a node and its children
        '''
        parity = sum([1 - self.comp_tree_p_of_node(con[0], node) for con in node.cons if con[0] is not ancestor]) % 2

        if type(node) == anyon_node:
            node.p = parity
            return node.p

        elif type(node) == junction_node:
            node.p = 1 - parity
            return node.p

        else:
            node.p = 1
            return node.p


    @debug.counter(name="ctd")
    def comp_tree_d_of_node(self, cluster, node, an_con=None):
        '''
        Recursive function to find the delay of a node and its children
        '''
        node.calc_delay = []
        node.w = 0

        if an_con is None:
            for con in node.cons:
                self.comp_tree_d_of_node(cluster, con[0], [node, con[1]])
        else:
            ancestor, edge = an_con
            size_diff = (node.s + node.g)//2 - (ancestor.s + node.g)//2 + edge*(-1)**(node.p + 1)
            support_fix = (node.g + ancestor.g)%2
            node.d = ancestor.d + int(2*self.fbloom*size_diff) - support_fix
            # node.d = ancestor.d + (node.s//2 - ancestor.s//2 + edge*(-1)**(node.p + 1))

            if node.d < cluster.mindl:                  # store cluster minimum delay
                cluster.mindl = node.d

            for con in node.cons:
                if con[0] is not ancestor:
                    self.comp_tree_d_of_node(cluster, con[0], [node, con[1]])


    def connect_nodes(self, nodeA, nodeB, edge):
        '''
        Connects two nodes by saving each other in the cons variable
        '''
        nodeA.cons.append([nodeB, edge])
        nodeB.cons.append([nodeA, edge])


    def joint(self, ac_vertex, pa_vertex, ac_cluster, pa_cluster):
        '''
        Union of two anyontrees.
        ac_vertex   merging vertex of base cluster
        pa_vertex   merging vertex of grow cluster
        '''
        ac_node, pa_node = ac_vertex.node, pa_vertex.node
        even_after_union = True if ac_cluster.parity % 2 == pa_cluster.parity % 2 else False
        '''
        ac_node     root of active vertex
        pa_node     root of passive vertex
        an_node     ancestor node during union
        ch_node     child node during union

        even_after_union:       if cluster is even after union, union of trees is done by weighted union
                                else, union is done by always appending even tree to odd tree,
                                delay calculation is needed from the child node (of union duo) and descendents
        '''
        if not even_after_union and pa_cluster.parity % 2 == 0:
            root_node, an_node, ch_node = ac_cluster.root_node, ac_node, pa_node
        else:
            root_node, an_node, ch_node = pa_cluster.root_node, pa_node, ac_node

        calc_delay_node = None if even_after_union else ch_node

        if ac_node.g == 0 and pa_node.s > 1:                             # Connect via new juntion-node
            pa_vertex.node = junction_node(pa_vertex)
            an_edge = an_node.s // 2
            self.connect_nodes(pa_vertex.node, an_node, an_edge)
            self.connect_nodes(pa_vertex.node, ch_node, ch_node.s // 2)
            calc_delay_node = None if even_after_union else [pa_vertex.node, an_edge, an_node]
        else:                                                               # Connect directly
            an_edge = (an_node.s + ch_node.s) // 2
            self.connect_nodes(an_node, ch_node, an_edge)
            calc_delay_node = None if even_after_union else [ch_node, an_edge, an_node]

        root_node.calc_delay.append(calc_delay_node)                        # store generator of undefined delay

        return root_node


    def new_empty(self, ac_vertex, pa_vertex, cluster):
        '''
        New empty node that is the result of error errors.
        Distance is calculated from this node to the closest non-empty node
        '''
        pa_vertex.node = empty_node(pa_vertex)
        ac_node, pa_node = ac_vertex.node, pa_vertex.node

        if ac_node.type == "E":
            self.connect_nodes(ac_node, pa_node, 1)
            pa_node.dis = ac_node.dis + 1
        else:
            self.connect_nodes(ac_node, pa_node, ac_node.s // 2)
            # cluster.root_node.calc_delay.append(pa_vertex.node)
