'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

The Minimum Weight Perfect Matching decoder

Uses networkx implementation of the Blossom algorithm in python
'''

import networkx as nx
from ...info.benchmark import timeit
from .._template.sim import Code as DecoderTemplate


class Toric(DecoderTemplate):
    '''
    MWPM decoder for the toric lattice (2D and 3D).
    Edges between all anyons are considered.
    '''
    name = "Minimum-Weight Perfect Matching (networkx)",

    compatibility_measurements = dict(
        PerfectMeasurements = True,
        FaultyMeasurements = False,
    )
    compatibility_errors =  dict(
        pauli=True,
        erasure=True,
    )

    @timeit()
    def decode(self):
        '''
        Decode functions for the MWPM toric decoder
        '''
        self.get_matchings()
        self.apply_matching()


    def get_matchings(self):       
        '''
        Returns all anyons in the graph, as well ans their respective anyons on the decode layer.
        This is the same for a 2D graph, but the most recent layer in the 3D case
        '''
        self.matching = []
        plaqs, decode_plaqs, stars, decode_stars = [], [], [], []
        for layer in self.code.ancilla_qubits.values():
            for ancilla in layer.values():
                if ancilla.state:
                    if ancilla.state_type == "x":
                        plaqs.append(ancilla)
                        decode_plaqs.append(
                            self.code.ancilla_qubits[self.code.decode_layer][ancilla.loc])
                    else:
                        plaqs.append(ancilla)
                        decode_plaqs.append(
                            self.code.ancilla_qubits[self.code.decode_layer][ancilla.loc])
        if plaqs:
            self.matching += self.get_matching(plaqs, decode_plaqs)        
        if stars:
            self.matching += self.get_matching(stars, decode_stars)


    def get_matching(self, anyons, d_anyons):
        nxgraph = nx.Graph()
        edges = self.get_edges(anyons)
        for i0, i1, weight in edges:
            nxgraph.add_edge(i0, i1, weight=-weight)
        output = nx.algorithms.matching.max_weight_matching(nxgraph, maxcardinality=self.mwpm_max_cardinality)
        return [[d_anyons[i0], d_anyons[i1], anyons[i0], anyons[i1]] for i0, i1 in output]

    def get_edges(self, anyons):
        '''
        Computes all edges and their respective weights between all all nodes that are inputted.
        Periodic boundary conditions are applied in x and y directions.
        '''
        edges = []
        for i0, v0 in enumerate(anyons[:-1]):
            (x0, y0), z0 = v0.loc, v0.z
            for i1, v1 in enumerate(anyons[i0 + 1:]):
                (x1, y1), z1 = v1.loc, v1.z
                wy = (y0 - y1) % (self.code.size)
                wx = (x0 - x1) % (self.code.size)
                wz = abs(z0 - z1)
                weight = min([wy, self.code.size - wy]) + \
                    min([wx, self.code.size - wx]) + wz
                edges.append([i0, i1 + i0 + 1, weight])
        return edges


    def apply_matching(self):
        '''
        Applies the matchings returned from the MWPM algorithm by doing a walk between nodes of the matching
        '''
        for v0, v1, m0, m1 in self.matching:
            (x0, y0) = v0.loc
            (x1, y1) = v1.loc
            dy0 = (y0 - y1) % self.code.size
            dx0 = (x0 - x1) % self.code.size
            dy1 = (y1 - y0) % self.code.size
            dx1 = (x1 - x0) % self.code.size
            dy, yd = (dy0, "n") if dy0 < dy1 else (dy1, "s")
            dx, xd = (dx0, "e") if dx0 < dx1 else (dx1, "w")
            xv = self.walk_and_flip(v0, m0, dy, yd)
            self.walk_and_flip(v1, m1, dx, xd)


    def walk_and_flip(self, flipnode, matchnode, length, key):
        '''
        adds this edge to the matching.
        '''
        for _ in range(length):
            (flipnode, flipedge) = self.get_neighbor(flipnode, key)
            (matchnode, _) = self.get_neighbor(matchnode, key)
            flipedge.state = 1 - flipedge.state
        return flipnode



# class Planar(Toric):
#     '''
#     Decodes the planar lattice (2D and 3D).
#     Edges between all anyons are considered.
#     Additionally, virtual anyons are added to the boundary, which connect to their main anyons.
#     Edges between all virtual anyons are added with weight zero.
#     '''

#     def decode(self):
#         '''
#         Decode functions for the MWPM planar decoder
#         '''
#         self.get_matchings()
#         self.remove_virtual()
#         self.apply_matching()
#         if self.code.gl_plot:
#             self.code.gl_plot.plot_lines(self.matching)


#     def get_stabs(self):
#         '''
#         Returns all anyons in the graph, as well as their respective virtual anyons in the boundary, for both their current layer as well as on the decode layer.
#         This is the same for a 2D graph, but the most recent layer in the 3D case
#         '''
#         verts, plaqs, tv, tp = [], [], [], []
#         dvert, dplaq, dv, dp = [], [], [], []
#         for layer in self.code.S.values():
#             for stab in layer.values():
#                 (type, y, x) = stab.sID
#                 if stab.state:
#                     if type == 0:
#                         verts.append(stab)
#                         dvert.append(
#                             self.code.S[self.code.decode_layer][(type, y, x)])

#                         if x < self.code.size/2:
#                             tv.append(self.code.B[stab.z][(type, y, 0)])
#                             dv.append(
#                                 self.code.B[self.code.decode_layer][(type, y, 0)])
#                         else:
#                             tv.append(self.code.B[stab.z]
#                                       [(type, y, self.code.size)])
#                             dv.append(self.code.B[self.code.decode_layer][(
#                                 type, y, self.code.size)])
#                     else:
#                         plaqs.append(stab)
#                         dplaq.append(
#                             self.code.S[self.code.decode_layer][(type, y, x)])
#                         if y < self.code.size/2:
#                             tp.append(self.code.B[stab.z][(type, -1, x)])
#                             dp.append(
#                                 self.code.B[self.code.decode_layer][(type, -1, x)])
#                         else:
#                             tp.append(self.code.B[stab.z][(
#                                 type, self.code.size - 1, x)])
#                             dp.append(self.code.B[self.code.decode_layer][(
#                                 type, self.code.size - 1, x)])
#         verts += tv
#         plaqs += tp
#         dvert += dv
#         dplaq += dp
#         return verts, plaqs, dvert, dplaq


#     def get_edges(self, anyons):
#         '''
#         Computes all edges and their respective weights between all all anyons that are inputted, between all virtual anyons and between anyons and virtual anyons.
#         '''

#         edges = []
#         mid = len(anyons)//2

#         # Add edges between all anyons
#         for i0, v0 in enumerate(anyons[:mid-1]):
#             (y0, x0), z0 = v0.sID[1:], v0.z
#             for i1, v1 in enumerate(anyons[i0 + 1:mid]):
#                 (y1, x1), z1 = v1.sID[1:], v1.z
#                 wy = abs(y0 - y1)
#                 wx = abs(x0 - x1)
#                 wz = abs(z0 - z1)
#                 weight = wy + wx + wz
#                 edges.append([i0, i1 + i0 + 1, weight])

#         # Add edges of weight 0 between all virtual anyons
#         for i0, v0 in enumerate(anyons[mid:-1], start=mid):
#             for i1, v1 in enumerate(anyons[i0 + 1:], start=i0 + 1):
#                 edges.append([i0, i1, 0])

#         # Add edges between virtual anyons and real anyons
#         for i in range(mid):
#             (type, ys, xs) = anyons[i].sID
#             (type, yb, xb) = anyons[mid + i].sID
#             weight = abs(xb - xs) if type == 0 else abs(yb - ys)
#             edges.append([i, mid + i, weight])

#         return edges


#     def get_distances(self, V0, V1):
#         '''
#         Computes the distance or number of walks and direction between inputted nodes in x and y directions
#         '''

#         y0, x0 = V0.sID[1:]
#         y1, x1 = V1.sID[1:]
#         dy = y0 - y1
#         dx = x0 - x1

#         yd = "n" if dy > 0 else "s"
#         xd = "w" if dx < 0 else "e"

#         return abs(dy), yd, abs(dx), xd


#     def remove_virtual(self):
#         '''
#         Removes matchings between virtual anyons which have weight 0, as they do not account to real machtings.
#         '''
#         matching = []
#         for V1, V2, V3, V4, in self.matching:
#             if not (V1.type == 1 and V2.type == 1):
#                 matching.append([V1, V2, V3, V4])
#         self.matching = matching
