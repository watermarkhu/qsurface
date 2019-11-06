import networkx as nx
import blossom5.pyMatch as pm

"""
:param size:
:param plot_load:

 We define the unit cell, which contains two qubits, a star operator and plaquette operator.

    |       |
- Star  -  Q_0 -     also top (T) qubit
    |       |
-  Q_1  - Plaq  -    also down (D) qubit
    |       |

By doing so, we can define arrays the star and plaquette operators, where their index value define their position
  on the qubit lattice. For the qubit array, there is an extra dimension to store the two qubits per unit cell.

self.array stores the qubit values and has dimension [XZ_error{0,1}, Top_down{0,1}, size, size]
Qubit values are either 0 or 1, which is analogous to the -1, and 1 state, respectively
"""


def measure_stab(graph, toric_plot=None):
    """
    The measurement outcomes of the stabilizers, which are the vertices on the graph are saved to their corresponding vertex objects. We loop over all vertex objects and over their neighboring edge or qubit objects.
    """

    for vertex in graph.V.values():
        for dir in graph.wind:
            if dir in vertex.neighbors:
                if vertex.neighbors[dir][1].state:
                    vertex.state = not vertex.state

    if toric_plot is not None:
        toric_plot.plot_anyons()


def get_matching_mwpm(graph):
    """
    Uses the MWPM algorithm to get the matchings. A list of combinations of all the anyons and their respective weights are feeded to the blossom5 algorithm. To apply the matchings, we walk from each matching vertex to where their paths meet perpendicualarly, flipping the edges on the way over.
    """

    nxgraph = nx.Graph()

    all_anyons = []
    num = 0

    for ertype in range(2):
        anyons = []  # Get all anyons as MWPM algorithm requires
        for y in range(graph.size):
            for x in range(graph.size):
                vertex = graph.V[(ertype, y, x)]
                if vertex.state:
                    anyons.append(vertex)
        all_anyons += anyons

        for i0, v0 in enumerate(anyons[:-1]):
            (_, y0, x0) = v0.sID
            for i1, v1 in enumerate(anyons[i0 + 1 :]):
                (_, y1, x1) = v1.sID
                wy = (y0 - y1) % (graph.size)
                wx = (x0 - x1) % (graph.size)
                weight = min([wy, graph.size - wy]) + min([wx, graph.size - wx])
                nxgraph.add_edge(num + i0, num + i1 + i0 + 1, weight=-weight)

        num = len(anyons)

    matching = nx.algorithms.matching.max_weight_matching(nxgraph, maxcardinality=True)
    return [[all_anyons[i0], all_anyons[i1]] for i0, i1 in matching]


def get_matching_blossom5(graph):
    """
    Uses the BlossomV algorithm to get the matchings. A list of combinations of all the anyons and their respective weights are feeded to the blossom5 algorithm. To apply the matchings, we walk from each matching vertex to where their paths meet perpendicualarly, flipping the edges on the way over.
    """

    edges = []  # Get all possible edges between the anyons and their weights

    all_anyons = []
    num = 0

    for ertype in range(2):
        anyons = []  # Get all anyons as MWPM algorithm requires
        for y in range(graph.size):
            for x in range(graph.size):
                vertex = graph.V[(ertype, y, x)]
                if vertex.state:
                    anyons.append(vertex)
        all_anyons += anyons

        for i0, v0 in enumerate(anyons[:-1]):
            (_, y0, x0) = v0.sID
            for i1, v1 in enumerate(anyons[i0 + 1 :]):
                (_, y1, x1) = v1.sID
                wy = (y0 - y1) % (graph.size)
                wx = (x0 - x1) % (graph.size)
                weight = min([wy, graph.size - wy]) + min([wx, graph.size - wx])
                edges.append([num + i0, num + i1 + i0 + 1, weight])

        num = len(anyons)

    output = pm.getMatching(len(anyons), edges) if anyons != [] else []
    return [[all_anyons[i0], all_anyons[i1]] for i0, i1 in enumerate(output) if i0 > i1]


def apply_matching_mwpm(graph, matching_pairs, toric_plot=None):

    for v0, v1 in matching_pairs:  # Apply the matchings to the graph

        (_, y0, x0) = v0.sID
        (_, y1, x1) = v1.sID

        dy0 = (
            y0 - y1
        ) % graph.size  # Get distance between endpoints, take modulo to find min distance
        dx0 = (x0 - x1) % graph.size
        dy1 = (y1 - y0) % graph.size
        dx1 = (x1 - x0) % graph.size

        if dy0 < dy1:  # Find closest path and walking direction
            dy = dy0
            yd = "u"
        else:
            dy = dy1
            yd = "d"
        if dx0 < dx1:
            dx = dx0
            xd = "r"
        else:
            dx = dx1
            xd = "l"

        ynext = v0  # walk vertically from v0
        for y in range(dy):
            (ynext, edge) = ynext.neighbors[yd]
            edge.state = not edge.state
            edge.matching = not edge.matching

        xnext = v1  # walk horizontally from v1
        for x in range(dx):
            (xnext, edge) = xnext.neighbors[xd]
            edge.state = not edge.state
            edge.matching = not edge.matching

    if toric_plot is not None:
        toric_plot.plot_lines(matching_pairs)
        toric_plot.plot_final()


def apply_matching_peeling(graph, toric_plot=None):
    """
    Uses the Peeling algorithm to get the matchings
    Optionally, edge_data can be inputted here, which is useful in multiple iteration simulations
    """
    for edge in graph.E.values():
        if edge.matching:
            edge.state = not edge.state

    if toric_plot is not None:
        toric_plot.plot_final()


def logical_error(graph):

    """
    Finds whether there are any logical errors on the lattice/graph. The logical error is returned as [Xvertical, Xhorizontal, Zvertical, Zhorizontal], where each item represents a homological Loop
    """
    logical_error = [False, False, False, False]

    for i in range(graph.size):
        if graph.E[(0, i, 0, 0)].state:
            logical_error[0] = not logical_error[0]
        if graph.E[(0, 0, i, 1)].state:
            logical_error[1] = not logical_error[1]
        if graph.E[(1, i, 0, 1)].state:
            logical_error[2] = not logical_error[2]
        if graph.E[(1, 0, i, 0)].state:
            logical_error[3] = not logical_error[3]

    return logical_error
