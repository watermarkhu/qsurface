'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
import os
import ctypes
from numpy.ctypeslib import ndpointer


def getMatching_fast(numNodes, nodes1, nodes2, weights):

    numEdges = len(nodes1)

    PMlib = ctypes.CDLL(
        "%s/PMlib.so" % "/".join(
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
        "%s/PMlib.so" % "/".join(
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
