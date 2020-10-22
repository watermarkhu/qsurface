from __future__ import annotations
from typing import List, Optional, Tuple
from ...codes.elements import AncillaQubit, Edge, PseudoQubit
from .elements import Cluster
from .._template import SimCode
from collections import defaultdict


class Toric(SimCode):
    """Union-Find decoder for the toric lattice.

    In this implementation, cluster properties are not stored at the root of the tree. Instead, ancillas are collected within `~.unionfind.elements.Cluster` objects. The root cluster element of an ancilla ``v`` can be found via ``v.cluster.``\ `~.unionfind.elements.Cluster.find` \``()``. And two ancillas ``v`` and ``u`` of different clusters are merged as below.

        >>> v.find()
        cl_v
        >>> cl_v.union(u.find())
        cl_v    # merged cluster

    Default values for the following parameters can be supplied via a *decoders.ini* file under the section of ``[unionfind]``.

    Parameters
    ----------

    weighted_growth : bool, optional
        Enables weighted growth via bucket growth. Default is true. See `grow_clusters`.
    weighted_union : bool, optional
        Enables weighted union, Default is true. See `union_bucket`.
    dynamic_forest : bool, optional
        Enables dynamically mainted forests. Default is true.
    degenerate_union : bool, optional
        Enables preference for union on ancillas with multiple connections to other clusters. Default is false.
    print_steps : bool, optional
        Prints additional decoding information. Default is false.

    Attributes
    ----------
    support : dict

        Dictionary of growth states of all edges in the code.

        =====   ========================
        value   state
        =====   ========================
        2       fully grown
        1       half grown
        0       none
        -1      removed by cycle or peel
        -2      added to matching
        =====   ========================

    buckets : `~collections.defaultdict`
        Ordered dictionary (by index) for bucket growth (implementation of weighted growth). See `grow_clusters`.
    bucket_max_filled : int
        The hightest occupied bucket. Allows for break from bucket loop.
    clusters : list
        List of all clusters at initialization.
    cluster_index : int
        Index value for cluster differentiation.
    """

    name = "Union-Find"
    short = "unionfind"
    cluster = Cluster

    compatibility_measurements = dict(
        PerfectMeasurements=True,
        FaultyMeasurements=False,
    )
    compatibility_errors = dict(
        pauli=True,
        erasure=False,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.config["step_growth"] = not (
            self.config["step_bucket"] or self.config["step_cluster"]
        )
        self.code.ancillaQubit.cluster = None
        self.code.ancillaQubit.peeled = None
        if not self.config["dynamic_forest"]:
            self.code.ancillaQubit.forest = None
            self.code.edge.forest = None

        self.support = {}
        for layer in self.code.data_qubits.values():
            for data_qubit in layer.values():
                for edge in data_qubit.edges.values():
                    self.support[edge] = 0
        if hasattr(self.code, "pseudo_edges"):
            for edge in self.code.pseudo_edges:
                self.support[edge] = 0

        if self.config["weighted_growth"]:
            self.buckets_num = self.code.size[0] * self.code.size[1] * self.code.layers * 2
        else:
            self.buckets_num = 2

        self.buckets = defaultdict(list)
        self.bucket_max_filled = 0
        self.clusters = []
        self.cluster_index = 0

    def reset(self):
        """Resets the decoder for a new iteration."""
        self.bucket_max_filled = 0
        self.cluster_index = 0
        self.clusters = []
        self.support = {edge: 0 for edge in self.support}

    def decode(self, reset=True, **kwargs):
        # Inherited docstrings
        self.find_clusters(**kwargs)
        self.grow_clusters(**kwargs)
        self.peel_clusters(**kwargs)

        if reset:
            self.reset()

    """
    ================================================================================================
                                    General helper functions
    ================================================================================================
    """

    def get_cluster(self, ancilla: AncillaQubit) -> Optional[Cluster]:
        """Returns the cluster to which ``ancilla`` belongs to.

        If ``ancilla`` has no cluster or the cluster is not from the current simulation, none is returned. Otherwise, the root element of the cluster-tree is found, updated to ``ancilla.cluster`` and returned.

        Parameters
        ----------
        ancilla
            The ancilla for which the cluster is to be found.
        """
        if not (ancilla.cluster is None or ancilla.cluster.instance != self.code.instance):
            ancilla.cluster = ancilla.cluster.find()
            return ancilla.cluster

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
                        cluster.add_ancilla(new_ancilla)
                        self._edge_full(ancilla, edge, new_ancilla)
                        self.cluster_find_ancillas(cluster, new_ancilla)
            else:  # Make sure new bound does not lead to self
                if new_ancilla.cluster is not cluster:
                    cluster.new_bound.append((ancilla, edge, new_ancilla))

    def _edge_peel(self, edge: Edge, variant: str = ""):
        """Peels or removes an edge"""
        self.support[edge] = -1
        if self.config["print_steps"]:
            print(f"del {edge} ({variant})")

    def _edge_grow(self, ancilla, edge, new_ancilla, **kwargs):
        """Grows the edge in support."""
        if self.support[edge] == 1:
            self._edge_full(ancilla, edge, new_ancilla, **kwargs)
        else:
            self.support[edge] += 1

    def _edge_full(self, ancilla, edge, new_ancilla, **kwargs):
        """Fully grows an edge."""
        self.support[edge] = 2
        
    """
    ================================================================================================
                                    1. Find clusters
    ================================================================================================
    """

    def find_clusters(self, **kwargs):
        """Initializes the clusters on the lattice.

        For every non-trivial ancilla on the lattice, a `~.unionfind.elements.Cluster` is initiated. If any set of ancillas are connected by some set of erased qubits, all connected ancillas are found by `cluster_find_ancillas` and a single cluster is initiated for the set.

        The cluster is then placed into a bucket based on its size and parity by `cluster_place_bucket`. See `grow_clusters` for more information on buckets.
        """
        plaqs, stars = self.get_syndrome()

        for ancilla in plaqs + stars:
            if ancilla.cluster is None or ancilla.cluster.instance != self.code.instance:
                cluster = self.cluster(self.cluster_index, self.code.instance)
                cluster.add_ancilla(ancilla)
                self.cluster_find_ancillas(cluster, ancilla)
                self.cluster_place_bucket(cluster, -1)
                self.cluster_index += 1
                self.clusters.append(cluster)

        if self.config["print_steps"]:
            print(f"Found clusters:\n" + ", ".join(map(str, self.clusters)) + "\n")

    """
    ================================================================================================
                                    2(a). Grow clusters expansion
    ================================================================================================
    """

    def grow_clusters(self, **kwargs):
        """Grows odd-parity clusters outward for union with others until all clusters are even.

        Lists of odd-parity clusters are maintained at ``self.buckets``. Starting from bucket 0, odd-parity clusters are popped from the bucket by '_grow_bucket and grown at the boundary by `_grow_boundary` by adding 1 for every boundary edge in ``cluster.bound`` in ``self.support``. Grown clusters are then placed in a new bucket by `cluster_place_bucket` based on its size if it has odd parity.

        Edges are fully added to the cluster per two growth iterations. Since a cluster with half-grown edges at the boundary has the same size (number of ancillas) as before growth, but is non-arguably *bigger*, the degeneracy in cluster size is differentiated by ``cluster.support``. When an union occurs between two clusters during growth, if the merged cluster is odd, it is placed in a new bucket. Thus the real bucket number is saved at the cluster locally as ``cluster.bucket``. These two checks are performed before a cluster is grown in `_grow_bucket`.

        The chronology of events per bucket must be the following:

        1.  Grow all clusters in the bucket if checks passed.

            *   Add all odd-parity clusters after growth to ``place_list``.
            *   Add all merging clusters to ``union_list``.

        2.  Merge all clusters in ``union_list``

            *   Add odd-parity clusters after union to ``place_list``.

        3.  Place all clusters in ``place_list`` in new bucket if parity is odd.

        For clusters with ``cluster.support==1`` or with half-grown edges at the boundary, the new boundary at ``clusters.new_bound`` consists of the same half-grown edges. For clusters with ``cluster.support==0``, the new boundary is found by ``cluster_find_ancillas``.

        If *weighted_growth* is disabled, odd-parity clusters are always placed in ``self.buckets[0]``. The same checks for ``cluster.bucket`` and ``cluster.support`` are applied to ensure clusters growth is valid.
        """
        if self.config["weighted_growth"]:
            for bucket_i in range(self.buckets_num):
                if bucket_i > self.bucket_max_filled:
                    break
                if bucket_i in self.buckets and self.buckets[bucket_i] != []:
                    union_list, place_list = self._grow_bucket(
                        self.buckets.pop(bucket_i), bucket_i
                    )
                    self.union_bucket(union_list)
                    self._place_bucket(place_list, bucket_i)
        else:
            bucket_i = 0
            while self.buckets[0]:
                union_list, place_list = self._grow_bucket(self.buckets.pop(0), bucket_i)
                self.union_bucket(union_list)
                self._place_bucket(place_list, bucket_i)
                bucket_i += 1

    def _grow_bucket(self, bucket: List[Cluster], bucket_i: int, **kwargs) -> Tuple[List, List]:
        """Grows the clusters which are contained in the current bucket.

        See `grow_clusters` for more information.

        Parameters
        ----------
        bucket
            List of clusters to be grown.
        bucket_i
            Current bucket number.

        Returns
        -------
        list
            List of clusters to be merged.
        list
            List of odd-parity clusters to be placed in new buckets.
        """
        if self.config["print_steps"]:
            string = f"Growing bucket {bucket_i} of clusters:"
            print("=" * len(string) + "\n" + string)

        union_list, place_list = [], []
        while bucket:  # Loop over all clusters in the current bucket\
            cluster = bucket.pop().find()
            if cluster.bucket == bucket_i and cluster.support == bucket_i % 2:
                place_list.append(cluster)
                self._grow_boundary(cluster, union_list)

        if self.config["print_steps"]:
            print("\n")

        return union_list, place_list

    def _grow_boundary(
        self, cluster: Cluster, union_list: List[Tuple[AncillaQubit, Edge, AncillaQubit]], **kwargs
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
        cluster.bound, cluster.new_bound = cluster.new_bound, []

        while cluster.bound:  # grow boundary
            boundary = cluster.bound.pop()
            new_edge = boundary[1]

            if self.support[new_edge] != 2:  # if not already fully grown
                self._edge_grow(*boundary)  # Grow boundaries by half-edge
                if self.support[new_edge] == 2:  # if edge is fully grown
                    union_list.append(boundary)  # Append to union_list list of edges
                else:
                    cluster.new_bound.append(boundary)

        if self.config["print_steps"]:
            print(f"{cluster}, ", end="")

    """
    ================================================================================================
                                    2(b). Grow clusters union
    ================================================================================================
    """

    def union_bucket(self, union_list: List[Tuple[AncillaQubit, Edge, AncillaQubit]], **kwargs):
        """Merges clusters in ``union_list`` if checks are passed.

        Items in ``union_list`` consists of ``[ancillaA, edge, ancillaB]`` of two ancillas that, at the time added to the list, were not part of the same cluster. The cluster of an ancilla is stored at ``ancilla.cluster``, but due to cluster mergers the cluster at ``ancilla_cluster`` may not be the root element in the cluster-tree, and thus the cluster must be requested by ``ancilla.cluster.``\ `~.unionfind.elements.Cluster.find`. Since the clusters of ``ancillaA`` and ``ancillaB`` may have already merged, checks are performed in `_union_check` after which the clusters are conditionally merged on ``edge`` by `_union_edge`.

        If ``weighted_union`` is enabled, the smaller cluster is always made a child of the bigger cluster in the cluster-tree. This ensures the that the depth of the tree is minimized and the future calls to `~.unionfind.elements.Cluster.find` is reduced.

        If ``degenerate_union`` is enabled, cluster mergers are prioritized on ancillas with a high connectivity to other clusters. A higher connectivity of two ancillas points to an increased chance of the union occuring on the edge spanned by these ancillas.

        If ``dynamic_forest`` is disabled, cycles within clusters are not immediately removed. The acyclic forest is then later constructed before peeling in `peel_leaf`.

        Parameters
        ----------
        union_list
            List of boundaries that exists between two clusters.
        """
        if union_list and self.config["print_steps"]:
            print("Fusing clusters")

        if self.config["degenerate_union"]:
            merging, count = [], defaultdict(int)

            for ancilla, edge, new_ancilla in union_list:
                cluster = self.get_cluster(ancilla)
                new_cluster = self.get_cluster(new_ancilla)
                if self._union_check(edge, new_ancilla, cluster, new_cluster):
                    merging.append((edge, ancilla, new_ancilla))

            for edge, ancilla, new_ancilla in merging:
                count[ancilla] += 1
                count[new_ancilla] += 1

            merge_buckets = [[] for i in range(6)]
            for merge_ancillas in merging:
                edge, ancilla, new_ancilla = merge_ancillas
                index = 7 - (count[ancilla] + count[new_ancilla])
                merge_buckets[index].append(merge_ancillas)

            for merge_bucket in merge_buckets:
                for items in merge_bucket:
                    self._union_edge(*items)
        else:
            for ancilla, edge, new_ancilla in union_list:
                self._union_edge(edge, ancilla, new_ancilla)

        if union_list and self.config["print_steps"]:
            print("")

    def _union_edge(
        self, edge: Edge, ancilla: AncillaQubit, new_ancilla: AncillaQubit, *args, **kwargs
    ):
        """Merges the clusters of ``ancilla`` and ``new_ancilla`` on ``edge.

        Weighted union is conditionally applied. See `union_bucket` for more information.
        """
        cluster = self.get_cluster(ancilla)
        new_cluster = self.get_cluster(new_ancilla)

        if self._union_check(edge, new_ancilla, cluster, new_cluster):
            string = "{}∪{}=".format(cluster, new_cluster) if self.config["print_steps"] else ""

            if self.config["weighted_union"] and cluster.size < new_cluster.size:
                cluster, new_cluster = new_cluster, cluster
            cluster.union(new_cluster)
            if string:
                print(string, cluster)

    def _union_check(
        self, edge: Edge, new_ancilla: AncillaQubit, cluster: Cluster, new_cluster: Cluster
    ) -> bool:
        """Checks whether ``cluster`` and ``new_cluster`` can be joined on ``edge``.

        See `union_bucket` for more information.
        """
        if new_cluster is None or new_cluster.instance != self.code.instance:
            cluster.add_ancilla(new_ancilla)
            self.cluster_find_ancillas(cluster, new_ancilla)
        elif new_cluster is cluster:
            if self.config["dynamic_forest"]:
                self._edge_peel(edge, variant="cycle")
        else:
            return True
        return False

    """
    ================================================================================================
                                    2(c). Place clusters in buckets
    ================================================================================================
    """

    def _place_bucket(self, place_list: List[Cluster], bucket_i: int):
        """Places all clusters in ``place_list`` with `cluster_place_bucket`."""
        for cluster in place_list:
            self.cluster_place_bucket(cluster.find(), bucket_i)

    def cluster_place_bucket(self, cluster: Cluster, bucket_i: int, **kwargs):
        """Places a ``cluster`` in a bucket if parity is odd.

        If ``weighted_growth`` is enabled. the cluster is placed in a new bucket based on its size, otherwise it is placed in ``self.buckets[0]``

        Parameters
        ----------
        cluster
            Cluster object to place.
        bucket_i
            Current bucket number.
        """

        if (cluster.parity % 2 == 1 and not cluster.on_bound) or (
            cluster.parity % 2 == 0 and cluster.on_bound
        ):
            if self.config["weighted_growth"]:
                cluster.bucket = 2 * (cluster.size - 1) + cluster.support
                self.buckets[cluster.bucket].append(cluster)
                if cluster.bucket > self.bucket_max_filled:
                    self.bucket_max_filled = cluster.bucket
            else:
                self.buckets[0].append(cluster)
                cluster.bucket = bucket_i + 1
        else:
            cluster.bucket = None

    """
    ================================================================================================
                                    3. Peel clusters
    ================================================================================================
    """

    def peel_clusters(self, *args, **kwargs):
        """Loops over all clusters to find pendant ancillas to peel.

        To make sure that all cluster-trees are fully peeled, all ancillas are considered in the loop. If the ancilla has not been peeled before and belongs to a cluster of the current simulation, the ancilla is considered for peeling by `peel_leaf`.
        """
        if self.config["print_steps"]:
            print("================\nPeeling clusters")
        for layer in self.code.ancilla_qubits.values():
            for ancilla in layer.values():
                if (
                    ancilla.peeled != self.code.instance
                    and ancilla.cluster
                    and ancilla.cluster.instance == self.code.instance
                ):
                    cluster = self.get_cluster(ancilla)
                    self.peel_leaf(cluster, ancilla)

    def peel_leaf(self, cluster: Cluster, ancilla: AncillaQubit, *args, **kwargs):
        """Recursive function which peels a branch of the tree if the input ancilla is a pendant ancilla

        If there is only one neighbor of the input ancilla that is in the same cluster, this ancilla is a pendant ancilla and can be peeled. The function calls itself on the other ancilla of the edge leaf.

        If ["dynamic_forest"] is disabled, once a pendant leaf is found, the acyclic forest is constructed by `static_forest`.

        Parameters
        ----------
        cluster
            Current cluster being peeled.
        ancilla
            Pendant ancilla of the edge to be peeled.
        """
        num_connect = 0
        connect_key = None

        for key in ancilla.parity_qubits:
            (new_ancilla, edge) = self.get_neighbor(ancilla, key)
            if self.support[edge] == 2:
                new_cluster = self.get_cluster(new_ancilla)
                if new_cluster is cluster:
                    num_connect += 1
                    connect_key = key
            if num_connect > 1:
                break
        else:
            if num_connect == 1:
                if not self.config["dynamic_forest"]:
                    self.static_forest(ancilla)
                (new_ancilla, edge) = self.get_neighbor(ancilla, connect_key)
                if ancilla.measured_state:
                    self._flip_edge(ancilla, edge, new_ancilla)
                    self.correct_edge(ancilla, connect_key)
                else:
                    self._edge_peel(edge, variant="peel")
                ancilla.peeled = self.code.instance
                self.peel_leaf(cluster, new_ancilla)

    def _flip_edge(self, ancilla: AncillaQubit, edge: Edge, new_ancilla: AncillaQubit, **kwargs):
        """Flips the values of the ancillas connected to ``edge``."""
        ancilla.measured_state = not ancilla.measured_state
        new_ancilla.measured_state = not new_ancilla.measured_state
        self.support[edge] = -2
        if self.config["print_steps"]:
            print(f"{edge} to matching")

    def static_forest(self, ancilla: AncillaQubit):
        """Constructs an acyclic forest in the cluster of ``ancilla``.

        Applies recursively to all neighbors of ``ancilla``. If a cycle is detected, edges are removed from the cluster.

        Parameters
        ----------
        ancilla
        """
        ancilla.forest = self.code.instance
        for key in ancilla.parity_qubits:
            (new_ancilla, edge) = self.get_neighbor(ancilla, key)
            if self.support[edge] == 2:
                if new_ancilla.forest == self.code.instance:
                    if edge.forest != self.code.instance:
                        self._edge_peel(edge, variant="cycle")
                else:
                    edge.forest = self.code.instance
                    self.static_forest(new_ancilla)


class Planar(Toric):
    """Union-Find decoder for the planar lattice.
    
    See the description of `.unionfind.sim.Toric`. 
    """

    def _union_check(
        self, edge: Edge, new_ancilla: AncillaQubit, cluster: Cluster, new_cluster: Cluster
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

    def static_forest(self, ancilla: AncillaQubit, found_bound: str = False, **kwargs) -> bool:
        # Inherited docsting
        if not found_bound and ancilla.cluster.find().parity % 2 == 0:
            found_bound = True

        ancilla.forest = self.code.instance
        for key in ancilla.parity_qubits:
            (new_ancilla, edge) = self.get_neighbor(ancilla, key)

            if self.support[edge] == 2:

                if type(new_ancilla) is PseudoQubit:
                    if found_bound:
                        self._edge_peel(edge, variant="cycle")
                    else:
                        edge.forest = self.code.instance
                        found_bound = True
                    continue

                if new_ancilla.forest == self.code.instance:
                    if edge.forest != self.code.instance:
                        self._edge_peel(edge, variant="cycle")
                else:
                    edge.forest = self.code.instance
                    found_bound = self.static_forest(new_ancilla, found_bound=found_bound)
        return found_bound