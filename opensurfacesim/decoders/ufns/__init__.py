"""
This implementation has full integrated the Balanced Bloom algorithm, where boundary edges are not stored at the cluster, but rather at the basetree-nodes.
Two decoder classes are defined in this file, toric and planar for their respective lattice types.
_____________________________________________

Objects and methods for the directed graph version of the Balanced Bloom algorithm

A undirected graph refers to that each node in the graph has a parameter cons (connections) refereing to the edges and nodes connected to this node.
During a merge of two tree's, these connections needs simply to be added in each of the nodes.

merge between M0 and M1::

      R0         R1
     /  \       /  \\
    N0   M0 == M1   N1

Connections before:

    R0: [N0, M0],  N0: [R0],  M0: [R0]
    R1: [N1, M1],  N1: [R1],  M1: [R1]

Tree after merge::

      R0
     /  \\
    N0   M0
          \\
           M1
            \\
             R1
              \\
               N1

Connection after:

R0: [N0, M0],  N0: [R0],  M0: [R0, M1]
R1: [N1, M1],  N1: [R1],  M1: [R1, M0]


# TODO: Proper calculation of delay for erasures/empty nodes in the graph
"""

from . import sim
from . import plot
from . import elements