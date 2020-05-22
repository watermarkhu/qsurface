'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

The Union-Find decoder as described by arXiv:1709.06218v1

An OOP implementation has been made here, where the boundary and support are not stored as separate lists, which have to accesed based on some key value of the cluster. We store the boundary list and support for each cluster, and other paramters, directly at the cluster object.
The decoder requires a graph object, containing the vertices (stabilizers) and edges (qubits) of the uf-lattice. The graph can either be 2D (perfect measurements) or 2D (noisy measurements).
Two decoder classes are defined in this file, toric and planar for their respective lattice types.
'''


from ..info.decorators import debug, plot
from ..info import printing as pr
from . import uf, uf_ndf, uf_uwg


class toric(uf_ndf.toric, uf_uwg.toric):
    '''
    Union-Find decoder for the toric lattice (2D and 3D)
    '''
    @debug.init_counters_uf()
    def __init__(self, plot_config=None, *args, **kwargs):
        '''
        Optionally acceps config dict which contains plotting options.
        Counters for decoder specific heuristics are initialized.
        Decoder options, defined in kwargs are stored as class variables.
        '''
        super().__init__(*args, **kwargs)
        self.type = "uf_ndf_uwg"

class planar(uf_ndf.planar, uf_uwg.planar, toric):
    pass
