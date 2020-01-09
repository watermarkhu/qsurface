import printing as pr
from termcolor import colored as cs

class anyon_node(object):
    '''
    Anyon node object - element in the aj-tree
    var id        id number (loc)
    var ancestor  ancestor of node in anyontree
    var e         length of edge connectint to ancestor
    var children  list of children nodes
    var s         size, number of growth iterations
    var g         growth state \ parity of s
    var c         number of total descendent anyon nodes
    var p         parity of node \ parity of c
    var d         delay, iterations to wait
    var w         waited, iterations already waited
    '''

    def __init__(self, id):

        self.type = "A"
        self.id = id
        self.ancestor = None
        self.e = None
        self.children = []
        self.s = 0
        # self.c = 0
        self.p = 0
        self.d = 0
        self.w = 0
        self.bucket = None

    @property
    def g(self):
        return self.s % 2

    # @property
    # def p(self):
    #     return self.c % 2

    @property
    def delay(self):
        return self.d

    @property
    def short_id(self):
        type = "s" if self.id[0] == 0 else "p"
        return self.type + type + "{},{}".format(self.id[1], self.id[2])

    @property
    def tree_rep(self):
        return self.short_id + cs(self.s, "red") + cs(self.p, "magenta") + cs(self.delay, "cyan") + cs(self.w, "green") + cs(self.e, "yellow")

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

    def __init__(self, id, anodes, pnode):
        super().__init__(id)
        self.type = "J"
        self.anodes = anodes
        self.ancestor = pnode
        self.e = pnode.s // 2
        pnode.children.append(self)

    @property
    def delay(self):
        '''
        delay defined as minimal delay from list of rooted anyon-nodes
        '''
        return min([anode.d for anode in self.anodes])


def union(main_vertex, grow_vertex, main_cluster, grow_cluster):
    '''
    var main_vertex   merging vertex of base cluster
    var grow_vertex   merging vertex of grow cluster
    var b_tree_size   size of anyon_tree of base cluster
    var g_tree_size   size of anyon_tree of grow cluster
    '''
    b_node, g_node = main_vertex.node, grow_vertex.node

    if main_cluster.tree_size > grow_cluster.tree_size:
        an_node, ch_node = b_node, g_node
        root_node = main_cluster.root_node
        main_cluster.tree_size += grow_cluster.tree_size
    else:
        an_node, ch_node = g_node, b_node
        root_node = grow_cluster.root_node
        grow_cluster.tree_size += main_cluster.tree_size

    # Create junction node if union on vertex
    if b_node.g == 0:
        node_list = []
        for node in [b_node, g_node]:
            if type(node) == anyon_node:
                node_list.append(node)
            elif type(node) == junction_node:
                node_list.extend(node.anodes)
            else:
                raise TypeError()

        # create junction-node as child of previous ancestor, junction_node has now role of ancestor in union
        an_node = junction_node(grow_vertex.sID, node_list, an_node)
        grow_vertex.node = an_node

    make_ancestor_child(ch_node, True)
    ch_node.ancestor = an_node
    an_node.children.append(ch_node)

    # Calculate child node edge to ancestor
    if b_node.g == 0:
        ch_node.e = b_node.s // 2
    else:
        ch_node.e = (b_node.s + g_node.s) // 2

    return root_node


def make_ancestor_child(node, main_level=False):
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

        if main_level:
            node.ancestor = None
            node.e = None


def comp_tree_delay(cluster):

    cluster.root_node = go_to_root_cluster(cluster.root_node)
    comp_tree_p_children(cluster.root_node)
    comp_tree_delay_of_node(cluster.root_node, cluster)

    pr.print_tree(cluster.root_node, "children", "tree_rep")


def go_to_root_cluster(node):
    if node.ancestor is None:
        return node
    else:
        return go_to_root_cluster(node.ancestor)


def comp_tree_number_of_children(node):

    if node.children:
        num_child = 0
        for child in node.children:
            num_child += comp_tree_number_of_children(child)
        node.c = num_child

        if type(node) == anyon_node:
            return num_child + 1
        elif type(node) == junction_node:
            return num_child
        else:
            raise TypeError()
    else:
        node.c = 0
        return 1

def comp_tree_p_children(node):

    if node.children:
        parity = 0
        for child in node.children:
            parity = int(parity == comp_tree_p_children(child))
        node.p = parity

        if type(node) == anyon_node:
            return parity
        elif type(node) == junction_node:
            return 1 - parity
        else:
            raise TypeError()
    else:
        node.p = 0
        return 0

def comp_tree_p_ancestor(node):

    parity = 0
    for child in node.children:
        if type(child) == anyon_node:
            parity = int(parity == child.p)
        elif type(child) == junction_node:
            parity = int(parity != child.p)
        else:
            raise TypeError()
    node.c = parity

    comp_tree_p_ancestor(node.ancestor)


def comp_tree_delay_of_node(node, cluster, ancestor_data=None):

    if node.ancestor is None:
        node.d, cluster.mindl = 0, 0

        for child in node.children:
            comp_tree_delay_of_node(child, cluster)
    else:
        if type(node) == anyon_node:

            if ancestor_data is None:
                node_e = node.e
                ancestor = node.ancestor
            else:
                node_e = node.e + ancestor_data[0]*(-1)**((node.p + node.ancestor.p)%2 + 1)
                ancestor = ancestor_data[1]

            size_diff = ((node.s + node.g)//2 - (ancestor.s + ancestor.g)//2 + node_e*(-1)**(node.p + 1))
            support_fix = (node.g + ancestor.g)%2
            node.d = ancestor.d + 2*size_diff - support_fix

            if node.d < cluster.mindl:
                cluster.mindl = node.d

            for child in node.children:
                comp_tree_delay_of_node(child, cluster)

        elif type(node) == junction_node:

            sum_ekl = node.e if ancestor_data is None else node.e + ancestor_data[0]

            if type(node.ancestor) == anyon_node:
                ancestor_data = [sum_ekl, node.ancestor]
            else:
                ancestor_data[0] = sum_ekl

            for child in node.children:
                comp_tree_delay_of_node(child, cluster, ancestor_data)

        else:
            raise TypeError()



































# end
