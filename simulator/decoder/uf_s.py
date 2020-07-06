'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

The Union-Find decoder as described by arXiv:1709.06218v1

An OOP implementation has been made here, where the boundary and support are not stored as separate lists, which have to accesed based on some key value of the cluster. We store the boundary list and support for each cluster, and other paramters, directly at the cluster object.
The decoder requires a graph object, containing the vertices (stabilizers) and edges (qubits) of the uf-lattice. The graph can either be 2D (perfect measurements) or 2D (noisy measurements).
Two decoder classes are defined in this file, toric and planar for their respective lattice types.
'''


from simulator.info import printing as pr
from simulator.decoder import uf_sb, uf_d
from simulator.decoder.modules_uf._decorators import *

class toric(uf_sb.toric, uf_d.toric):
    '''
    Union-Find decoder for the toric lattice (2D and 3D)
    '''
    def __init__(self, *args, **kwargs):
        '''
        Optionally acceps config dict which contains plotting options.
        Counters for decoder specific heuristics are initialized.
        Decoder options, defined in kwargs are stored as class variables.
        '''
        super().__init__(*args, **kwargs)
        self.type = "uf_s"
        self.name = "Static-forest Union-Find"

class planar(uf_sb.planar, uf_d.planar, toric):
    pass
