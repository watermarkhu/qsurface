from termcolor import colored as cs

class anyon_node(object):
    '''
    Anyon node object - element in the aj-tree
    var id          id number (loc)
    var ancestor    ancestor of node in anyontree
    var e           length of edge connectint to ancestor
    var children    list of children nodes
    var s           size, number of growth iterations
    var g           growth state \ parity of s
    var p           parity of node
    var d           delay, iterations to wait
    var w           waited, iterations already waited
    var calc_delay  list of children nodes with undefined delay
    '''

    def __init__(self, vertex):

        self.type = "A"
        self.vertex = vertex
        self.id = vertex.sID

        self.ancestor = None
        self.e = None
        self.children = []
        self.s = 0
        self.p = 0
        self.d = 0
        self.w = 0
        self.boundary = [[], []]
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
    inherit all methods from anyon_node
    add list of anyon-nodes
    '''
    def __init__(self, id):
        super().__init__(id)
        self.type = "J"


class boundary_node(anyon_node):
    '''
    inherit all methods from anyon_node
    add list of anyon-nodes
    '''
    def __init__(self, id):
        super().__init__(id)
        self.type = "B"
        self.p = 1


class empty_node(anyon_node):
    '''
    inherit all methods from anyon_node
    add list of anyon-nodes
    '''
    def __init__(self, id):
        super().__init__(id)
        self.type = "E"
        self.dis = 0


def make_ancestor_child(node, ac_level=False):
    '''
    Recursive function to reroot an tree in a certain node
    '''
    if node is not None:
        make_ancestor_child(node.ancestor)
        ancestor = node.ancestor

        if ancestor is not None:
            ancestor.children.remove(node)
            ancestor.ancestor = node
            ancestor.e = node.e
            node.children.append(ancestor)

        if ac_level:
            node.ancestor = None
            node.e = None


def comp_tree_p_of_node(node):
    '''
    Recursive function to find the parity of a node and its children
    '''

    parity = sum([1 - comp_tree_p_of_node(child) for child in node.children]) % 2

    if type(node) == anyon_node:
        node.p = parity
        return node.p

    elif type(node) == junction_node:
        node.p = 1 - parity
        return node.p

    else:
        node.p = 1
        return node.p


def comp_tree_d_of_node(node, cluster):
    '''
    Recursive function to find the delay of a node and its children
    '''
    node.calc_delay = []
    node.w = 0

    if node.ancestor is None:
        for child in node.children:
            comp_tree_d_of_node(child, cluster)
    else:
        ancestor = node.ancestor
        # size_diff = (node.s + node.g)//2 - (ancestor.s + node.g)//2 + node.e*(-1)**(node.p + 1)
        # support_fix = (node.g + ancestor.g)%2
        # node.d = ancestor.d + 2 * size_diff - support_fix - 1
        node.d = ancestor.d + (node.s//2 - ancestor.s//2 + node.e*(-1)**(node.p + 1))

        if node.d < cluster.mindl:                  # store cluster minimum delay
            cluster.mindl = node.d
        for child in node.children:
            comp_tree_d_of_node(child, cluster)


def connect_nodes(ancestor, child, edge):
    child.ancestor = ancestor
    ancestor.children.append(child)
    child.e = edge


def adoption(ac_vertex, pa_vertex, ac_cluster, pa_cluster):
    '''
    var ac_vertex   merging vertex of base cluster
    var pa_vertex   merging vertex of grow cluster
    '''
    ac_node, pa_node = ac_vertex.node, pa_vertex.node
    even_after_union = True if ac_cluster.parity % 2 == pa_cluster.parity % 2 else False

    '''
    ac_node:    root of active vertex
    pa_node:    root of passive vertex
    an_node:    ancestor node during union
    ch_node:    child node during union

    even_after_union:       if cluster is even after union, union of trees is done by weighted union
                            else, union is done by always appending even tree to odd tree,
                            delay calculation is needed from the child node (of union duo) and descendents
    '''
    if (even_after_union and ac_cluster.parity > pa_cluster.parity) or pa_cluster.parity % 2 == 0:
        root_node, an_node, ch_node = ac_cluster.root_node, ac_node, pa_node
    else:
        root_node, an_node, ch_node = pa_cluster.root_node, pa_node, ac_node

    make_ancestor_child(ch_node, True)

    if ac_node.g == 0 and pa_node.s > 1:                             # Connect via new juntion-node
        pa_vertex.node = junction_node(pa_vertex)
        connect_nodes(an_node, pa_vertex.node, an_node.s // 2)
        connect_nodes(pa_vertex.node, ch_node, ch_node.s // 2)
        calc_delay_node = None if even_after_union else pa_vertex.node
    else:                                                               # Connect directly
        connect_nodes(an_node, ch_node, (ac_node.s + pa_node.s) // 2)
        calc_delay_node = None if even_after_union else ch_node

    root_node.calc_delay.append(calc_delay_node)        # store generator of undefined delay

    return root_node


def new_empty(ac_vertex, pa_vertex, cluster):

    pa_vertex.node = empty_node(pa_vertex)
    ac_node, pa_node = ac_vertex.node, pa_vertex.node

    if ac_node.type == "E":
        connect_nodes(ac_node, pa_node, 1)
        pa_node.dis = ac_node.dis + 1
    else:
        connect_nodes(ac_node, pa_node, ac_node.s // 2)
        # cluster.root_node.calc_delay.append(pa_vertex.node)
