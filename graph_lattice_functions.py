import time
import random
from decimal import Decimal as dec
import graph_objects as go
import plot_graph_lattice as pg



def init_toric_graph(size, decoder, plot_load=False, plot_config=None):

    graph = go.iGraph(size, "toric", decoder)

    # Add vertices to graph
    for ertype in range(2):
        for y in range(size):
            for x in range(size):
                graph.add_stab((ertype, y, x))

    # Add edges to graph
    for y in range(size):
        for x in range(size):

            VL, VR = graph.S[(0, y, x)], graph.S[(0, y, (x + 1) % size)]
            VU, VD = graph.S[(1, (y - 1) % size, x)], graph.S[(1, y, x)]
            graph.add_qubit((y, x, 0), VL, VR, VU, VD)

            VU, VD = graph.S[(0, y, x)], graph.S[(0, (y + 1) % size, x)]
            VL, VR = graph.S[(1, y, (x - 1) % size)], graph.S[(1, y, x)]
            graph.add_qubit((y, x, 1), VL, VR, VU, VD)

    if plot_load:
        graph.plot = pg.lattice_plot(graph, **plot_config)

    return graph


def init_planar_graph(size, decoder, plot_load=False, plot_config=None):

    graph = go.iGraph(size, "planar", decoder)

    # Add vertices to graph
    for yx in range(size):
        for xy in range(size - 1):
            graph.add_stab((0, yx, xy + 1))
            graph.add_stab((1, xy, yx))

        graph.add_boundary((0, yx, 0))
        graph.add_boundary((0, yx, size))
        graph.add_boundary((1, -1, yx))
        graph.add_boundary((1, size - 1, yx))

    for y in range(size):
        for x in range(size):
            if x == 0:
                VL, VR = graph.B[(0, y, x)], graph.S[(0, y, x + 1)]
            elif x == size - 1:
                VL, VR = graph.S[(0, y, x)], graph.B[(0, y, x + 1)]
            else:
                VL, VR = graph.S[(0, y, x)], graph.S[(0, y, x + 1)]
            if y == 0:
                VU, VD = graph.B[(1, y - 1, x)], graph.S[(1, y, x)]
            elif y == size - 1:
                VU, VD = graph.S[(1, y - 1, x)], graph.B[(1, y, x)]
            else:
                VU, VD = graph.S[(1, y - 1, x)], graph.S[(1, y, x)]

            graph.add_qubit((y, x, 0), VL, VR, VU, VD)

            if y != size - 1 and x != size - 1:
                VU, VD = graph.S[(0, y, x + 1)], graph.S[(0, y + 1, x + 1)]
                VL, VR = graph.S[(1, y, x)], graph.S[(1, y, x + 1)]
                graph.add_qubit((y, x + 1, 1), VL, VR, VU, VD)

    if plot_load:
        graph.plot = pg.lattice_plot(graph, **plot_config)

    return graph


def init_random_seed(timestamp=None, worker=0, iteration=0, **kwargs):
    if timestamp is None:
        timestamp = time.time()
    seed = "{:.0f}".format(timestamp*10**7) + str(worker) + str(iteration)
    random.seed(dec(seed))
    return seed


def apply_random_seed(seed=None, **kwargs):
    if seed is None:
        seed = init_random_seed()
    if type(seed) is not dec:
        seed = dec(seed)
    random.seed(seed)


def init_erasure(graph, pE=0, **kwargs):
    """
    :param pE           probability of an erasure error
    :param savefile     toggle to save the errors to a file

    Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
    """

    if pE != 0:
        for qubit in graph.Q.values():
            if random.random() < pE:
                qubit.erasure = True
                rand = random.random()
                if rand < 0.25:
                    qubit.VXE.state = 1 - qubit.VXE.state
                elif rand >= 0.25 and rand < 0.5:
                    qubit.PZE.state = 1 - qubit.PZE.state
                elif rand >= 0.5 and rand < 0.75:
                    qubit.VXE.state = 1 - qubit.VXE.state
                    qubit.PZE.state = 1 - qubit.PZE.state

    if graph.plot: graph.plot.plot_erasures()


def init_pauli(graph, pX=0, pZ=0, **kwargs):
    """
    :param pX           probability of a Pauli X error
    :param pZ           probability of a Pauli Z error
    :param savefile     toggle to save the errors to a file

    initates Pauli X and Z errors on the lattice based on the error rates
    """

    if pX != 0 or pZ != 0:
        for qubit in graph.Q.values():
            if pX != 0 and random.random() < pX:
                qubit.VXE.state = 1 - qubit.VXE.state
            if pZ != 0 and random.random() < pZ:
                qubit.PZE.state = 1 - qubit.PZE.state

    if graph.plot: graph.plot.plot_errors()


def measure_stab(graph, **kwargs):
    """
    The measurement outcomes of the stabilizers, which are the vertices on the graph are saved to their corresponding vertex objects. We loop over all vertex objects and over their neighboring edge or qubit objects.
    """
    for stab in graph.S.values():
        for vertex, edge in stab.neighbors.values():
            if edge.state:
                stab.state = 1 - stab.state

    if graph.plot: graph.plot.plot_syndrome()


def logical_error(graph):

    """
    Finds whether there are any logical errors on the lattice/graph. The logical error is returned as [Xvertical, Xhorizontal, Zvertical, Zhorizontal], where each item represents a homological Loop
    """

    if graph.plot: graph.plot.plot_final()

    if graph.type == "toric":

        logical_error = [0, 0, 0, 0]

        for i in range(graph.size):
            if graph.Q[(i, 0, 0)].VXE.state:
                logical_error[0] = 1 - logical_error[0]
            if graph.Q[(0, i, 1)].VXE.state:
                logical_error[1] = 1 - logical_error[1]
            if graph.Q[(i, 0, 1)].PZE.state:
                logical_error[2] = 1 - logical_error[2]
            if graph.Q[(0, i, 0)].PZE.state:
                logical_error[3] = 1 - logical_error[3]

        errorless = True if logical_error == [0, 0, 0, 0] else False
        return logical_error, errorless

    elif graph.type == "planar":

        logical_error = [False, False]

        for i in range(graph.size):
            if graph.Q[(i, 0, 0)].VXE.state:
                logical_error[0] = 1 - logical_error[0]
            if graph.Q[(0, i, 0)].PZE.state:
                logical_error[1] = 1 - logical_error[1]

        errorless = True if logical_error == [0, 0] else False
        return logical_error, errorless
