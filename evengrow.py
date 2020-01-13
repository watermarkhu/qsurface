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
    var bucket      indicator to grow node size once per bucket
    var calc_delay  list of children nodes with undefined delay
    '''

    def __init__(self, id):

        self.type = "A"
        self.id = id

        self.ancestor = None
        self.e = None
        self.children = []
        self.s = 0
        self.p = 0
        self.d = 0
        self.w = 0
        self.bucket = None
        self.calc_delay = []

    @property
    def g(self):
        return self.s % 2

    @property
    def short_id(self):
        type = "s" if self.id[0] == 0 else "p"
        return self.type + type + "{},{}".format(self.id[1], self.id[2])

    @property
    def tree_rep(self):
        return self.short_id + cs(self.s, "red") + cs(self.p, "magenta") + cs(self.d, "cyan") + cs(self.w, "green") + cs(self.e, "yellow")

    def __repr__(self):
        children_id_list = [child.id for child in self.children]

        if self.ancestor:
            return self.type + "{}^{}_{}".format(self.id, self.ancestor.id, children_id_list)
        else:
            return self.type + "{}_{}".format(self.id, children_id_list)


class junction_node(anyon_node):
    '''
    inherit all methods from anyon_node
    add list of anyon-nodes
    '''
    def __init__(self, id):
        super().__init__(id)
        self.type = "J"


def adoption(ac_vertex, pa_vertex, ac_cluster, pa_cluster):
    '''
    var ac_vertex   merging vertex of base cluster
    var pa_vertex   merging vertex of grow cluster
    '''
    ac_node, pa_node = ac_vertex.node, pa_vertex.node
    even_after_union = True if ac_cluster.parity % 2 == pa_cluster.parity % 2 else False
    create_junction = True if ac_node.g == 0 and pa_node.s > 1 else False

    '''
    ac_node:    root of active vertex
    pa_node:    root of passive vertex
    an_node:    ancestor node during union
    ch_node:    child node during union

    even_after_union:       if cluster is even after union, union of trees is done by weighted union
                            else, union is done by always appending even tree to odd tree,
                            delay calculation is needed from the child node (of union duo) and descendents
    create_junstion:        if conditions are met, a junction-node is created on the passive vertex.
                            this junction node is made a child of the ancestor node (of union duo)
                            child node edge is affected
    '''
    if (even_after_union and ac_cluster.parity > pa_cluster.parity) or pa_cluster.parity % 2 == 0:
        root_node, an_node, ch_node = ac_cluster.root_node, ac_node, pa_node
    else:
        root_node, an_node, ch_node = pa_cluster.root_node, pa_node, ac_node

    calc_delay_node = None if even_after_union else ch_node

    if create_junction:                                 # create junction-node on passive vertex
        j_node = junction_node(pa_vertex.sID)
        j_node.ancestor = an_node
        j_node.e = an_node.s //2
        an_node.children.append(j_node)
        pa_vertex.node = j_node
        if not even_after_union:
            calc_delay_node = j_node
        an_node = j_node

    make_ancestor_child(ch_node, True)                  # re-root child node as root of child-tree
    ch_node.ancestor = an_node                          # merge trees by adoption
    an_node.children.append(ch_node)

    if create_junction:                                 # Calculate child node edge to ancestor
        ch_node.e = ch_node.s // 2
    else:
        ch_node.e = (ac_node.s + pa_node.s) // 2

    root_node.calc_delay.append(calc_delay_node)        # store generator of undefined delay

    return root_node


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

    if node.children:
        parity = sum([1 - comp_tree_p_of_node(child) for child in node.children]) % 2
        if type(node) == anyon_node:
            node.p = parity
        else:
            node.p = 1 - parity
        return node.p
    else:
        node.p = 0
        return 0


def comp_tree_d_of_node(node, cluster):
    '''
    Recursive function to find the delay of a node and its children
    '''
    node.calc_delay = []
    node.w = 0

    if node.ancestor is None:
        node.d, cluster.mindl = 0, 0
        for child in node.children:
            comp_tree_d_of_node(child, cluster)
    else:
        ancestor = node.ancestor
        size_diff = ((node.s + node.g)//2 - (ancestor.s + ancestor.g)//2 + node.e*(-1)**(node.p + 1))
        support_fix = (node.g + ancestor.g)%2
        node.d = ancestor.d + 2*size_diff - support_fix

        if node.d < cluster.mindl:                  # store cluster minimum delay
            cluster.mindl = node.d
        for child in node.children:
            comp_tree_d_of_node(child, cluster)





































# end
