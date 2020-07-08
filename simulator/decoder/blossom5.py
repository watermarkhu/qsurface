'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

The Minimum Weight Perfect Matching decoder

Uses either Kolmogorov's Blossom V algorithm:
    Vladimir Kolmogorov. "Blossom V: A new implementation of a minimum cost perfect matching algorithm."
            In Mathematical Programming Computation (MPC), July 2009, 1(1):43-67.
'''
import time
from simulator.decoder import mwpm
from simulator.decoder.modules_blossom5.methods import *


class toric(mwpm.toric):
    '''
    MWPM decoder for the toric lattice (2D and 3D).
    Edges between all anyons are considered.
    '''

    def __init__(self, graph,
                 name="Minimum-Weight Perfect Matching (blossomV)",
                 config={},
                 **kwargs):
        super().__init__(graph, name, config, **kwargs)

    def get_matching(self, anyons, d_anyons):
        output = getMatching(len(anyons), self.get_edges(anyons))
        return [[d_anyons[i0], d_anyons[i1], anyons[i0], anyons[i1]] for i0, i1 in enumerate(output) if i0 > i1]



class planar(mwpm.planar, toric):
    '''
    Decodes the planar lattice (2D and 3D).
    Edges between all anyons are considered.
    Additionally, virtual anyons are added to the boundary, which connect to their main anyons.
    Edges between all virtual anyons are added with weight zero.
    '''
    pass
