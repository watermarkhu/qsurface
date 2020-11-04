from typing import List, Tuple
from opensurfacesim.codes.elements import AncillaQubit
from .._template import Sim
import networkx as nx
from numpy.ctypeslib import ndpointer
import ctypes
import os


LA = List[AncillaQubit]


class Toric(Sim):
    """Minimum-Weight Perfect Matching decoder for the toric lattice.
    
    Parameters
    ----------
    args, kwargs
        Positional and keyword arguments are passed on to `.decoders._template.Sim`. 
    """

    name = "Minimum-Weight Perfect Matching"
    short = "mwpm"

    compatibility_measurements = dict(
        PerfectMeasurements=True,
        FaultyMeasurements=False,
    )
    compatibility_errors = dict(
        pauli=True,
        erasure=True,
    )

    def decode(self, **kwargs):
        # Inherited docstring
        plaqs, stars = self.get_syndrome()
        self.correct_matching(plaqs, self.match_syndromes(plaqs, **kwargs))
        self.correct_matching(stars, self.match_syndromes(stars, **kwargs))

    def match_syndromes(self, syndromes: LA, use_blossomv: bool = False, **kwargs) -> list:
        """Decodes a list of syndromes of the same type.

        A graph is constructed with the syndromes in ``syndromes`` as nodes and the distances between each of the syndromes as the edges. The distances are dependent on the boundary conditions of the code and is calculated by `get_qubit_distances`. A minimum-weight matching is then found by either `match_networkx` or `match_blossomv`.

        Parameters
        ----------
        syndromes
            Syndromes of the code.
        use_blossomv
            Use external C++ Blossom V library for minimum-weight matching. Needs to be downloaded and compiled by calling `.get_blossomv`.

        Returns
        -------
        list of `~.codes.elements.AncillaQubit`
            Minimum-weight matched ancilla-qubits.

        """
        matching_graph = self.match_blossomv if use_blossomv else self.match_networkx
        edges = self.get_qubit_distances(syndromes, self.code.size)
        matching = matching_graph(
            edges,
            maxcardinality=self.config["max_cardinality"],
            num_nodes=len(syndromes),
            **kwargs,
        )
        return matching

    def correct_matching(self, syndromes: LA, matching: list, **kwargs):
        """Applies the matchings as a correction to the code."""
        weight = 0
        for i0, i1 in matching:
            weight += self._correct_matched_qubits(syndromes[i0], syndromes[i1])
        return weight

    @staticmethod
    def match_networkx(edges: list, maxcardinality: float, **kwargs) -> list:
        """Finds the minimum-weight matching of a list of ``edges`` using `networkx.algorithms.matching.max_weight_matching`.

        Parameters
        ----------
        edges :  [[nodeA, nodeB, distance(nodeA,nodeB)],...]
            A graph defined by a list of edges.
        maxcardinality
            See `networkx.algorithms.matching.max_weight_matching`.

        Returns
        -------
        list
            Minimum weight matching in the form of [[nodeA, nodeB],..].
        """
        nxgraph = nx.Graph()
        for i0, i1, weight in edges:
            nxgraph.add_edge(i0, i1, weight=-weight)
        return nx.algorithms.matching.max_weight_matching(nxgraph, maxcardinality=maxcardinality)

    @staticmethod
    def match_blossomv(edges: list, num_nodes: float = 0, **kwargs) -> list:
        """Finds the minimum-weight matching of a list of ``edges`` using `Blossom V <https://pub.ist.ac.at/~vnk/software.html>`_.

        Parameters
        ----------
        edges : [[nodeA, nodeB, distance(nodeA,nodeB)],...]
            A graph defined by a list of edges.

        Returns
        -------
        list
            Minimum weight matching in the form of [[nodeA, nodeB],..].
        """

        if num_nodes == 0:
            return []
        try:
            folder = os.path.dirname(os.path.abspath(__file__))
            PMlib = ctypes.CDLL(folder + "/blossom5-v2.05.src/PMlib.so")
        except:
            raise FileNotFoundError("Blossom5 library not found. See docs.")

        PMlib.pyMatching.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        PMlib.pyMatching.restype = ndpointer(dtype=ctypes.c_int, shape=(num_nodes,))

        # initialize ctypes array and fill with edge data
        numEdges = len(edges)
        nodes1 = (ctypes.c_int * numEdges)()
        nodes2 = (ctypes.c_int * numEdges)()
        weights = (ctypes.c_int * numEdges)()

        for i in range(numEdges):
            nodes1[i] = edges[i][0]
            nodes2[i] = edges[i][1]
            weights[i] = edges[i][2]

        matching = PMlib.pyMatching(ctypes.c_int(num_nodes), ctypes.c_int(numEdges), nodes1, nodes2, weights)
        return [[i0, i1] for i0, i1 in enumerate(matching) if i0 > i1]

    @staticmethod
    def get_qubit_distances(qubits: LA, size: Tuple[float, float]):
        """Computes the distance between a list of qubits.

        On a toric lattice, the shortest distance between two qubits may be one in four directions due to the periodic boundary conditions. The ``size`` parameters indicates the length in both x and y directions to find the shortest distance in all directions.
        """
        edges = []
        for i0, q0 in enumerate(qubits[:-1]):
            (x0, y0), z0 = q0.loc, q0.z
            for i1, q1 in enumerate(qubits[i0 + 1 :]):
                (x1, y1), z1 = q1.loc, q1.z
                wx = int(x0 - x1) % (size[0])
                wy = int(y0 - y1) % (size[1])
                wz = int(abs(z0 - z1))
                weight = min([wy, size[1] - wy]) + min([wx, size[0] - wx]) + wz
                edges.append([i0, i1 + i0 + 1, weight])
        return edges

    def _correct_matched_qubits(self, aq0: AncillaQubit, aq1: AncillaQubit) -> float:
        """Flips the values of edges between two matched qubits by doing a walk in between."""
        ancillas = self.code.ancilla_qubits[self.code.decode_layer]
        pseudos = self.code.pseudo_qubits[self.code.decode_layer]
        dq0 = ancillas[aq0.loc] if aq0.loc in ancillas else pseudos[aq0.loc]
        dq1 = ancillas[aq1.loc] if aq1.loc in ancillas else pseudos[aq1.loc]
        dx, dy, xd, yd = self._walk_direction(aq0, aq1, self.code.size)
        xv = self._walk_and_correct(dq0, dy, yd)
        self._walk_and_correct(dq1, dx, xd)
        return dy + dx + abs(aq0.z - aq1.z)

    @staticmethod
    def _walk_direction(q0: AncillaQubit, q1: AncillaQubit, size: Tuple[float, float]):
        """Finds the closest walking distance and direction."""
        (x0, y0) = q0.loc
        (x1, y1) = q1.loc
        dx0 = int(x0 - x1) % size[0]
        dx1 = int(x1 - x0) % size[0]
        dy0 = int(y0 - y1) % size[1]
        dy1 = int(y1 - y0) % size[1]
        dx, xd = (dx0, (0.5, 0)) if dx0 < dx1 else (dx1, (-0.5, 0))
        dy, yd = (dy0, (0, -0.5)) if dy0 < dy1 else (dy1, (0, 0.5))
        return dx, dy, xd, yd

    def _walk_and_correct(self, qubit: AncillaQubit, length: float, key: str):
        """Corrects the state of a qubit as it traversed during a walk."""
        for _ in range(length):
            try:
                qubit = self.correct_edge(qubit, key)
            except:
                break
        return qubit


class Planar(Toric):
    """Minimum-Weight Perfect Matching decoder for the planar lattice.

    Additionally to all edges, virtual qubits are added to the boundary, which connect to their main qubits.Edges between all virtual qubits are added with weight zero.
    """

    def decode(self, **kwargs):
        # Inherited docstring
        plaqs, stars = self.get_syndrome(find_pseudo=True)
        self.correct_matching(plaqs, self.match_syndromes(plaqs, **kwargs))
        self.correct_matching(stars, self.match_syndromes(stars, **kwargs))

    def correct_matching(self, syndromes: List[Tuple[AncillaQubit, AncillaQubit]], matching: list):
        # Inherited docstring
        weight = 0
        for i0, i1 in matching:
            if i0 < len(syndromes) or i1 < len(syndromes):
                aq0 = syndromes[i0][0] if i0 < len(syndromes) else syndromes[i0 - len(syndromes)][1]
                aq1 = syndromes[i1][0] if i1 < len(syndromes) else syndromes[i1 - len(syndromes)][1]
                weight += self._correct_matched_qubits(aq0, aq1)
        return weight

    @staticmethod
    def get_qubit_distances(qubits, *args):
        """Computes the distance between a list of qubits.

        On a planar lattice, any qubit can be paired with the boundary, which is inhabited by `~.codes.elements.PseudoQubit` objects. The graph of syndromes that supports minimum-weight matching algorithms must be fully connected, with each syndrome connecting additionally to its boundary pseudo-qubit, and a fully connected graph between all pseudo-qubits with weight 0.
        """
        edges = []

        # Add edges between all ancilla-qubits
        for i0, (a0, _) in enumerate(qubits):
            (x0, y0), z0 = a0.loc, a0.z
            for i1, (a1, _) in enumerate(qubits[i0 + 1 :], start=i0 + 1):
                (x1, y1), z1 = a1.loc, a1.z
                wx = int(abs(x0 - x1))
                wy = int(abs(y0 - y1))
                wz = int(abs(z0 - z1))
                weight = wy + wx + wz
                edges.append([i0, i1, weight])

        # Add edges between ancilla-qubits and their boundary pseudo-qubits
        for i, (ancilla, pseudo) in enumerate(qubits):
            (xs, ys) = ancilla.loc
            (xb, yb) = pseudo.loc
            weight = xb - xs if ancilla.state_type == "x" else yb - ys
            edges.append([i, len(qubits) + i, int(abs(weight))])

        # Add edges of weight 0 between all pseudo-qubits
        for i0 in range(len(qubits), len(qubits)):
            for i1 in range(i0 + 1, len(qubits) - 1):
                edges.append([i0, i1, 0])
        return edges

    @staticmethod
    def _walk_direction(q0, q1, *args):
        # Inherited docsting
        (x0, y0), (x1, y1) = q0.loc, q1.loc
        dx, dy = int(x0 - x1), int(y0 - y1)
        xd = (0.5, 0) if dx > 0 else (-0.5, 0)
        yd = (0, -0.5) if dy > 0 else (0, 0.5)
        return abs(dx), abs(dy), xd, yd
