"""
The Union-Find Node-Suspension decoder [hu2020thesis]_ uses the potential matching weight as a heuristic to prioritize  growth in specific partitions -- the nodes -- of the Union-Find cluster (see :ref:`union-find-decoder`). The potential matching weight is approximated by levering a node-tree in the Node-Suspension Data-structure. The elements of the node-tree are descendent objects of `~.ufns.elements.Node`. 

The complexity of the algorithm is determined by the calculation of the *node parity* in `~.ufns.elements.Node.ns_parity`, the *node delay* in `~.ufns.elements.Node.ns_delay`, and the growth of the cluster, which is now applied as a recursive function that inspects all nodes in the node tree (`.ufns.sim.Toric.grow_node`). During cluster mergers, additional to `~.unionfind.elements.Cluster.union`, node-trees are joined by `~.ufns.sim.Toric.join_node_trees`. 

.. todo:: Proper calculation of delay for erasures/empty nodes in the graph
"""

from . import sim
from . import plot
from . import elements
