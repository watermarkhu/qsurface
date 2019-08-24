import os
import sys
import time
import datetime
import random
import networkx as nx
import blossom5.pyMatch as pm


class errors:

    def __init__(self, graph, toric_plot=None, worker=None):

        '''
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
        '''
        self.time = time.time()
        self.graph = graph
        self.toric_plot = toric_plot

        if not os.path.exists("./errors/"):
            os.makedirs("./errors/")

        if worker is None:
            # random.seed(self.time)        # if random seed need even when loading errors
            random.seed(self.time)        # load seed from file
        else:
            random.seed(float(str(worker) + str(self.time)))    # makes sure that each worker has different seeds


    def init_erasure_region(self, pE=0, savefile=False, erasure_file=None):
        '''
        :param pE           probability of an erasure error
        :param savefile     toggle to save the errors to a file

        Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error. This function is the same as init_erasure_errors, except that for every erasure, its (6) neighbor edges are also initated as an erasure. The error rate is therefore higher than pE.
        '''

        if erasure_file is None:
            self.time = time.time()

            if pE != 0:
                for y in range(self.graph.size):                          # Loop over all qubits
                    for td in range(2):
                        for x in range(self.graph.size):
                            if random.random() < pE:
                                region = {(y, x, td)}

                                vertices = self.graph.E[(0, y, x, td)].vertices
                                for vertex in vertices:
                                    for wind in self.graph.wind:
                                        (n_vertex, edge) = vertex.neighbors[wind]
                                        (type, y, x, td) = edge.qID
                                        region.add((y, x, td))      # Get all qubits around erasure center, create region

                                for (y, x, td) in region:           # Apply uniform Pauli errors on erasure region
                                    self.graph.E[(0, y, x, td)].erasure = True      # Set erasure state
                                    self.graph.E[(1, y, x, td)].erasure = True
                                    rand = random.random()
                                    if rand < 0.25:
                                        self.graph.E[(0, y, x, td)].state = not self.graph.E[(0, y, x, td)].state
                                    elif rand >= 0.25 and rand < 0.5:
                                        self.graph.E[(1, y, x, td)].state = not self.graph.E[(1, y, x, td)].state
                                    elif rand >= 0.5 and rand < 0.75:
                                        self.graph.E[(0, y, x, td)].state = not self.graph.E[(0, y, x, td)].state
                                        self.graph.E[(1, y, x, td)].state = not self.graph.E[(1, y, x, td)].state

            if savefile:
                st = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d_%H-%M-%S')
                st2 = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H-%M-%S')
                name = "./errors/" + st + "_erasure.txt"
                f = open(name, "w")
                f.write("Erasure error file created on " + st2 + "\n")
                f.write("Seed = " + str(self.time) + "\n")
                f.write("L = " + str(self.graph.size) + "\n\n")
                e_file = "pE = " + str(pE) + "\n"
                for y in range(self.graph.size):
                    for td in range(2):
                        if td == 0:
                            e_file += "  "
                        for x in range(self.graph.size):
                            if self.graph.E[(0, y, x, td)].erasure:
                                Xstate = self.graph.E[(0, y, x, td)].state
                                Zstate = self.graph.E[(1, y, x, td)].state
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
            self.read_erasure(erasure_file)

        if self.toric_plot is not None:
            self.toric_plot.plot_erasures()

    def init_erasure(self, pE=0, savefile=False, erasure_file=None):
        '''
        :param pE           probability of an erasure error
        :param savefile     toggle to save the errors to a file

        Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
        '''
        if erasure_file is None:
            self.time = time.time()

            # Write first lines of error file
            if savefile:
                st = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d_%H-%M-%S')
                st2 = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H-%M-%S')
                name = "./errors/" + st + "_erasure.txt"
                f = open(name, "w")
                f.write("Erasure error file created on " + st2 + "\n")
                f.write("Seed = " + str(self.time) + "\n")
                f.write("L = " + str(self.graph.size) + "\n\n")
                e_file = "pE = " + str(pE) + "\n"

            # Loop over all qubits
            for y in range(self.graph.size):
                for td in range(2):
                    if savefile and td == 0:
                        e_file += "  "
                    for x in range(self.graph.size):                      # Loop over all qubits
                        if random.random() < pE:

                            self.graph.E[(0, y, x, td)].erasure = True  # Set erasure state
                            self.graph.E[(1, y, x, td)].erasure = True

                            rand = random.random()                  # Apply random X or Z error on erasure
                            if rand < 0.25:
                                self.graph.E[(0, y, x, td)].state = not self.graph.E[(0, y, x, td)].state
                                e_state = 2
                            elif rand >= 0.25 and rand < 0.5:
                                self.graph.E[(1, y, x, td)].state = not self.graph.E[(1, y, x, td)].state
                                e_state = 3
                            elif rand >= 0.5 and rand < 0.75:
                                self.graph.E[(0, y, x, td)].state = not self.graph.E[(0, y, x, td)].state
                                self.graph.E[(1, y, x, td)].state = not self.graph.E[(1, y, x, td)].state
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
            self.read_erasure(erasure_file)

        if self.toric_plot is not None:
            self.toric_plot.plot_erasures()

    def init_pauli(self, pX=0, pZ=0, savefile=False, pauli_file=None):
        '''
        :param pX           probability of a Pauli X error
        :param pZ           probability of a Pauli Z error
        :param savefile     toggle to save the errors to a file

        initates Pauli X and Z errors on the lattice based on the error rates
        '''

        if pauli_file is None:
            self.time = time.time()

            # Write first lines of error file
            if savefile:
                st = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d_%H-%M-%S')
                st2 = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H-%M-%S')
                name = "./errors/" + st + "_pauli.txt"
                f = open(name, "w")
                f.write("Pauli error file created on " + st2 + "\n")
                f.write("Seed = " + str(self.time) + "\n")
                f.write("L = " + str(self.graph.size) + "\n\n")
                x_file = "pX = " + str(pX) + "\n"
                z_file = "pZ = " + str(pZ) + "\n"

            for y in range(self.graph.size):
                for td in range(2):
                    if savefile and td == 0:
                        x_file += "  "
                        z_file += "  "
                    for x in range(self.graph.size):      # Loop over all qubits

                        if pX != 0:                 # Apply X error if chance > 0
                            if random.random() < pX:
                                self.graph.E[(0, y, x, td)].state = not self.graph.E[(0, y, x, td)].state
                                x_state = 1
                            else:
                                x_state = 0
                        else:
                            x_state = 0

                        if pZ != 0:                 # Apply Z error if chance > 0
                            if random.random() < pZ:
                                self.graph.E[(1, y, x, td)].state = not self.graph.E[(1, y, x, td)].state
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
            self.read_pauli(pauli_file)

        if self.toric_plot is not None:
            self.toric_plot.plot_errors()

    def read_erasure(self, erasure_file):
        '''
        Reads the erasure errors from the erasure file.
        '''
        filename = "./errors/" + erasure_file + ".txt"
        try:
            erasure_errors = open(filename, "r")
        except FileNotFoundError:
            sys.exit("Error file not found")
        firstlines = [next(erasure_errors) for _ in range(4)]
        self.time = float(firstlines[1][7:])
        self.graph.size = int(firstlines[2][4:])
        self.pE = float(next(erasure_errors)[5:])

        for linenum in range(self.graph.size*2):
            line = next(erasure_errors)
            y = linenum // 2
            td = linenum % 2
            for x in range(self.graph.size):
                if td == 0:
                    state = int(line[2 + x*4])
                else:
                    state = int(line[x*4])
                if state != 0:
                    self.graph.E[(0, y, x, td)].erasure = True
                    self.graph.E[(1, y, x, td)].erasure = True
                    if state == 2:
                        self.graph.E[(0, y, x, td)].state = not self.graph.E[(0, y, x, td)].state
                    elif state == 3:
                        self.graph.E[(1, y, x, td)].state = not self.graph.E[(1, y, x, td)].state
                    elif state == 4:
                        self.graph.E[(0, y, x, td)].state = not self.graph.E[(0, y, x, td)].state
                        self.graph.E[(1, y, x, td)].state = not self.graph.E[(1, y, x, td)].state

    def read_pauli(self, pauli_file):
        '''
        Reads the pauli errors from the pauli file

        '''
        filename = "./errors/" + pauli_file + ".txt"
        try:
            pauli_errors = open(filename, "r")
        except FileNotFoundError:
            sys.exit("Error file not found")
        firstlines = [next(pauli_errors) for _ in range(4)]
        self.time = float(firstlines[1][7:])
        self.graph.size = int(firstlines[2][4:])
        self.pX = float(next(pauli_errors)[5:])

        for linenum in range(self.graph.size*2):
            line = next(pauli_errors)
            y = linenum // 2
            td = linenum % 2
            for x in range(self.graph.size):
                if td == 0:
                    state = int(line[2 + x*4])
                else:
                    state = int(line[x*4])
                if state == 1:
                    self.graph.E[(0, y, x, td)].state = not self.graph.E[(0, y, x, td)].state

        line = next(pauli_errors)
        self.pZ = float(next(pauli_errors)[5:])

        for linenum in range(self.graph.size*2):
            line = next(pauli_errors)
            y = linenum // 2
            td = linenum % 2
            for x in range(self.graph.size):
                if td == 0:
                    state = int(line[2 + x*4])
                else:
                    state = int(line[x*4])
                if state == 1:
                    self.graph.E[(1, y, x, td)].state = not self.graph.E[(1, y, x, td)].state


    '''
    Main functions
    '''


def measure_stab(graph, toric_plot=None):
    '''
    The measurement outcomes of the stabilizers, which are the vertices on the graph are saved to their corresponding vertex objects. We loop over all vertex objects and over their neighboring edge or qubit objects.
    '''

    for vertex in graph.V.values():
        for dir in graph.wind:
            if dir in vertex.neighbors:
                if vertex.neighbors[dir][1].state:
                    vertex.state = not vertex.state

    if toric_plot is not None:
        toric_plot.plot_anyons()


def get_matching_mwpm(graph):
    '''
    Uses the MWPM algorithm to get the matchings. A list of combinations of all the anyons and their respective weights are feeded to the blossom5 algorithm. To apply the matchings, we walk from each matching vertex to where their paths meet perpendicualarly, flipping the edges on the way over.
    '''

    nxgraph = nx.Graph()

    all_anyons = []
    num = 0

    for ertype in range(2):
        anyons = []                     # Get all anyons as MWPM algorithm requires
        for y in range(graph.size):
            for x in range(graph.size):
                vertex = graph.V[(ertype, y, x)]
                if vertex.state:
                    anyons.append(vertex)
        all_anyons += anyons

        for i0, v0 in enumerate(anyons[:-1]):
            (_, y0, x0) = v0.sID
            for i1, v1 in enumerate(anyons[i0 + 1:]):
                (_, y1, x1) = v1.sID
                wy = (y0 - y1) % (graph.size)
                wx = (x0 - x1) % (graph.size)
                weight = min([wy, graph.size - wy]) + min([wx, graph.size - wx])
                nxgraph.add_edge(num + i0, num + i1 + i0 + 1, weight=-weight)

        num = len(anyons)

    matching = nx.algorithms.matching.max_weight_matching(nxgraph, maxcardinality=True)
    return [[all_anyons[i0], all_anyons[i1]] for i0, i1 in matching]


def get_matching_blossom5(graph):
    '''
    Uses the BlossomV algorithm to get the matchings. A list of combinations of all the anyons and their respective weights are feeded to the blossom5 algorithm. To apply the matchings, we walk from each matching vertex to where their paths meet perpendicualarly, flipping the edges on the way over.
    '''

    edges = []                      # Get all possible edges between the anyons and their weights

    all_anyons = []
    num = 0

    for ertype in range(2):
        anyons = []                     # Get all anyons as MWPM algorithm requires
        for y in range(graph.size):
            for x in range(graph.size):
                vertex = graph.V[(ertype, y, x)]
                if vertex.state:
                    anyons.append(vertex)
        all_anyons += anyons

        for i0, v0 in enumerate(anyons[:-1]):
            (_, y0, x0) = v0.sID
            for i1, v1 in enumerate(anyons[i0 + 1:]):
                (_, y1, x1) = v1.sID
                wy = (y0 - y1) % (graph.size)
                wx = (x0 - x1) % (graph.size)
                weight = min([wy, graph.size - wy]) + min([wx, graph.size - wx])
                edges.append([num + i0, num + i1 + i0 + 1, weight])

        num = len(anyons)

    output = pm.getMatching(len(anyons), edges) if anyons != [] else []
    return [[all_anyons[i0], all_anyons[i1]] for i0, i1 in enumerate(output) if i0 > i1]


def apply_matching_mwpm(graph, matching_pairs, toric_plot=None):

    for v0, v1 in matching_pairs:   # Apply the matchings to the graph

        (_, y0, x0) = v0.sID
        (_, y1, x1) = v1.sID

        dy0 = (y0 - y1) % graph.size  # Get distance between endpoints, take modulo to find min distance
        dx0 = (x0 - x1) % graph.size
        dy1 = (y1 - y0) % graph.size
        dx1 = (x1 - x0) % graph.size

        if dy0 < dy1:               # Find closest path and walking direction
            dy = dy0
            yd = 'u'
        else:
            dy = dy1
            yd = 'd'
        if dx0 < dx1:
            dx = dx0
            xd = 'r'
        else:
            dx = dx1
            xd = 'l'

        ynext = v0                  # walk vertically from v0
        for y in range(dy):
            (ynext, edge) = ynext.neighbors[yd]
            edge.state = not edge.state
            edge.matching = not edge.matching

        xnext = v1                  # walk horizontally from v1
        for x in range(dx):
            (xnext, edge) = xnext.neighbors[xd]
            edge.state = not edge.state
            edge.matching = not edge.matching

    if toric_plot is not None:
        toric_plot.plot_lines(matching_pairs)
        toric_plot.plot_final()


def apply_matching_peeling(graph, toric_plot=None):
    '''
    Uses the Peeling algorithm to get the matchings
    Optionally, edge_data can be inputted here, which is useful in multiple iteration simulations
    '''
    for edge in graph.E.values():
        if edge.matching:
            edge.state = not edge.state

    if toric_plot is not None:
        toric_plot.plot_final()


def logical_error(graph):

    '''
    Finds whether there are any logical errors on the lattice/graph. The logical error is returned as [Xvertical, Xhorizontal, Zvertical, Zhorizontal], where each item represents a homological Loop
    '''
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
