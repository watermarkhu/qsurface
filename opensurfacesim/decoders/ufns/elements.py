from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from opensurfacesim.codes.elements import AncillaQubit
from ..unionfind.elements import Cluster


class Node(ABC):
    """Element in the node-tree.

    Paramters
    ---------
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
    neighbors : list
        Neighboring nodes in the node-tree.
    root_list : list
        List of even subroots of merged node-trees.
    radius : int
        Node radius size.
    parity : {0,1}
        Node parity.
    delay : int
        Number of iterations to wait.
    waited : int
        Number of iterations waited.
    """

    short = "T"

    def __init__(self, primer: AncillaQubit):

        self.primer = primer
        primer.node = self

        self.old_bound = []
        self.new_bound = []
        self.neighbors = []
        self.root_list = []
        self.radius = 0
        self.parity = 0
        self.delay = 0
        self.waited = 0

    def __repr__(self):
        return f"{self.short}N{self.primer.loc}|{self.primer.z})"

    @property
    def _status(self):
        parity = "o" if self.parity else "e"
        return f"{self.radius}{parity}{self.waited}/{self.delay}"

    @property
    def _repr_status(self):
        return str(self) + self._status

    @abstractmethod
    def ns_parity(self):
        pass

    def ns_delay(self, parent: Optional[Tuple[Node, int]] = None, min_delay: Optional[int] = None):
        """
        .. math:: n_d = m_d + \floor{n_r-m_r}- (-1)^{n_p}\abs{(n,m)}.
        """
        self.root_list = []
        self.waited = 0

        if parent is not None:
            parent, edge = parent
            self.delay = parent.delay + (self.radius/2 - parent.radius/2) % 1 - edge * (-1) ** parent.parity
            if min_delay is None or (self.delay < min_delay):
                min_delay = self.delay

        for node, edge in self.neighbors:
            if node is not parent:
                min_delay = node.ns_delay((self, edge), min_delay)

        return min_delay


class Syndrome(Node):
    short = "S"
    def ns_parity(self, parent_node: Optional[Node] = None) -> int:
        """
        .. math:: s_p &= \hspace{.6cm}\big( \sum_{\mathclap{n \in \text{ children of } s}} (1+s_p) \big ) \bmod 2,
        """
        self.parity = (
            sum(
                [1 - node.ns_parity(self) for node, _ in self.neighbors if node is not parent_node]
            )
            % 2
        )
        return self.parity

class Junction(Node):
    short = "J"

    def ns_parity(self, parent_node: Optional[Node] = None) -> int:
        """
        .. math:: j_p &= 1 - \big(\sum_{\mathclap{n \in \text{ children of } j}} (1+n_p) \big) \bmod 2.
        """
        self.parity = 1 - (
            sum(
                [1 - node.ns_parity(self) for node, _ in self.neighbors if node is not parent_node]
            )
            % 2
        )
        return self.parity



class Boundary(Node):
    short = "B"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parity = 1

    def ns_parity(self, *args, **kwargs) -> int:
        return self.parity


class Filler(Node):
    short = "F"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parity = 1

    def ns_parity(self, *args, **kwargs) -> int:
        return self.parity
