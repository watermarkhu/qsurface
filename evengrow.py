

class anyonnode(object):
    def __init__(self, id):

        self.id = id
        self.s = 0
        self.g = 0
        self.e = None
        self.c = 0
        self.p = 0
        self.d = 0
        self.w = 0
        self.bucket = None
        self.ancestor = None
        self.children = []

    def __repr__(self):
        children_id_list = [child.id for child in self.children]

        if self.ancestor:
            return "A{}^{}_{}".format(self.id, self.ancestor.id, children_id_list)
        else:
            return "A{}_{}".format(self.id, children_id_list)


def union(anode_p, p_tree_size, anode_c_list, c_tree_size):

    if p_tree_size < c_tree_size:
        anode_p, anode_c = anode_c, anode_p

    make_ancestor_child(anode_c)
    anode_c.ancestor = anode_p
    anode_p.children.append(anode_c)


def make_ancestor_child(anode):

    if anode is not None:
        make_ancestor_child(anode.ancestor)
        ancestor = anode.ancestor

        if ancestor is not None:
            ancestor.children.remove(anode)
            ancestor.ancestor = anode
            anode.children.append(ancestor)
