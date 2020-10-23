from typing import List, Optional, Tuple
from ...codes.elements import AncillaQubit, Edge, PseudoQubit
from ..unionfind.sim import Toric as UFToric, Planar as UFPlanar
from ..unionfind.elements import Cluster
from .elements import Node, Syndrome, Junction, Boundary, Filler

UL = List[Tuple[AncillaQubit, Edge, AncillaQubit]]


class Toric(UFToric):
    """Union-Find Node-Suspension decoder for the toric lattice.
    
    Within the combined Union-Find and Node-Suspension data structure, every `~.unionfind.elements.Cluster` is partitioned into one or more `~.ufns.elements.Node`\ s. The ``node`` attribute is monkey-patched to the ``~.codes.elements.AncillaQubit` object to assist the identification of its parent `~.ufns.elements.Node`. 

    The boundary of every cluster is not stored at the cluster object, but divided under its partitioned nodes. Cluster growth is initiated from the root of the node-tree. The attributes ``root_node`` and ``min_delay`` are monkey-patched to the `~.unionfind.elements.Cluster` object to assist with cluster growth in the Node-Suspension data structure. See `grow_node` for more. 

    The current class inherits from `.unionfind.sim.Toric` for its application the Union-Find data structure for cluster growth and mergers. To maintain low operating complexity in UFNS, the following parameters are set of the Union-Find super. 

    =================   =======
    parameter           value
    =================   =======
    weighted_growth     True
    weighted_union      True
    dynamic_forest      True
    degenerate_union    False
    =================   =======

    Attributes
    ----------
    new_boundary : list
        List of newly found cluster boundary elements.
    """

    name = "Union-Find Node-Suspension"
    short = "ufns"

    syndromeNode = Syndrome
    junctionNode = Junction
    boundaryNode = Boundary
    fillerNode = Filler

    compatibility_measurements = dict(
        PerfectMeasurements=True,
        FaultyMeasurements=False,
    )
    compatibility_errors = dict(
        pauli=True,
        erasure=False,
    )

    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            "weighted_growth" : True,
            "weighted_union" : True,
            "dynamic_forest" : True,
            "degenerate_union" : False,
        })
        super().__init__(*args, **kwargs)

        self.code.ancillaQubit.node = None
        self.cluster.root_node = None
        self.cluster.min_delay = 0
        self.new_boundary = []
    """
    ================================================================================================
                                    General helper functions
    ================================================================================================
    """

    def cluster_add_ancilla(self, cluster: Cluster, ancilla: AncillaQubit, parent: Optional[AncillaQubit]=None, **kwargs):
        """Recursively adds erased edges to ``cluster`` and finds the new boundary.

        For a given ``ancilla``, this function finds the neighboring edges and ancillas that are in the the currunt cluster. If the newly found edge is erased, the edge and the corresponding ancilla will be added to the cluster, and the function applied recursively on the new ancilla. Otherwise, the neighbor is added to the new boundary ``self.new_boundary``.

        Parameters
        ----------
        cluster
            Current active cluster
        ancilla
            Ancilla from which the connected erased edges or boundary are searched.
        """
        cluster.add_ancilla(ancilla)
        if parent:
            ancilla.node = parent.node

        for key in ancilla.parity_qubits:
            (new_ancilla, edge) = self.get_neighbor(ancilla, key)

            if (
                "erasure" in self.code.errors
                and edge.qubit.erasure == self.code.instance
                and new_ancilla is not parent
                and self.support[edge] == 0
            ):  # if edge not already traversed
                if new_ancilla.cluster == cluster:  # cycle detected, peel edge
                    self._edge_peel(edge, variant="cycle")
                else:  # if no cycle detected
                    self.fillerNode(new_ancilla)
                    self._edge_full(ancilla, edge, new_ancilla)
                    self.cluster_add_ancilla(cluster, new_ancilla, parent=ancilla)

            else:  # Make sure new bound does not lead to self
                if new_ancilla.cluster is not cluster:
                    self.new_boundary.append((ancilla, edge, new_ancilla))

    def bound_ancilla_to_node(self):
        """Saves the new boundary to their respective nodes.
        
        Saves all the new boundaries found by `cluster_add_ancilla`, which are of the form ``[inner_ancilla, edge, outer_ancilla]``, to the node at ``inner_ancilla.node``. This method is called after cluster union in `union_bucket`, which also joins the node-trees, such that the new boundary is saved to the updated nodes. 
        """
        while self.new_boundary:
            boundary = self.new_boundary.pop()
            ancilla = boundary[0]
            ancilla.node.new_bound.append(boundary)
    """
    ================================================================================================
                                    1. Find clusters
    ================================================================================================
    """

    def find_clusters(self, **kwargs):
        """Initializes the clusters on the lattice.

        For every non-trivial ancilla on the lattice, a `~.unionfind.elements.Cluster` is initiated. If any set of ancillas are connected by some set of erased qubits, all connected ancillas are found by `cluster_add_ancilla` and a single cluster is initiated for the set.

        Additionally, a syndrome-node is initiated on the non-trivial ancilla -- a syndrome -- with the ancilla as primer. New boundaries are saved to the nodes by ``bound_ancilla_to_node``. 

        The cluster is then placed into a bucket based on its size and parity by `cluster_place_bucket`. See `grow_clusters` for more information on buckets.
        """
        plaqs, stars = self.get_syndrome()

        for ancilla in plaqs + stars:
            if ancilla.cluster is None or ancilla.cluster.instance != self.code.instance:
                node = self.syndromeNode(ancilla)
                cluster = self.cluster(self.cluster_index, self.code.instance)
                cluster.root_node = node
                self.cluster_add_ancilla(cluster, ancilla)
                self.cluster_place_bucket(cluster, -1)
                self.cluster_index += 1
                self.clusters.append(cluster)

        self.bound_ancilla_to_node()

        if self.config["print_steps"]:
            print(f"Found clusters:\n" + ", ".join(map(str, self.clusters)) + "\n")

    """
    ================================================================================================
                                    2(a). Grow clusters expansion
    ================================================================================================
    """

    def grow_boundary(
        self, cluster: Cluster, union_list: UL, **kwargs
    ):
        """Grows the boundary of the ``cluster``.

        See `grow_clusters` for more information. Each element in the ``root_list`` of the root node of the ``cluster`` is a subroot of an even subtree in the node-tree. From each of these subroots, the node parity and delays are calculated by `~.ufns.elements.ns_parity` and `~ufns.elements.ns_delay`. The node-tree is then recursively grown by `grow_node`.  

        Parameters
        ----------
        cluster
            The cluster to be grown.
        union_list
            List of odd-parity clusters to be placed in new buckets.
        """
        cluster.support = 1 - cluster.support

        if self.config["print_steps"]:
            print(f"{cluster}, ", end="")

        while cluster.root_node.root_list:
            node, edge, parent_node = cluster.root_node.root_list.pop()
            node.ns_parity(parent_node)
            min_delay = node.ns_delay((parent_node, edge))
            if min_delay < cluster.min_delay:
                cluster.min_delay = min_delay

        self.grow_node(cluster, cluster.root_node, union_list)

        if self.config["print_steps"]:
            print("")

    def grow_node(self, cluster: Cluster, node: Node, union_list: UL, parent_node: Optional[Node] = None):
        '''Recursive function that grows a ``node`` and its descendents. 

        Grows the boundary list that is stored at the current node if there the current node is not suspended. The condition required is the following:

        .. math: n_{\text{delay}} - n_{\text{waited}} - \min_{x \in \mathcal{N}}{n_{\text{delay}}} = 0

        where :math:`\mathcal{N}` is the node-tree. The minimal delay value in the node-tree here stored as ``cluster.min_delay``. Fully grown edges are added to ``union_list`` to be later considered by `union_bucket`. 

        Parameters
        ----------
        cluster
            Parent cluster object of ``node``. 
        node
            Node to consider for growth.
        union_list
            List of potential mergers between two cluster-distinct ancillas. 
        parent_node
            Parent node in the node-tree to indicate recursive direction.
        '''
        if self.config["print_tree"]:
            pass
        elif self.config["print_steps"]:
            print(node._repr_status)

        if node.delay - node.waited == cluster.min_delay:
            self._grow_node_boundary(node, union_list)
        else:
            node.waited += 1

        for child_node, _ in node.neighbors:
            if child_node is not parent_node:
                self.grow_node(cluster, child_node, union_list, node)

    def _grow_node_boundary(self, node: Node, union_list: UL):
        """Grows the boundary of a node."""
        node.radius += 1
        node.old_bound, node.new_bound = node.new_bound, []
        while node.old_bound:
            boundary = node.old_bound.pop()
            ancilla, new_edge, new_ancilla = boundary
            if self.support[new_edge] != 2:
                self._edge_grow(*boundary)
                if self.support[new_edge] == 2:
                    union_list.append(boundary)
                else:
                    node.new_bound.append(boundary)
    """
    ================================================================================================
                                    2(b). Grow clusters union
    ================================================================================================
    """
    def union_bucket(self, *args, **kwargs):
        # Inherited docstring
        super().union_bucket(*args, **kwargs)
        self.bound_ancilla_to_node()

    def _union_edge(
        self, edge: Edge, ancilla: AncillaQubit, new_ancilla: AncillaQubit, *args, **kwargs
    ):
        """Potentially merges two neighboring ancillas. 

        If the check by `_union_check` is passed, the clusters of ``ancilla`` and ``new_ancilla`` are merged. additionally, the node-trees either directly joined, or by the creation of a new *junction-node* which as ``new_ancilla`` as its primer. Weighted union is applied to ensure low operating complexity. 
        """
        cluster = self.get_cluster(ancilla)
        new_cluster = self.get_cluster(new_ancilla)

        if self._union_check(edge, ancilla, new_ancilla, cluster, new_cluster):

            node, new_node = ancilla.node, new_ancilla.node
            even = (cluster.parity + new_cluster.parity) % 2 == 0

            if not even and new_cluster.parity % 2 == 0:
                root_node, parent, child = cluster.root_node, node, new_node
            else:
                root_node, parent, child = new_cluster.root_node, new_node, node

            if not node.radius % 2 and new_node.radius > 1: # Connect via new junction-node
                junction = self.junctionNode(new_ancilla)
                new_ancilla.node = junction
                parent_edge, child_edge = parent.radius // 2, child.radius // 2
                junction.neighbors = [(parent, parent_edge), (child, child_edge)]
                parent.neighbors.append((junction, parent_edge))
                child.neighbors.append((junction, child_edge))
                calc_delay = None if even else [
                    junction, parent_edge, parent]
            else:                                         # Connect directly
                edge = (parent.radius + child.radius) // 2
                parent.neighbors.append((child, edge))
                child.neighbors.append((parent, edge))
                calc_delay = None if even else [child, edge, parent]
            root_node.root_list.append(calc_delay)

            string = "{}∪{}=".format(cluster, new_cluster) if self.config["print_steps"] else ""
            if cluster.size < new_cluster.size:
                cluster, new_cluster = new_cluster, cluster
            cluster.union(new_cluster)
            cluster.root_node = root_node
            if string:
                print(string, cluster)

class Planar(Toric, UFPlanar):
    """Union-Find Node-Suspension decoder for the planar lattice.
    
    See the description of `.ufns.sim.Toric`. 
    """
    pass