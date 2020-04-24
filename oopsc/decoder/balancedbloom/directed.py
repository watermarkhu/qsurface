
'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

Objects and methods for the directed graph version of the Balanced Bloom algorithm

A directed graph refers to that each node in the graph has a parameters parent and children.
During a merge of two tree's, each in a child node, one tree of the two needs to be rerooted in that child node.

merge between M0 and M1:

    R0          R1
   /  \        /  \
  N0   M0 --- M1   N1

Reroot T1 in M1:

    R1          M1
   /  \  --->  /  \
  N1  M1      R1   N1

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

# TODO: Proper calculation of delay for erasures/empty nodes in the graph
'''
from termcolor import colored as cs
from ...info.decorators import debug

class anyon_node(object):
    '''
    Anyon node object - element in the aj-tree

    type        A for anyon, J for junction, B for boundary, E for empty
    vertex      the vertex/stab object this node refers to
    id          id number (loc)
    ancestor    ancestor of node in anyontree
    e           length of edge connectint to ancestor
    children    list of children nodes
    s           size, number of growth iterations
    g           growth state \ parity of s
    p           parity of node
    d           delay, iterations to wait
    w           waited, iterations already waited
    boundary    list of new boundaries to grow

    calc_delay  list of children nodes with undefined delay
    '''

    def __init__(self, vertex):

        self.type       = "A"
        self.vertex     = vertex
        self.id         = vertex.sID
        self.ancestor   = None
        self.e          = None
        self.children   = []
        self.s          = 0
        self.p          = 0
        self.d          = 0
        self.w          = 0
        self.boundary   = [[], []]
        self.calc_delay = []

        '''
        unionfind_evengrow_plugin
        Needed to grow node in size once per round for plugin version
        '''
        self.bucket = None

    @property
    def g(self):
        return self.s % 2

    def __repr__(self):
        children_id_list = [child.id for child in self.children]

        if self.ancestor:
            return self.type + "{}^{}_{}".format(self.id, self.ancestor.id, children_id_list)
        else:
            return self.type + "{}_{}".format(self.id, children_id_list)

    def short_id(self):
        type = "s" if self.id[0] == 0 else "p"
        return self.type + type + "{},{}".format(self.id[1], self.id[2])

    def tree_rep(self):
        color_id = cs(self.s, "red") + cs(self.p, "magenta") + cs(self.d, "cyan") + cs(self.w, "green") + cs(self.e, "yellow")
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

    @debug.counter(name="mac")
    def make_ancestor_child(self, node, ac_level=False):
        '''
        Recursive function to reroot an tree in a certain node
        '''
        if node is not None:
            self.make_ancestor_child(node.ancestor)
            ancestor = node.ancestor

            if ancestor is not None:
                ancestor.children.remove(node)
                ancestor.ancestor = node
                ancestor.e = node.e
                node.children.append(ancestor)

            if ac_level:
                node.ancestor = None
                node.e = None


    def comp_tree_p_of_node(self, node):
        '''
        Recursive function to find the parity of a node and its children
        '''
        parity = sum([1 - self.comp_tree_p_of_node(child) for child in node.children]) % 2

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
    def comp_tree_d_of_node(self, node, cluster):
        '''
        Recursive function to find the delay of a node and its children
        '''
        node.calc_delay = []
        node.w = 0

        if node.ancestor is None:
            for child in node.children:
                self.comp_tree_d_of_node(child, cluster)
        else:
            ancestor = node.ancestor
            size_diff = (node.s + node.g)//2 - (ancestor.s + node.g)//2 + node.e*(-1)**(node.p + 1)
            support_fix = (node.g + ancestor.g)%2
            node.d = ancestor.d + int(2*self.fbloom*size_diff) - support_fix
            # node.d = ancestor.d + (node.s//2 - ancestor.s//2 + node.e*(-1)**(node.p + 1))

            if node.d < cluster.mindl:                  # store cluster minimum delay
                cluster.mindl = node.d
            for child in node.children:
                self.comp_tree_d_of_node(child, cluster)


    def connect_nodes(self, ancestor, child, edge):
        '''
        Connects two nodes by setting the parent child relationchip between the two
        '''
        child.ancestor = ancestor
        ancestor.children.append(child)
        child.e = edge


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
        if (even_after_union and ac_cluster.parity > pa_cluster.parity) or pa_cluster.parity % 2 == 0:
            root_node, an_node, ch_node = ac_cluster.root_node, ac_node, pa_node
        else:
            root_node, an_node, ch_node = pa_cluster.root_node, pa_node, ac_node

        self.make_ancestor_child(ch_node, True)

        if ac_node.g == 0 and pa_node.s > 1:                             # Connect via new juntion-node
            pa_vertex.node = junction_node(pa_vertex)
            self.connect_nodes(an_node, pa_vertex.node, an_node.s // 2)
            self.connect_nodes(pa_vertex.node, ch_node, ch_node.s // 2)
            calc_delay_node = None if even_after_union else pa_vertex.node
        else:                                                               # Connect directly
            self.connect_nodes(an_node, ch_node, (ac_node.s + pa_node.s) // 2)
            calc_delay_node = None if even_after_union else ch_node

        root_node.calc_delay.append(calc_delay_node)        # store generator of undefined delay

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
