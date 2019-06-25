import os
import sys
import time
import datetime
import random
import toric_plot as tp
import blossom5.pyMatch as pm
import peeling as pel
import graph_objects as GO


class lattice:

    def __init__(self, size=10, pauli_file=None, erasure_file=None, plot_load=True, graph=None):

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

        self.plot_load = plot_load

        if not os.path.exists("./errors/"):
            os.makedirs("./errors/")

        # If no input file is given
        if pauli_file is None and erasure_file is None:
            self.size = size
            self.time = time.time()
            self.pauli_file, self.erasure_file = None, None

        # Read time seed, size from input files
        else:
            if pauli_file is not None:
                filename = "./errors/" + pauli_file + ".txt"
                try:
                    self.pauli_file = open(filename, "r")
                except FileNotFoundError:
                    sys.exit("Error file not found")
                firstlines = [next(self.pauli_file) for _ in range(4)]
                self.time = float(firstlines[1][7:])
                self.size = int(firstlines[2][4:])
            if erasure_file is not None:
                filename = "./errors/" + erasure_file + ".txt"
                try:
                    self.erasure_file = open(filename, "r")
                except FileNotFoundError:
                    sys.exit("Error file not found")
                firstlines = [next(self.erasure_file) for _ in range(4)]
                self.time = float(firstlines[1][7:])
                self.size = int(firstlines[2][4:])

        random.seed(self.time)

        if graph is None:

            self.G = GO.Graph(None, None, None)

            # Add vertices and edges to graph
            for ertype in range(2):
                for y in range(self.size):
                    for x in range(self.size):
                        self.G.add_vertex((ertype, y, x))
            for ertype in range(2):
                for y in range(self.size):
                    for x in range(self.size):
                        for td in range(2):
                            qID = (ertype, y, x, td)
                            if ertype == 0 and td == 0:
                                VL_sID = (ertype, y, x)
                                VR_sID = (ertype, y, (x + 1) % self.size)
                                self.G.add_edge(qID, VL_sID, VR_sID, 'H')
                            elif ertype == 1 and td == 1:
                                VL_sID = (ertype, y, (x - 1) % self.size)
                                VR_sID = (ertype, y, x)
                                self.G.add_edge(qID, VL_sID, VR_sID, 'H')
                            elif ertype == 0 and td == 1:
                                VU_sID = (ertype, y, x)
                                VD_sID = (ertype, (y + 1) % self.size, x)
                                self.G.add_edge(qID, VU_sID, VD_sID, 'V')
                            elif ertype == 1 and td == 0:
                                VU_sID = (ertype, (y - 1) % self.size, x)
                                VD_sID = (ertype, y, x)
                                self.G.add_edge(qID, VU_sID, VD_sID, 'V')
        else:
            self.G = graph

        # Plot the lattice
        if self.plot_load:
            self.LP = tp.lattice_plot(self.size, self.G)
            self.LP.plot_lattice()

    def init_erasure_errors_region(self, pE=0, savefile=False):
        '''
        :param pE           probability of an erasure error
        :param savefile     toggle to save the errors to a file

        Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error. This function is the same as init_erasure_errors, except that for every erasure, its (6) neighbor edges are also initated as an erasure. The error rate is therefore higher than pE.
        '''

        if self.erasure_file is None:

            # Loop over all qubits
            for y in range(self.size):
                for td in range(2):
                    for x in range(self.size):

                        # Save erasure state if pE > 0
                        if pE != 0 and random.random() < pE:

                            region = {(y, x, td)}

                            vertices = self.G.E[(0, y, x, td)].vertices
                            for vertex in vertices:
                                for wind in self.G.wind:
                                    (n_vertex, edge) = vertex.neighbors[wind]
                                    (type, y, x, td) = edge.qID
                                    region.add((y, x, td))

                            for (y, x, td) in region:
                                self.G.E[(0, y, x, td)].erasure = True
                                self.G.E[(1, y, x, td)].erasure = True
                                rand = random.random()
                                if rand < 0.25:
                                    self.G.E[(0, y, x, td)].state = not self.G.E[(0, y, x, td)].state
                                elif rand >= 0.25 and rand < 0.5:
                                    self.G.E[(1, y, x, td)].state = not self.G.E[(1, y, x, td)].state
                                elif rand >= 0.5 and rand < 0.75:
                                    self.G.E[(0, y, x, td)].state = not self.G.E[(0, y, x, td)].state
                                    self.G.E[(1, y, x, td)].state = not self.G.E[(1, y, x, td)].state

            if savefile:
                st = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d_%H-%M-%S')
                st2 = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H-%M-%S')
                name = "./errors/" + st + "_erasure.txt"
                f = open(name, "w")
                f.write("Erasure error file created on " + st2 + "\n")
                f.write("Seed = " + str(self.time) + "\n")
                f.write("L = " + str(self.size) + "\n\n")
                e_file = "pE = " + str(pE) + "\n"

                for y in range(self.size):
                    for td in range(2):
                        if td == 0:
                            e_file += "  "
                        for x in range(self.size):
                            if self.G.E[(0, y, x, td)].erasure:
                                Xstate = self.G.E[(0, y, x, td)].state
                                Zstate = self.G.E[(1, y, x, td)].state
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
            self.read_erasure_errors()

        if self.plot_load:
            self.LP.plot_erasures()

    def init_erasure_errors(self, pE=0, savefile=False):
        '''
        :param pE           probability of an erasure error
        :param savefile     toggle to save the errors to a file

        Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
        '''
        if self.erasure_file is None:

            # Write first lines of error file
            if savefile:
                st = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d_%H-%M-%S')
                st2 = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H-%M-%S')
                name = "./errors/" + st + "_erasure.txt"
                f = open(name, "w")
                f.write("Erasure error file created on " + st2 + "\n")
                f.write("Seed = " + str(self.time) + "\n")
                f.write("L = " + str(self.size) + "\n\n")
                e_file = "pE = " + str(pE) + "\n"

            # Loop over all qubits
            for y in range(self.size):
                for td in range(2):

                    if savefile and td == 0:
                        e_file += "  "

                    for x in range(self.size):

                        # Save erasure state if pE > 0
                        if pE != 0 and random.random() < pE:

                            self.G.E[(0, y, x, td)].erasure = True
                            self.G.E[(1, y, x, td)].erasure = True

                            # Apply random X or Z error on erasure
                            rand = random.random()
                            if rand < 0.25:
                                self.G.E[(0, y, x, td)].state = not self.G.E[(0, y, x, td)].state
                                e_state = 2
                            elif rand >= 0.25 and rand < 0.5:
                                self.G.E[(1, y, x, td)].state = not self.G.E[(1, y, x, td)].state
                                e_state = 3
                            elif rand >= 0.5 and rand < 0.75:
                                self.G.E[(0, y, x, td)].state = not self.G.E[(0, y, x, td)].state
                                self.G.E[(1, y, x, td)].state = not self.G.E[(1, y, x, td)].state
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
            self.read_erasure_errors()

        if self.plot_load:
            self.LP.plot_erasures()


    def init_pauli_errors(self, pX=0, pZ=0, savefile=False):
        '''
        :param pX           probability of a Pauli X error
        :param pZ           probability of a Pauli Z error
        :param savefile     toggle to save the errors to a file

        initates Pauli X and Z errors on the lattice based on the error rates
        '''

        if self.pauli_file is None:

            # Write first lines of error file
            if savefile:
                st = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d_%H-%M-%S')
                st2 = datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H-%M-%S')
                name = "./errors/" + st + "_pauli.txt"
                f = open(name, "w")
                f.write("Pauli error file created on " + st2 + "\n")
                f.write("Seed = " + str(self.time) + "\n")
                f.write("L = " + str(self.size) + "\n\n")
                x_file = "pX = " + str(pX) + "\n"
                z_file = "pZ = " + str(pZ) + "\n"

            # Loop over all qubits
            for y in range(self.size):
                for td in range(2):
                    if savefile and td == 0:
                        x_file += "  "
                        z_file += "  "

                    for x in range(self.size):

                        # Apply X error if chance > 0
                        if pX != 0:
                            if random.random() < pX:
                                self.G.E[(0, y, x, td)].state = not self.G.E[(0, y, x, td)].state
                                x_state = 1
                            else:
                                x_state = 0
                        else:
                            x_state = 0

                        # Apply Z error if chance > 0
                        if pZ != 0:
                            if random.random() < pZ:
                                self.G.E[(1, y, x, td)].state = not self.G.E[(1, y, x, td)].state
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
            self.read_pauli_errors()

        if self.plot_load:
            self.LP.plot_erasures()
            self.LP.plot_errors()


    def read_erasure_errors(self):
        '''
        Reads the erasure errors from the erasure file.
        '''

        self.pE = float(next(self.erasure_file)[5:])

        for linenum in range(self.size*2):
            line = next(self.erasure_file)
            y = linenum // 2
            td = linenum % 2
            for x in range(self.size):
                if td == 0:
                    state = int(line[2 + x*4])
                else:
                    state = int(line[x*4])
                if state != 0:
                    self.G.E[(0, y, x, td)].erasure = True
                    self.G.E[(1, y, x, td)].erasure = True
                    if state == 2:
                        self.G.E[(0, y, x, td)].state = not self.G.E[(0, y, x, td)].state
                    elif state == 3:
                        self.G.E[(1, y, x, td)].state = not self.G.E[(1, y, x, td)].state
                    elif state == 4:
                        self.G.E[(0, y, x, td)].state = not self.G.E[(0, y, x, td)].state
                        self.G.E[(1, y, x, td)].state = not self.G.E[(1, y, x, td)].state


    def read_pauli_errors(self):
        '''
        Reads the pauli errors from the pauli file


        '''
        self.pX = float(next(self.pauli_file)[5:])

        for linenum in range(self.size*2):
            line = next(self.pauli_file)
            y = linenum // 2
            td = linenum % 2
            for x in range(self.size):
                if td == 0:
                    state = int(line[2 + x*4])
                else:
                    state = int(line[x*4])
                if state == 1:
                    self.G.E[(0, y, x, td)].state = not self.G.E[(0, y, x, td)].state

        line = next(self.pauli_file)
        self.pZ = float(next(self.pauli_file)[5:])

        for linenum in range(self.size*2):
            line = next(self.pauli_file)
            y = linenum // 2
            td = linenum % 2
            for x in range(self.size):
                if td == 0:
                    state = int(line[2 + x*4])
                else:
                    state = int(line[x*4])
                if state == 1:
                    self.G.E[(1, y, x, td)].state = not self.G.E[(1, y, x, td)].state


    '''
    Main functions
    '''

    def measure_stab(self):
        '''
        self.stab is an array that stores the measurement outcomes for the stabilizer measurements
            It has dimension [XZ{0,1}, size, size]
            Measurements outcomes are either 0 or 1, analogous to -1 and 1 states
            The 0 values are the quasiparticles
        '''

        directions = ["u", "d", "l", "r"]
        for vertex in self.G.V.values():
            for dir in directions:
                if dir in vertex.neighbors:
                    if vertex.neighbors[dir][1].state:
                        vertex.state = not vertex.state

        if self.plot_load:
            self.LP.plot_anyons()

    def get_matching_peeling(self):
        '''
        Uses the Peeling algorithm to get the matchings
        Optionally, edge_data can be inputted here, which is useful in multiple iteration simulations
        '''

        PL = pel.toric(self)
        PL.find_clusters()
        PL.grow_clusters()
        PL.init_trees()
        PL.peel_trees()

        for edge in self.G.E.values():
            if edge.matching:
                edge.state = not edge.state

        if self.plot_load:
            self.LP.plot_final()

    def get_matching_MWPM(self):
        '''
        Uses the MWPM algorithm to get the matchings
        A list of combinations of all the anyons and their respective weights are feeded to the blossom5 algorithm
        '''
        all_matchings = []

        for ertype in range(2):

            anyons = []

            for y in range(self.size):
                for x in range(self.size):
                    vertex = self.G.V[(ertype, y, x)]
                    if vertex.state:
                        anyons.append(vertex)

            edges = []

            # Get all possible strings - connections between the quasiparticles and their weights
            for i0, v0 in enumerate(anyons[:-1]):

                (_, y0, x0) = v0.sID

                for i1, v1 in enumerate(anyons[i0 + 1:]):

                    (_, y1, x1) = v1.sID
                    wy = (y0 - y1) % (self.size)
                    wx = (x0 - x1) % (self.size)
                    weight = min([wy, self.size - wy]) + min([wx, self.size - wx])
                    edges.append([i0, i1 + i0 + 1, weight])

            # Apply BlossomV algorithm if there are quasiparticles
            output = pm.getMatching(len(anyons), edges) if anyons != [] else []

            # Save results to same format as self.syn_inf
            matching_pairs = [[anyons[i0], anyons[i1]] for i0, i1 in enumerate(output) if i0 > i1]
            all_matchings.append(matching_pairs)

            '''
            Finds the qubits that needs to be flipped in order to correct the errors
            '''

            for v0, v1 in matching_pairs:

                (_, y0, x0) = v0.sID
                (_, y1, x1) = v1.sID

                # Get distance between endpoints, take modulo to find min distance
                dy0 = (y0 - y1) % self.size
                dx0 = (x0 - x1) % self.size
                dy1 = (y1 - y0) % self.size
                dx1 = (x1 - x0) % self.size

                if dy0 < dy1:
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

                ynext = v0
                for y in range(dy):
                    (ynext, edge) = ynext.neighbors[yd]
                    edge.state = not edge.state
                    edge.matching = not edge.matching

                xnext = v1
                for x in range(dx):
                    (xnext, edge) = xnext.neighbors[xd]
                    edge.state = not edge.state
                    edge.matching = not edge.matching

        if self.plot_load:
            self.LP.plot_lines(all_matchings)
            self.LP.plot_final()

    def logical_error(self):

        # logical error in [Xvertical, Xhorizontal, Zvertical, Zhorizontal]
        logical_error = [False, False, False, False]

        for i in range(self.size):
            if self.G.E[(0, i, 0, 0)]:
                logical_error[0] = not logical_error[0]
            if self.G.E[(0, 0, i, 1)]:
                logical_error[1] = not logical_error[1]
            if self.G.E[(0, i, 0, 1)]:
                logical_error[2] = not logical_error[2]
            if self.G.E[(0, 0, i, 0)]:
                logical_error[3] = not logical_error[3]

        return logical_error
