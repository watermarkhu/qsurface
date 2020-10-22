from typing import List, Optional, Tuple
from ...codes.elements import AncillaQubit, Edge, PseudoQubit
from ..unionfind.sim import Toric as UFToric, Planar as UFPlanar
from ..unionfind.elements import Cluster
from .elements import Node, Syndrome, Junction, Boundary, Filler

UL = List[Tuple[AncillaQubit, Edge, AncillaQubit]]


class Toric(UFToric):
    """Union-Find Node-Suspension decoder for the toric lattice."""

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

        self.boundary_ancillas = []



    """
    ================================================================================================
                                    General helper functions
    ================================================================================================
    """

    def cluster_find_ancillas(self, cluster: Cluster, ancilla: AncillaQubit, **kwargs):
        """Recursively adds erased edges to ``cluster`` and finds the new boundary.

        For a given ``ancilla``, this function finds the neighboring edges and ancillas that are in the the currunt cluster. If the newly found edge is erased, the edge and the corresponding ancilla will be added to the cluster, and the function applied recursively on the new ancilla. Otherwise, the neighbor is added to the new boundary ``self.new_bound``.

        Parameters
        ----------
        cluster
            Current active cluster
        ancilla
            Ancilla from which the connected erased edges or boundary are searched.
        """

        for key in ancilla.parity_qubits:
            (new_ancilla, edge) = self.get_neighbor(ancilla, key)

            if (
                "erasure" in self.code.errors and edge.qubit.erasure == self.code.instance
            ):  # if edge not already traversed
                if self.support[edge] == 0:
                    if new_ancilla.cluster == cluster:  # cycle detected, peel edge
                        self._edge_peel(edge, variant="cycle")
                    else:  # if no cycle detected
                        self.fillerNode(new_ancilla)
                        cluster.add_ancilla(new_ancilla)
                        self._edge_full(ancilla, edge, new_ancilla)
                        self.cluster_find_ancillas(cluster, new_ancilla)

            else:  # Make sure new bound does not lead to self
                if new_ancilla.cluster is not cluster:
                    self.boundary_ancillas.append((ancilla, edge, new_ancilla))

    def bound_ancilla_to_node(self):
        while self.boundary_ancillas:
            boundary = self.boundary_ancillas.pop()
            ancilla = boundary[0]
            ancilla.node.new_bound.append(boundary)
    """
    ================================================================================================
                                    1. Find clusters
    ================================================================================================
    """

    def find_clusters(self, **kwargs):
        """Initializes the clusters on the lattice.

        For every non-trivial ancilla on the lattice, a `~.unionfind.elements.Cluster` is initiated. If any set of ancillas are connected by some set of erased qubits, all connected ancillas are found by `cluster_find_ancillas` and a single cluster is initiated for the set.

        Additionally, a syndrome-node is initiated on the non-trivial ancilla -- a syndrome -- with the ancilla as primer.

        The cluster is then placed into a bucket based on its size and parity by `cluster_place_bucket`. See `grow_clusters` for more information on buckets.
        """
        plaqs, stars = self.get_syndrome()

        for ancilla in plaqs + stars:
            if ancilla.cluster is None or ancilla.cluster.instance != self.code.instance:
                node = self.syndromeNode(ancilla)
                cluster = self.cluster(self.cluster_index, self.code.instance)
                cluster.add_ancilla(ancilla)
                cluster.root_node = node
                self.cluster_find_ancillas(cluster, ancilla)
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

    def _grow_boundary(
        self, cluster: Cluster, union_list: UL, **kwargs
    ):
        """Grows the boundary of the ``cluster``.

        See `grow_clusters` for more information.

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
        '''
        Grows the boundary list that is stored at the current node using the directed base-tree.
        Fully grown edges are added to the fusion list.

        .. math: \m{s}(n) = n_d - \max_{x \in \nset}{x_d} - n_w. 

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
                self._grow_node(cluster, child_node, union_list, node)

    def _grow_node_boundary(self, node: Node, union_list: UL):
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
        super().union_bucket(*args, **kwargs)
        self.bound_ancilla_to_node()

    def _union_edge(
        self, edge: Edge, ancilla: AncillaQubit, new_ancilla: AncillaQubit, *args, **kwargs
    ):
        """Merges the clusters of ``ancilla`` and ``new_ancilla`` on ``edge.

        Weighted union is conditionally applied. See `union_bucket` for more information.
        """
        cluster = self.get_cluster(ancilla)
        new_cluster = self.get_cluster(new_ancilla)

        if self._union_check(edge, ancilla, new_ancilla, cluster, new_cluster):

            root_node = self.join_node_trees(ancilla, new_ancilla, cluster, new_cluster)
            string = "{}∪{}=".format(cluster, new_cluster) if self.config["print_steps"] else ""
            if cluster.size < new_cluster.size:
                cluster, new_cluster = new_cluster, cluster
            cluster.union(new_cluster)
            cluster.root_node = root_node
            if string:
                print(string, cluster)

    def _union_check(
        self, edge: Edge, ancilla: AncillaQubit, new_ancilla: AncillaQubit, cluster: Cluster, new_cluster: Cluster
    ) -> bool:
        """Checks whether ``cluster`` and ``new_cluster`` can be joined on ``edge``.

        See `union_bucket` for more information.
        """
        if new_cluster is None or new_cluster.instance != self.code.instance:
            new_ancilla.node = ancilla.node
            self.boundary_ancillas.append((ancilla, edge, new_ancilla))
            cluster.add_ancilla(new_ancilla)
            self.cluster_find_ancillas(cluster, new_ancilla)
        elif new_cluster is cluster:
            if self.config["dynamic_forest"]:
                self._edge_peel(edge, variant="cycle")
        else:
            return True
        return False

    def join_node_trees(self,
        ancilla: AncillaQubit,
        new_ancilla: AncillaQubit,
        cluster: Cluster,
        new_cluster: Cluster
    ) -> Node:
        '''
        Union of two anyontrees.
        ancilla   merging vertex of base cluster
        new_ancilla   merging vertex of grow cluster

        node     root of active vertex
        new_node     root of passive vertex
        parent     ancestor node during union
        child     child node during union

        even:       if cluster is even after union, union of trees is done by weighted union
                                else, union is done by always appending even tree to odd tree,
                                delay calculation is needed from the child node (of union duo) and descendents
        '''
        node, new_node = ancilla.node, new_ancilla.node
        even = (cluster.parity + new_cluster.parity) % 2 == 0

        if not even and new_cluster.parity % 2 == 0:
            root_node, parent, child = cluster.root_node, node, new_node
        else:
            root_node, parent, child = new_cluster.root_node, new_node, node

        if not node.radius % 2 and new_node.radius > 1: # Connect via new juntion-node
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

        # store generator of undefined delay
        root_node.root_list.append(calc_delay)

        return root_node

class Planar(Toric, UFPlanar):
    
    def _union_check(
        self, edge: Edge, ancilla: AncillaQubit, new_ancilla: AncillaQubit, cluster: Cluster, new_cluster: Cluster
    ) -> bool:
        # Inherited docsting
        p_bound = (
            new_cluster is not None
            and new_cluster.instance == self.code.instance
            and new_cluster.on_bound
        )
        if cluster.on_bound and type(new_ancilla) == PseudoQubit:
            if self.config["dynamic_forest"]:
                self._edge_peel(edge, variant="cycle")
        elif new_cluster is None or new_cluster.instance != self.code.instance:
            if (
                self.config["print_steps"]
                and type(new_ancilla) == PseudoQubit
                and not cluster.on_bound
            ):
                print("{} ∪ boundary".format(cluster))
            new_ancilla.node = ancilla.node
            self.boundary_ancillas.append((ancilla, edge, new_ancilla))
            cluster.add_ancilla(new_ancilla)
            self.cluster_find_ancillas(cluster, new_ancilla)
        elif new_cluster is cluster:
            if self.config["dynamic_forest"]:
                self._edge_peel(edge, variant="cycle")
        elif cluster.on_bound and p_bound:
            if self.config["dynamic_forest"]:
                self._edge_peel(edge, variant="cycle")
            else:
                return True
        else:
            return True
        return False