from __future__ import annotations
from typing import Optional, Tuple, List
from ...codes.elements import AncillaQubit
import itertools
import pptree
import math


class SyndromeNode(object):
    """Element in the node-tree.

    A subgraph :math:`\\mathcal{V}\\subseteq C` is a spanning-tree of a cluster :math:`C` if it is a connected acyclic subgraph that includes all vertices of :math:`C` and a minimum number of edges. We call the spanning-tree of a cluster its ancilla-tree. An acyclic connected spanning-forest is required for the Union-Find Decoder.

    A node-tree :math:`\\mathcal{N}` is a partition of a ancilla-tree :math:`\\mathcal{V}`, such that each element of the partition -- which we call a *node* :math:`n` -- represents a set of adjacent vertices that lie at the same distance -- the *node radius :math:`r` -- from the *primer ancilla*, which initializes the node and lies at its center. The node-tree is a directed acyclic graph, and its edges :math:`\\mathcal{E}_i` have lengths equal to the distance between the primer vertices of neighboring nodes.

    Parameters
    ----------
    primer
        Primer ancilla-qubit.

    Attributes
    ----------
    short : str
        Short name of the node.
    old_bound : list
        Current boundary edges.
    new_bound : list
        Next boundary edges.
    neighbors : dict
        Neighboring nodes in the node-tree.
    radius : int
        Node radius size.
    parity : {0,1}
        Node parity.
    delay : int
        Number of iterations to wait.
    waited : int
        Number of iterations waited.
    """

    short = "S"

    def __init__(self, primer: AncillaQubit):

        # Vertex properties
        self.primer = primer
        primer.node = self
        self.old_bound = self.new_bound = []
        self.neighbors = {}

        # Nodetree properties
        self.radius = self.parity = self.delay = 0

        # Priority heap properties
        self.parent = self.child = self.left = self.right = None
        self.degree = 0
        self.mark = False

    def __repr__(self):
        return f"{self.short}N({self.primer.loc[0]},{self.primer.loc[1]}|{self.primer.z})"

    @property
    def _status(self):
        parity = "o" if self.parity else "e"
        return f"{self.radius}{parity}{self.waited}/{self.delay}"

    @property
    def _repr_status(self):
        return str(self) + self._status

    def get_children(self, parent: Optional[SyndromeNode] = None):
        return [neighbor for neighbor in self.neighbors.keys() if neighbor is not parent]

    def ns_parity(self, 
        parent: Optional[SyndromeNode] = None, 
        **kwargs
    ) -> int:
        """Calculates the node parity.

        Tail recursive function that calculates the parities of the current node and all its descendent nodes.

        .. math:: s_p = \\big( \\sum_{n \\in \\text{ children of } s} (1+s_p) \\big) \\bmod 2

        Parameters
        ----------
        parent
            Parent node in node-tree to indicate direction.
        """
        self.parity = sum(
            [
                1 - node.ns_parity(self) 
                for node in self.get_children(parent)
            ]
        ) % 2
        return self.parity


    def ns_delay(self, parent: Optional[SyndromeNode] = None, **kwargs) -> int:
        """Calculates the node delay.

        Head recursive function that calculates the delays of the current node and all its descendent nodes.

        .. math:: n_d = m_d + \\lfloor n_r-m_r \\rfloor - (-1)^{n_p} |(n,m)|

        Parameters
        ----------
        parent
            Parent node in node-tree to indicate direction.
        """

        if parent is not None:
            edge = self.neighbors[parent]
            self.delay = (parent.delay 
                + int((self.radius / 2 - parent.radius / 2) % 1)
                - edge * (-1) ** self.parity
            )

        for node in self.get_children(parent=parent):
            node.ns_delay(parent=self)



class JunctionNode(SyndromeNode):
    short = "J"

    def ns_parity(self, *args, **kwargs) -> int:
        """Calculates the node parity.

        Tail recursive function that calculates the parities of the current node and all its children.

        .. math:: j_p = 1 - \\big(\\sum_{n \\in \\text{ children of } j} (1+n_p) \\big) \\bmod 2.

        Parameters
        ----------
        parent_node
            Parent node in node-tree to indicate direction.
        """
        self.parity = 1 - super().ns_parity(*args, **kwargs)
        return self.parity


class OddNode(SyndromeNode):
    short = "O"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parity = 1

    def ns_parity(self, *args, **kwargs) -> int:
        # Inherited docsting
        return self.parity


def print_tree(current_node: SyndromeNode, parent_node: Optional[SyndromeNode] = None):
    """Prints the node-tree of ``current_node`` and its descendents.

    Utilizes `pptree <https://pypi.org/project/pptree/>`_ to print a tree of nodes, which requires a list of children elements per node. Since the node-tree is semi-directional (the root can be any element in the tree), we need to traverse the node-tree from ``current_node`` in all directions except for the ``parent_node`` to find the children attributes for the current direction.

    Parameters
    ----------
    current_node
        Current root of the node-tree to print.
    parent_node
        Parent node which will not be printed.
    """

    def get_children(node, parent=None):
        node.children = [child for child, _ in node.neighbors if child is not parent]
        for child in node.children:
            get_children(child, node)

    get_children(current_node, parent_node)
    pptree.print_tree(current_node, childattr="children", nameattr="_repr_status", horizontal=True)



class FibonacciHeap:
    """
    From https://github.com/danielborowski/fibonacci-heap-python
    """

    def __init__(self) -> None:

        # pointer to the head and minimum node in the root list
        self.root_list, self.min_node = None, None

        # maintain total node count in full fibonacci heap
        self.total_nodes = 0

    def __repr__(self) -> str:
        if self.min_node:
            return "Fibonacci Heap: " + ", ".join(
                [str(n) for n in itertools.islice(self.iterate(self.find_min()), 3)]
            ) + "..."
        else:
            return "Empty Fibonacci Heap"


    # function to iterate through a doubly linked list
    def iterate(self, head):
        node = stop = head
        flag = False
        while True:
            if node == stop and flag is True:
                break
            elif node == stop:
                flag = True
            yield node
            node = node.right


    # return min node in O(1) time
    def find_min(self):
        return self.min_node

    # extract (delete) the min node from the heap in O(log n) time
    # amortized cost analysis can be found here (http://bit.ly/1ow1Clm)
    def extract_min(self):
        z = self.min_node
        if z is not None:
            if z.child is not None:
                # attach child nodes to root list
                children = [x for x in self.iterate(z.child)]
                for i in range(0, len(children)):
                    self.merge_with_root_list(children[i])
                    children[i].parent = None
            self.remove_from_root_list(z)
            # set new min node in heap
            if z == z.right:
                self.min_node = self.root_list = None
            else:
                self.min_node = z.right
                self.consolidate()
            self.total_nodes -= 1
        return z

    # insert new node into the unordered root list in O(1) time
    # returns the node so that it can be used for decrease_key later
    def insert(self, n: SyndromeNode):
        n.left = n.right = n
        self.merge_with_root_list(n)
        if self.min_node is None or n.delay < self.min_node.delay:
            self.min_node = n
        self.total_nodes += 1
        return n

    # modify the key of some node in the heap in O(1) time
    def decrease_key(self, node: SyndromeNode, delay: int):
        if delay > node.delay:
            return None
        node.delay = delay
        y = node.parent
        if y is not None and node.delay < y.delay:
            self.cut(node, y)
            self.cascading_cut(y)
        if node.delay < self.min_node.delay:
            self.min_node = node

    # merge two fibonacci heaps in O(1) time by concatenating the root lists
    # the root of the new root list becomes equal to the first list and the second
    # list is simply appended to the end (then the proper min node is determined)
    def merge(self, h2):
        H = FibonacciHeap()
        H.root_list, H.min_node = self.root_list, self.min_node
        # fix pointers when merging the two heaps
        last = h2.root_list.left
        h2.root_list.left = H.root_list.left
        H.root_list.left.right = h2.root_list
        H.root_list.left = last
        H.root_list.left.right = H.root_list
        # update min node if needed
        if h2.min_node.delay < H.min_node.delay:
            H.min_node = h2.min_node
        # update total nodes
        H.total_nodes = self.total_nodes + h2.total_nodes
        return H

    # if a child node becomes smaller than its parent node we
    # cut this child node off and bring it up to the root list
    def cut(self, node: SyndromeNode, y):
        self.remove_from_child_list(y, node)
        y.degree -= 1
        self.merge_with_root_list(node)
        node.parent = None
        node.mark = False

    # cascading cut of parent node to obtain good time bounds
    def cascading_cut(self, y):
        z = y.parent
        if z is not None:
            if y.mark is False:
                y.mark = True
            else:
                self.cut(y, z)
                self.cascading_cut(z)

    # combine root nodes of equal degree to consolidate the heap
    # by creating a list of unordered binomial trees
    def consolidate(self):
        A = [None] * int(math.log(self.total_nodes) * 2)
        nodes = [w for w in self.iterate(self.root_list)]
        for w in range(0, len(nodes)):
            x = nodes[w]
            d = x.degree
            while A[d] != None:
                y = A[d]
                if x.delay > y.delay:
                    temp = x
                    x, y = y, temp
                self.heap_link(y, x)
                A[d] = None
                d += 1
            A[d] = x
        # find new min node - no need to reconstruct new root list below
        # because root list was iteratively changing as we were moving
        # nodes around in the above loop
        for i in range(0, len(A)):
            if A[i] is not None:
                if A[i].delay < self.min_node.delay:
                    self.min_node = A[i]

    # actual linking of one node to another in the root list
    # while also updating the child linked list
    def heap_link(self, y: SyndromeNode, x: SyndromeNode):
        self.remove_from_root_list(y)
        y.left = y.right = y
        self.merge_with_child_list(x, y)
        x.degree += 1
        y.parent = x
        y.mark = False

    # merge a node with the doubly linked root list
    def merge_with_root_list(self, node: SyndromeNode):
        if self.root_list is None:
            self.root_list = node
        else:
            node.right = self.root_list.right
            node.left = self.root_list
            self.root_list.right.left = node
            self.root_list.right = node

    # merge a node with the doubly linked child list of a root node
    def merge_with_child_list(self, parent: SyndromeNode, node: SyndromeNode):
        if parent.child is None:
            parent.child = node
        else:
            node.right = parent.child.right
            node.left = parent.child
            parent.child.right.left = node
            parent.child.right = node

    # remove a node from the doubly linked root list
    def remove_from_root_list(self, node: SyndromeNode):
        if node == self.root_list:
            self.root_list = node.right
        node.left.right = node.right
        node.right.left = node.left

    # remove a node from the doubly linked child list
    def remove_from_child_list(self, parent: SyndromeNode, node: SyndromeNode):
        if parent.child == parent.child.right:
            parent.child = None
        elif parent.child == node:
            parent.child = node.right
            node.right.parent = parent
        node.left.right = node.right
        node.right.left = node.left