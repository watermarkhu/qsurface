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
from . import uf


class toric(uf.toric):
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
        self.type = "uf_ndf"


    def edge_growth_choices(self, edge, aV, pV, aC, pC):
        '''
        Checks the type of the fully grown edge.
        1. if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        2. elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
        3. else:   Edge is between two separate clusters. Returns true to perform some function
        '''
        union = False
        if pC is None:
            aC.add_vertex(pV)
            self.cluster_new_vertex(aC, pV, self.plot_growth)
        elif pC is aC:
            pass
        else:
            union = True
        return union

    '''
    ##################################################################################################

                                            3. Peel clusters

    ##################################################################################################
    '''
    @plot.iter_peel_clusters()
    def peel_clusters(self, *args, **kwargs):
        """
        Loops overal all vertices to find pendant vertices which are selected from peeling using {peel_edge}

        """
        for layer in self.graph.S.values():
            for vertex in layer.values():
                if vertex.cluster is not None:
                    self.forest(vertex)
                    cluster = self.get_vertex_cluster(vertex)
                    self.peel_edge(cluster, vertex)


    def forest(self, vertex):
        vertex.forest = 1
        for (NV, NE) in vertex.neighbors.values():
            if NE.support == 2:
                if NV.forest == 1:
                    if NE.forest == 0:
                        NE.support = 0
                        if self.plot:
                            if self.plot_cut:
                                self.plot.new_iter(str(NE) + " cut")
                            self.plot.add_edge(NE, vertex)
                            if self.plot_cut:
                                self.plot.draw_plot()
                else:
                    NE.forest = 1
                    self.forest(NV)


class planar(uf.planar, toric):
    pass
