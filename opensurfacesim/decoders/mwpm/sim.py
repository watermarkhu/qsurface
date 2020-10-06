import ctypes
from opensurfacesim.codes._template.elements import AncillaQubit
import networkx as nx
from .._template.sim import Code as DecoderTemplate
from numpy.ctypeslib import ndpointer
import os


class Toric(DecoderTemplate):
    """
    MWPM decoder for the toric lattice (2D and 3D).
    Edges between all qubits are considered.
    """

    name = ("Minimum-Weight Perfect Matching",)

    compatibility_measurements = dict(
        PerfectMeasurements=True,
        FaultyMeasurements=False,
    )
    compatibility_errors = dict(
        pauli=True,
        erasure=True,
    )

    def do_decode(self, **kwargs):
        """
        Decode functions for the MWPM toric decoder
        Returns all qubits in the graph, as well ans their respective qubits on the decode layer.
        This is the same for a 2D graph, but the most recent layer in the 3D case
        """
        plaqs, dplaqs, stars, dstars = [], [], [], []
        dlayer, ancillas = self.code.decode_layer, self.code.ancilla_qubits
        for layer in ancillas.values():
            for ancilla in layer.values():
                if ancilla.state:
                    if ancilla.state_type == "x":
                        plaqs.append(ancilla)
                        dplaqs.append(ancillas[dlayer][ancilla.loc])
                    else:
                        plaqs.append(ancilla)
                        dstars.append(ancillas[dlayer][ancilla.loc])
        self.decode_group(plaqs, dplaqs, **kwargs)
        self.decode_group(stars, dstars, **kwargs)

    def decode_group(self, layer_ancillas, decode_ancillas, use_blossom5=False, **kwargs):

        matching_graph = self.matching_blossom5 if use_blossom5 else self.matching_networkx
        edges = self.get_qubit_distances(layer_ancillas, self.code.size)
        output = matching_graph(
            edges,
            num_nodes=len(layer_ancillas),
            maxcardinality=self.mwpm_max_cardinality,
            **kwargs,
        )
        layer_matchings = [[layer_ancillas[i0], layer_ancillas[i1]] for i0, i1 in output]
        decode_matchings = [[decode_ancillas[i0], decode_ancillas[i1]] for i0, i1 in output]
        self.apply_matching(layer_matchings, decode_matchings, self.code.size)

    @staticmethod
    def matching_networkx(edges, num_nodes, **kwargs):
        nxgraph = nx.Graph()
        for i0, i1, weight in edges:
            nxgraph.add_edge(i0, i1, weight=-weight)
        return nx.algorithms.matching.max_weight_matching(nxgraph, **kwargs)

    @staticmethod
    def matching_blossom5(edges, num_nodes, **kwargs):
        if num_nodes == 0:
            return []
        try:
            folder = os.path.dirname(os.path.abspath(__file__))
            PMlib = ctypes.CDLL(folder + "/blossom5-v2.05.src/PMlib.so")
        except:
            raise FileExistsError(
                "Blossom5 library not found. Prepare library with 'get_blossom5.py'."
            )

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

        matching = PMlib.pyMatching(
            ctypes.c_int(num_nodes), ctypes.c_int(numEdges), nodes1, nodes2, weights
        )
        return [[i0, i1] for i0, i1 in enumerate(matching) if i0 > i1]

    @staticmethod
    def get_qubit_distances(qubits, size):
        """
        Computes all edges and their respective weights between all all nodes that are inputted.
        Periodic boundary conditions are applied in x and y directions.
        """
        edges = []
        for i0, q0 in enumerate(qubits[:-1]):
            (x0, y0), z0 = q0.loc, q0.z
            for i1, q1 in enumerate(qubits[i0 + 1 :]):
                (x1, y1), z1 = q1.loc, q1.z
                wx = (x0 - x1) % (size[0])
                wy = (y0 - y1) % (size[1])
                wz = abs(z0 - z1)
                weight = min([wy, size[1] - wy]) + min([wx, size[0] - wx]) + wz
                edges.append([i0, i1 + i0 + 1, weight])
        return edges


    def apply_matching(self, layered_matchings, decode_matchings, size):
        """
        Applies the matchings returned from the MWPM algorithm by doing a walk between nodes of the matching
        """
        weight = 0
        for (lm0, lm1), (dm0, dm1) in zip(layered_matchings, decode_matchings):
            dx, dy, xd, yd = self.walk_direction(lm0, lm1, size)
            xv = self.walk_and_flip(dm0, dy, yd)
            self.walk_and_flip(dm1, dx, xd)
            weight += dy + dx + abs(lm0.z - lm1.z)
        return weight
    
    @staticmethod
    def walk_direction(q0, q1, size):
        (x0, y0) = q0.loc
        (x1, y1) = q1.loc
        dx0 = int(x0 - x1) % size[0]
        dx1 = int(x1 - x0) % size[0]
        dy0 = int(y0 - y1) % size[1]
        dy1 = int(y1 - y0) % size[1]
        dx, xd = (dx0, "e") if dx0 < dx1 else (dx1, "w")
        dy, yd = (dy0, "s") if dy0 < dy1 else (dy1, "n")
        return dx, dy, xd, yd


    def walk_and_flip(self, flipnode, length, key):
        for _ in range(length):
            try: 
                (flipnode, flipedge) = self.get_neighbor(flipnode, key)
            except:
                break
            flipedge.state = 1 - flipedge.state
        return flipnode


class Planar(Toric):
    """
    Decodes the planar lattice (2D and 3D).
    Edges between all qubits are considered.
    Additionally, virtual qubits are added to the boundary, which connect to their main qubits.
    Edges between all virtual qubits are added with weight zero.
    """
    def do_decode(self, **kwargs):
        """
        Returns all qubits in the graph, as well as their respective virtual qubits in the boundary, for both their current layer as well as on the decode layer.
        This is the same for a 2D graph, but the most recent layer in the 3D case
        """
        stars, plaqs, pstars, pplaqs = [], [], [], []
        dstar, dplaq, dpstar, dpplaq = [], [], [], []
        dlayer, size = self.code.decode_layer, self.code.size
        ancillas, pseudos = self.code.ancilla_qubits, self.code.pseudo_qubits

        for layer in ancillas.values():
            for ancilla in layer.values():
                if ancilla.state:
                    if ancilla.state_type == "x":
                        plaqs.append(ancilla)
                        dplaq.append(ancillas[dlayer][ancilla.loc])
                        if ancilla.loc[0] < size[0] / 2:
                            loc = (0, ancilla.loc[1])
                            pplaqs.append(pseudos[ancilla.z][loc])
                            dpplaq.append(pseudos[dlayer][loc])
                        else:
                            loc = (size[0], ancilla.loc[1])
                            pplaqs.append(pseudos[ancilla.z][loc])
                            dpplaq.append(pseudos[dlayer][loc])

                    else:
                        stars.append(ancilla)
                        dstar.append(ancillas[dlayer][ancilla.loc])
                        if ancilla.loc[1] < self.code.size[1] / 2:
                            loc = (ancilla.loc[0], -0.5)
                            pstars.append(pseudos[ancilla.z][loc])
                            dpstar.append(pseudos[dlayer][loc])
                        else:
                            loc = (ancilla.loc[0], size[1] - 0.5)
                            pstars.append(pseudos[ancilla.z][loc])
                            dpstar.append(pseudos[dlayer][loc])

        stars += pstars
        plaqs += pplaqs
        dstar += dpstar
        dplaq += dpplaq
        self.decode_group(plaqs, dplaq, **kwargs)
        self.decode_group(stars, dstar, **kwargs)

    @staticmethod
    def get_qubit_distances(qubits, *args):
        """
        Computes all edges and their respective weights between all all qubits that are inputted, between all virtual qubits and between qubits and virtual qubits.
        """
        edges = []
        mid = len(qubits) // 2

        # Add edges between all qubits
        for i0, q0 in enumerate(qubits[: mid - 1]):
            (x0, y0), z0 = q0.loc, q0.z
            for i1, q1 in enumerate(qubits[i0 + 1 : mid]):
                (x1, y1), z1 = q1.loc, q1.z
                wx = abs(x0 - x1)
                wy = abs(y0 - y1)
                wz = abs(z0 - z1)
                weight = wy + wx + wz
                edges.append([i0, i1 + i0 + 1, weight])

        # Add edges of weight 0 between all virtual qubits
        for i0, q0 in enumerate(qubits[mid:-1], start=mid):
            for i1, q1 in enumerate(qubits[i0 + 1 :], start=i0 + 1):
                edges.append([i0, i1, 0])

        # Add edges between virtual qubits and real qubits
        for i in range(mid):
            (xs, ys) = qubits[i].loc
            (xb, yb) = qubits[mid + i].loc
            weight = abs(xb - xs) if qubits[i].state_type == "x" else abs(yb - ys)
            edges.append([i, mid + i, weight])
        return edges

    def apply_matching(self, layered_matchings, decode_matchings, size):
        ancilla_layer, ancilla_decode = [], []
        for (lm0, lm1), decode in zip(layered_matchings, decode_matchings):
            if not (type(lm0) != AncillaQubit and type(lm1) != AncillaQubit):
                ancilla_layer.append((lm0, lm1))
                ancilla_decode.append(decode)
        super().apply_matching(ancilla_layer, ancilla_decode, size)

    @staticmethod
    def walk_direction(q0, q1, *args):
        """
        Computes the distance or number of walks and direction between inputted nodes in x and y directions
        """
        (x0, y0), (x1, y1) = q0.loc, q1.loc
        dx, dy = x0 - x1, y0 - y1
        yd = "s" if dy > 0 else "n"
        xd = "e" if dx > 0 else "w"
        return abs(dx), abs(dy), xd, yd
