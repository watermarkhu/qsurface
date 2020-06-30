'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

The Minimum Weight Perfect Matching decoder

Uses either Kolmogorov's Blossom 5 algorithm:
    Vladimir Kolmogorov. "Blossom V: A new implementation of a minimum cost perfect matching algorithm."
            In Mathematical Programming Computation (MPC), July 2009, 1(1):43-67.
'''
import os
import time
import ctypes
from numpy.ctypeslib import ndpointer
from simulator.info.decorators import debug
from simulator.decoder import mwpm


def getMatching_fast(numNodes, nodes1, nodes2, weights):

    numEdges = len(nodes1)

    PMlib = ctypes.CDLL(
        "%s/blossom5/PMlib.so" % "/".join(
            (os.path.realpath(__file__)).split("/")[:-1])
    )

    PMlib.pyMatching.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]

    PMlib.pyMatching.restype = ndpointer(dtype=ctypes.c_int, shape=(numNodes,))

    # initialize ctypes array and fill with edge data
    n1 = (ctypes.c_int * numEdges)()
    n2 = (ctypes.c_int * numEdges)()
    w = (ctypes.c_int * numEdges)()

    for i in range(numEdges):
        n1[i], n2[i], w[i] = nodes1[i], nodes2[i], weights[i]

    result = PMlib.pyMatching(ctypes.c_int(
        numNodes), ctypes.c_int(numEdges), n1, n2, w)

    return result


def getMatching(numNodes, graphArray):

    numEdges = len(graphArray)

    PMlib = ctypes.CDLL(
        "%s/blossom5/PMlib.so" % "/".join(
            (os.path.realpath(__file__)).split("/")[:-1])
    )

    PMlib.pyMatching.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]

    PMlib.pyMatching.restype = ndpointer(dtype=ctypes.c_int, shape=(numNodes,))

    # initialize ctypes array and fill with edge data
    nodes1 = (ctypes.c_int * numEdges)()
    nodes2 = (ctypes.c_int * numEdges)()
    weights = (ctypes.c_int * numEdges)()

    # c_int_array = ctypes.c_int*numEdges
    # nodes1 = c_int_array(*[graphArray[i][0] for i in range(numEdges)])

    for i in range(numEdges):
        nodes1[i] = graphArray[i][0]
        nodes2[i] = graphArray[i][1]
        weights[i] = graphArray[i][2]

    return PMlib.pyMatching(
        ctypes.c_int(numNodes), ctypes.c_int(numEdges), nodes1, nodes2, weights
    )


class toric(mwpm.toric):
    '''
    MWPM decoder for the toric lattice (2D and 3D).
    Edges between all anyons are considered.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "blossom"

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
