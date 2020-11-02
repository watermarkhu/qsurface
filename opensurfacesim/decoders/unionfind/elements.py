from __future__ import annotations
from ...codes.elements import AncillaQubit, PseudoQubit


class Cluster(object):
    """CLuster of `~.elements.AncillaQubit` objects.

    A disjoint set, or cluster, of ancilla-qubits. The size of the cluster is equal to the number of qubits in the cluster. The parity of the cluster is equal to the number of non-trivial ancilla-qubits in the cluster.

    A cluster can be joined with another by `union`. Joined clusters are stored in the union-find data structure [tarjan1975efficiency]_. The representative element or root cluster is returned by `find`.

    Parameters
    ----------
    index
        Indicator index number.
    instance :
        The epoch timestamp of the simulation.

    Attributes
    ----------
    size : int
        Size of this cluster based on the number contained ancillas.
    support : int
        Growth state of the cluster.
    parity : int
        Parity of this cluster based on the number non-trivial ancilla-qubits.
    parent : `~.unionfind.elements.Cluster`
        The parent cluster of the current cluster.
    bound, new_bound : list, `[[inner_ancilla, edge, outer_ancilla],...]`
        The current and next boundary of the current cluster.
    bucket : int
        The bucket number the current ancilla belongs to.
    on_bound : bool
        Whether this cluster is connected to the boundary.
    """

    def __init__(self, index: int, instance: float, **kwargs):
        self.index = index
        self.instance = instance
        self.size = 0
        self.support = 0
        self.parity = 0
        self.parent = self
        self.bound = []
        self.new_bound = []
        self.bucket = -1
        self.on_bound = False

    def __repr__(self):
        sep = "|" if self.on_bound else ":"
        return "C{}({}{}{})".format(self.index, self.size, sep, self.parity)

    def __hash__(self):
        return self.index, self.instance

    def add_ancilla(self, ancilla: AncillaQubit):
        """Adds an ancilla to a cluster."""
        ancilla.cluster = self
        if type(ancilla) is AncillaQubit:
            self.size += 1
            if ancilla.syndrome:
                self.parity += 1
        elif type(ancilla) is PseudoQubit:
            self.on_bound = True

    def union(self, cluster: Cluster, **kwargs):
        """Merges two clusters.

        The `cluster` is made a child of the current cluster. The joined size and parity attributes are updated.

        Parameters
        ----------
        cluster
            The cluster to merge with ``self``.

        Examples
        --------

        For two clusters ``cl0`` and ``cl1``, ``cl0.union(cl1)`` results in the following tree::

              cl0
              /
            cl1


        """
        cluster.parent = self
        self.size += cluster.size
        self.parity += cluster.parity
        self.new_bound.extend(cluster.new_bound)
        self.on_bound = self.on_bound or cluster.on_bound

    def find(self, **kwargs) -> Cluster:
        """Finds the representative root cluster. 
        
        The function is applied recursively until the root element of the union-find tree is encountered. The representative root element is returned. Path compression is applied to reduce the depth of the tree. 

        Examples
        --------
        For joined clusters in the union-find data structure::

                cl0
                / \\
              cl1 cl2
              /
            cl2

        the representative element can be found by

            >>> cl2.find()
            cl0
        """
        if self.parent is not self:
            self.parent = self.parent.find()
        return self.parent
