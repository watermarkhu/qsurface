from typing import List, Optional, Tuple
from ...codes.elements import AncillaQubit, Edge
from ..unionfind.sim import Toric as UFToric, Planar as UFPlanar
from ..unionfind.elements import Cluster
from .elements import Node, Syndrome, Junction, OddNode, print_tree

UL = List[Tuple[AncillaQubit, Edge, AncillaQubit]]


class Toric(UFToric):
    """Union-Find Node-Suspension decoder for the toric lattice.

    Within the combined Union-Find and Node-Suspension data structure, every `~.unionfind.elements.Cluster` is partitioned into one or more `~.ufns.elements.Node`\ s. The ``node`` attribute is monkey-patched to the `~.codes.elements.AncillaQubit` object to assist the identification of its parent `~.ufns.elements.Node`.

    The boundary of every cluster is not stored at the cluster object, but divided under its partitioned nodes. Cluster growth is initiated from the root of the node-tree. The attributes ``root_node`` and ``min_delay`` are monkey-patched to the `~.unionfind.elements.Cluster` object to assist with cluster growth in the Node-Suspension data structure. See `grow_node` for more.

    The current class inherits from `.unionfind.sim.Toric` for its application the Union-Find data structure for cluster growth and mergers. To maintain low operating complexity in UFNS, the following parameters are set of the Union-Find parent class.

    =================   =======
    parameter           value
    =================   =======
    weighted_growth     True
    weighted_union      True
    dynamic_forest      True
    =================   =======

    Attributes
    ----------
    new_boundary : list
        List of newly found cluster boundary elements.
    """

    name = "Union-Find Node-Suspension"
    short = "ufns"

    _Syndrome = Syndrome
    _Junction = Junction
    _OddNode = OddNode

    compatibility_measurements = dict(
        PerfectMeasurements=True,
        FaultyMeasurements=False,
    )
    compatibility_errors = dict(
        pauli=True,
        erasure=False,
    )

    def __init__(self, *args, **kwargs) -> None:
        kwargs.update(
            {
                "weighted_growth": True,
                "weighted_union": True,
                "dynamic_forest": True,
            }
        )
        super().__init__(*args, **kwargs)

        self.code._AncillaQubit.node = None
        self._Cluster.root_node = None
        self._Cluster.min_delay = 0
        self.new_boundary = []

    """
    ================================================================================================
                                    General helper functions
    ================================================================================================
    """

    def cluster_add_ancilla(
        self,
        cluster: Cluster,
        ancilla: AncillaQubit,
        parent: Optional[AncillaQubit] = None,
        **kwargs,
    ):
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

        for (new_ancilla, edge) in self.get_neighbors(ancilla).values():
            if (
                "erasure" in self.code.errors
                and edge.qubit.erasure == self.code.instance
                and new_ancilla is not parent
                and self.support[edge] == 0
            ):  # if edge not already traversed
                if new_ancilla.cluster == cluster:  # cycle detected, peel edge
                    self._edge_peel(edge, variant="cycle")
                else:  # if no cycle detected
                    self._OddNode(new_ancilla)
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

        The cluster is then placed into a bucket based on its size and parity by `place_bucket`. See `grow_clusters` for more information on buckets.
        """
        plaqs, stars = self.get_syndrome()

        for ancilla in plaqs + stars:
            if ancilla.cluster is None or ancilla.cluster.instance != self.code.instance:
                node = self._Syndrome(ancilla)
                cluster = self._Cluster(self.cluster_index, self.code.instance)
                cluster.root_node = node
                self.cluster_add_ancilla(cluster, ancilla)
                self.cluster_index += 1
                self.clusters.append(cluster)

        self.bound_ancilla_to_node()
        self.place_bucket(self.clusters, -1)

        if self.config["print_steps"]:
            print(f"Found clusters:\n" + ", ".join(map(str, self.clusters)) + "\n")

    """
    ================================================================================================
                                    2(a). Grow clusters expansion
    ================================================================================================
    """

    def grow_clusters(self, **kwargs):
        """Grows odd-parity clusters outward for union with others until all clusters are even.

        Lists of odd-parity clusters are maintained at ``self.buckets``. Starting from bucket 0, odd-parity clusters are popped from the bucket by 'grow_bucket and grown at the boundary by `grow_boundary` by adding 1 for every boundary edge in ``cluster.bound`` in ``self.support``. Grown clusters are then placed in a new bucket by `place_bucket` based on its size if it has odd parity.

        Edges are fully added to the cluster per two growth iterations. Since a cluster with half-grown edges at the boundary has the same size (number of ancillas) as before growth, but is non-arguably *bigger*, the degeneracy in cluster size is differentiated by ``cluster.support``. When an union occurs between two clusters during growth, if the merged cluster is odd, it is placed in a new bucket. Thus the real bucket number is saved at the cluster locally as ``cluster.bucket``. These two checks are performed before a cluster is grown in `grow_bucket`.

        The chronology of events per bucket must be the following:

        1.  Grow all clusters in the bucket if checks passed.

            *   Add all odd-parity clusters after growth to ``place_list``.
            *   Add all merging clusters to ``union_list``.

        2.  Merge all clusters in ``union_list``

            *   Add odd-parity clusters after union to ``place_list``.

        3.  Place all clusters in ``place_list`` in new bucket if parity is odd.

        For clusters with ``cluster.support==1`` or with half-grown edges at the boundary, the new boundary at ``clusters.new_bound`` consists of the same half-grown edges. For clusters with ``cluster.support==0``, the new boundary is found by ``cluster_add_ancilla``.

        The current implementation of `grow_clusters` for the ``ufns`` decoder currently includes a work-around for a non-frequently occuring bug. Since the grown of a cluster is separated into nodes, and nodes may be *buried* by surrounding cluster trees such that it is an interior element and has no boundaries, it may be possible that when an odd cluster is grown no edges are actually added to the cluster. In this case, due to cluster parity duality the odd cluster will be placed in the same bucket after two rounds of growth. The work-around is to always check if the previous bucket is empty before moving on to the next one.
        """
        self.bucket_i = 0

        while self.bucket_i < self.buckets_num:

            if self.bucket_i > self.bucket_max_filled:
                break

            if self.bucket_i in self.buckets and self.buckets[self.bucket_i] != []:
                union_list, place_list = self.grow_bucket(self.buckets.pop(self.bucket_i), self.bucket_i)
                self.union_bucket(union_list)
                self.place_bucket(place_list, self.bucket_i)

            if self.buckets[self.bucket_i - 1] != []:
                self.bucket_i -= 1
            else:
                self.bucket_i += 1

    def grow_boundary(self, cluster: Cluster, union_list: UL, **kwargs):
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

        for node, edge, parent_node in cluster.root_node.root_list:
            node.ns_parity(parent_node)
            min_delay = node.ns_delay((parent_node, edge))
            if min_delay < cluster.min_delay:
                cluster.min_delay = min_delay
        if cluster.root_node.root_list:
            cluster.root_node.root_list = []
            if self.config["print_tree"]:
                print_tree(cluster.root_node)

        self.grow_node(cluster, cluster.root_node, union_list)

        if self.config["print_steps"]:
            print("")

    def grow_node(self, cluster: Cluster, node: Node, union_list: UL, parent_node: Optional[Node] = None):
        """Recursive function that grows a ``node`` and its descendents.

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
        """
        if node.delay - node.waited == cluster.min_delay:
            self.grow_node_boundary(node, union_list)
            if self.config["print_steps"]:
                print(node._repr_status, end="; ")
        else:
            node.waited += 1

        for child_node, _ in node.neighbors:
            if child_node is not parent_node:
                self.grow_node(cluster, child_node, union_list, node)

    def grow_node_boundary(self, node: Node, union_list: UL):
        """Grows the boundary of a ``node``."""
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

    def union_bucket(self, union_list: List[Tuple[AncillaQubit, Edge, AncillaQubit]], **kwargs):
        """Potentially merges two neighboring ancillas.

        If the check by `union_check` is passed, the clusters of ``ancilla`` and ``new_ancilla`` are merged. additionally, the node-trees either directly joined, or by the creation of a new *junction-node* which as ``new_ancilla`` as its primer. Weighted union is applied to ensure low operating complexity.
        """
        if union_list and self.config["print_steps"]:
            print("Fusing clusters")

        for ancilla, edge, new_ancilla in union_list:
            cluster = self.get_cluster(ancilla)
            new_cluster = self.get_cluster(new_ancilla)

            if self.union_check(edge, ancilla, new_ancilla, cluster, new_cluster):

                node, new_node = ancilla.node, new_ancilla.node
                even = (cluster.parity + new_cluster.parity) % 2 == 0

                if not even and new_cluster.parity % 2 == 0:
                    root_node, parent, child = cluster.root_node, node, new_node
                else:
                    root_node, parent, child = new_cluster.root_node, new_node, node

                if not node.radius % 2 and new_node.radius > 1:  # Connect via new junction-node
                    junction = self._Junction(new_ancilla)
                    new_ancilla.node = junction
                    parent_edge, child_edge = parent.radius // 2, child.radius // 2
                    junction.neighbors = [(parent, parent_edge), (child, child_edge)]
                    parent.neighbors.append((junction, parent_edge))
                    child.neighbors.append((junction, child_edge))
                    calc_delay = [junction, parent_edge, parent]
                else:  # Connect directly
                    edge = (parent.radius + child.radius) // 2
                    parent.neighbors.append((child, edge))
                    child.neighbors.append((parent, edge))
                    calc_delay = [child, edge, parent]
                if not even:
                    root_node.root_list.append(calc_delay)

                string = "{}∪{}=".format(cluster, new_cluster) if self.config["print_steps"] else ""
                if cluster.size < new_cluster.size:
                    cluster, new_cluster = new_cluster, cluster
                cluster.union(new_cluster)
                cluster.root_node = root_node
                if string:
                    print(string, cluster)

        if union_list and self.config["print_steps"]:
            print("")
        self.bound_ancilla_to_node()


class Planar(Toric, UFPlanar):
    """Union-Find Node-Suspension decoder for the planar lattice.

    See the description of `.ufns.sim.Toric`.
    """

    pass
