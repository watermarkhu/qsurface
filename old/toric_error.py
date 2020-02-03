import sys
import time
import datetime
import random
from decimal import Decimal as dec


def init_random_seed(timestamp=None, worker=0, iteration=0):
    if timestamp is None:
        timestamp = time.time()
    seed = int("{:.0f}".format(timestamp*10**7) + str(worker) + str(iteration))
    random.seed(dec(seed))
    return seed

def apply_random_seed(seed=None):
    if seed is None:
        seed = init_random_seed()
    if type(seed) is not dec:
        seed = dec(seed)
    random.seed(seed)


def init_erasure_region(
    graph, pE=0, toric_plot=None, savefile=0, timestamp=None, erasure_file=None, **kwargs
):
    """
    :param pE           probability of an erasure error
    :param savefile     toggle to save the errors to a file

    Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error. This function is the same as init_erasure_errors, except that for every erasure, its (6) neighbor edges are also initated as an erasure. The error rate is therefore higher than pE.
    """

    if erasure_file is None:
        if pE != 0:
            for y0 in range(graph.size):  # Loop over all qubits
                for td in range(2):
                    for x0 in range(graph.size):
                        if random.random() < pE:
                            region = {(y0, x0, td)}
                            (y1, x1) = (
                                (y0, (x0 + 1) % graph.size)
                                if td == 0
                                else ((y0 + 1) % graph.size, x0)
                            )

                            locs = [(y0, x0), (y1, x1)]
                            for y, x in locs:
                                vertex = graph.V[(0, y, x)]
                                for wind in graph.wind:
                                    (n_vertex, edge) = vertex.neighbors[wind]
                                    (type, y, x, td) = edge.qID
                                    region.add(
                                        (y, x, td)
                                    )  # Get all qubits around erasure center, create region

                            for (
                                y,
                                x,
                                td,
                            ) in region:  # Apply uniform Pauli errors on erasure region
                                graph.E[
                                    (0, y, x, td)
                                ].erasure = True  # Set erasure state
                                graph.E[(1, y, x, td)].erasure = True
                                rand = random.random()
                                if rand < 0.25:
                                    graph.E[(0, y, x, td)].state = not graph.E[
                                        (0, y, x, td)
                                    ].state
                                elif rand >= 0.25 and rand < 0.5:
                                    graph.E[(1, y, x, td)].state = not graph.E[
                                        (1, y, x, td)
                                    ].state
                                elif rand >= 0.5 and rand < 0.75:
                                    graph.E[(0, y, x, td)].state = not graph.E[
                                        (0, y, x, td)
                                    ].state
                                    graph.E[(1, y, x, td)].state = not graph.E[
                                        (1, y, x, td)
                                    ].state

        if savefile:
            if timestamp is not None:
                st = datetime.datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d_%H-%M-%S"
                )
                name = "./errors/" + st + "_erasure.txt"
            else:
                name = "./errors/erasure.txt"
            st2 = datetime.datetime.fromtimestamp(time.time()).strftime(
                "%Y-%m-%d %H-%M-%S"
            )
            f = open(name, "w")
            f.write("Erasure error file created on " + st2 + "\n")
            f.write("L = " + str(graph.size) + "\n\n")
            e_file = "pE = " + str(pE) + "\n"
            for y in range(graph.size):
                for td in range(2):
                    if td == 0:
                        e_file += "  "
                    for x in range(graph.size):
                        if graph.E[(0, y, x, td)].erasure:
                            Xstate = graph.E[(0, y, x, td)].state
                            Zstate = graph.E[(1, y, x, td)].state
                            if not Xstate and not Zstate:
                                e_state = 1
                            elif Xstate and not Zstate:
                                e_state = 2
                            elif not Xstate and Zstate:
                                e_state = 3
                            else:
                                e_state = 4
                        else:
                            e_state = 0
                        e_file += str(e_state) + "   "
                    e_file += "\n"
            f.write(e_file + "\n")
            f.close()
    else:
        timestamp, _ = read_erasure(graph, erasure_file)

    if toric_plot is not None:
        toric_plot.plot_erasures()


def init_erasure(
    graph, pE=0, toric_plot=None, savefile=0, timestamp=None, erasure_file=None, **kwargs
):
    """
    :param pE           probability of an erasure error
    :param savefile     toggle to save the errors to a file

    Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
    """
    if erasure_file is None:
        # Write first lines of error file
        if savefile:
            if timestamp is not None:
                st = datetime.datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d_%H-%M-%S"
                )
                name = "./errors/" + st + "_erasure.txt"
            else:
                name = "./errors/erasure.txt"
            st2 = datetime.datetime.fromtimestamp(time.time()).strftime(
                "%Y-%m-%d %H-%M-%S"
            )
            f = open(name, "w")
            f.write("Erasure error file created on " + st2 + "\n")
            f.write("L = " + str(graph.size) + "\n\n")
            e_file = "pE = " + str(pE) + "\n"

        # Loop over all qubits
        for y in range(graph.size):
            for td in range(2):
                if savefile and td == 0:
                    e_file += "  "
                for x in range(graph.size):  # Loop over all qubits
                    if random.random() < pE:

                        graph.E[(0, y, x, td)].erasure = True  # Set erasure state
                        graph.E[(1, y, x, td)].erasure = True

                        rand = random.random()  # Apply random X or Z error on erasure
                        if rand < 0.25:
                            graph.E[(0, y, x, td)].state = not graph.E[
                                (0, y, x, td)
                            ].state
                            e_state = 2
                        elif rand >= 0.25 and rand < 0.5:
                            graph.E[(1, y, x, td)].state = not graph.E[
                                (1, y, x, td)
                            ].state
                            e_state = 3
                        elif rand >= 0.5 and rand < 0.75:
                            graph.E[(0, y, x, td)].state = not graph.E[
                                (0, y, x, td)
                            ].state
                            graph.E[(1, y, x, td)].state = not graph.E[
                                (1, y, x, td)
                            ].state
                            e_state = 4
                        else:
                            e_state = 1
                    else:
                        e_state = 0
                    if savefile:
                        e_file += str(e_state) + "   "
                if savefile:
                    e_file += "\n"
        if savefile:
            f.write(e_file + "\n")
            f.close()
    else:
        read_erasure(graph, erasure_file)

    if toric_plot is not None:
        toric_plot.plot_erasures()


def init_pauli(
    graph, pX=0, pZ=0, toric_plot=None, savefile=0, timestamp=None, pauli_file=None, **kwargs
):
    """
    :param pX           probability of a Pauli X error
    :param pZ           probability of a Pauli Z error
    :param savefile     toggle to save the errors to a file

    initates Pauli X and Z errors on the lattice based on the error rates
    """
    if pauli_file is None:
        # Write first lines of error file
        if savefile:
            if timestamp is not None:
                st = datetime.datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d_%H-%M-%S"
                )
                name = "./errors/" + st + "_pauli.txt"
            else:
                name = "./errors/pauli.txt"
            st2 = datetime.datetime.fromtimestamp(time.time()).strftime(
                "%Y-%m-%d %H-%M-%S"
            )
            f = open(name, "w")
            f.write("Pauli error file created on " + st2 + "\n")
            f.write("L = " + str(graph.size) + "\n\n")
            x_file = "pX = " + str(pX) + "\n"
            z_file = "pZ = " + str(pZ) + "\n"

        for y in range(graph.size):
            for td in range(2):
                if savefile and td == 0:
                    x_file += "  "
                    z_file += "  "
                for x in range(graph.size):  # Loop over all qubits

                    if pX != 0:  # Apply X error if chance > 0
                        if random.random() < pX:
                            graph.E[(0, y, x, td)].state = not graph.E[
                                (0, y, x, td)
                            ].state
                            x_state = 1
                        else:
                            x_state = 0
                    else:
                        x_state = 0

                    if pZ != 0:  # Apply Z error if chance > 0
                        if random.random() < pZ:
                            graph.E[(1, y, x, td)].state = not graph.E[
                                (1, y, x, td)
                            ].state
                            z_state = 1
                        else:
                            z_state = 0
                    else:
                        z_state = 0

                    if savefile:
                        x_file += str(x_state) + "   "
                        z_file += str(z_state) + "   "
                if savefile:
                    x_file += "\n"
                    z_file += "\n"
        if savefile:
            f.write(x_file + "\n")
            f.write(z_file + "\n")
            f.close()
    else:
        read_pauli(graph, pauli_file)

    if toric_plot is not None:
        toric_plot.plot_errors()


def read_erasure(graph, erasure_file):
    """
    Reads the erasure errors from the erasure file.
    """
    filename = "./errors/" + erasure_file + ".txt"
    try:
        erasure_errors = open(filename, "r")
    except FileNotFoundError:
        sys.exit("Error file not found")
    firstlines = [next(erasure_errors) for _ in range(3)]
    graph.size = int(firstlines[1][4:])
    pE = float(next(erasure_errors)[5:])

    for linenum in range(graph.size * 2):
        line = next(erasure_errors)
        y = linenum // 2
        td = linenum % 2
        for x in range(graph.size):
            if td == 0:
                state = int(line[2 + x * 4])
            else:
                state = int(line[x * 4])
            if state != 0:
                graph.E[(0, y, x, td)].erasure = True
                graph.E[(1, y, x, td)].erasure = True
                if state == 2:
                    graph.E[(0, y, x, td)].state = not graph.E[(0, y, x, td)].state
                elif state == 3:
                    graph.E[(1, y, x, td)].state = not graph.E[(1, y, x, td)].state
                elif state == 4:
                    graph.E[(0, y, x, td)].state = not graph.E[(0, y, x, td)].state
                    graph.E[(1, y, x, td)].state = not graph.E[(1, y, x, td)].state
    return pE


def read_pauli(graph, pauli_file):
    """
    Reads the pauli errors from the pauli file

    """
    filename = "./errors/" + pauli_file + ".txt"
    try:
        pauli_errors = open(filename, "r")
    except FileNotFoundError:
        sys.exit("Error file not found")
    firstlines = [next(pauli_errors) for _ in range(3)]

    graph.size = int(firstlines[1][4:])

    pX = float(next(pauli_errors)[5:])

    for linenum in range(graph.size * 2):
        line = next(pauli_errors)
        y = linenum // 2
        td = linenum % 2
        for x in range(graph.size):
            if td == 0:
                state = int(line[2 + x * 4])
            else:
                state = int(line[x * 4])
            if state == 1:
                graph.E[(0, y, x, td)].state = not graph.E[(0, y, x, td)].state

    line = next(pauli_errors)
    pZ = float(next(pauli_errors)[5:])

    for linenum in range(graph.size * 2):
        line = next(pauli_errors)
        y = linenum // 2
        td = linenum % 2
        for x in range(graph.size):
            if td == 0:
                state = int(line[2 + x * 4])
            else:
                state = int(line[x * 4])
            if state == 1:
                graph.E[(1, y, x, td)].state = not graph.E[(1, y, x, td)].state

    return pX, pZ
