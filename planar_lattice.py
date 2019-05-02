import math
import numpy as np
import planar_plot as pp
import blossom_cpp as bl
import blossom5.pyMatch as pm
import time
import copy
from matplotlib import pyplot as plt


class lattice:

    def __init__(self, size = 10, plot_load = True):

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
        self.size = size
        self.plot_load = plot_load

        # Initiate plot
        if plot_load:   self.L = pp.plotlattice(size)

        self.array = np.ones([2, 2, self.size, self.size])



    def init_errors(self, pX = 0.1, pZ=0.1, new_errors=True, write_error = True, array_file = "array.txt"):

        '''
        :param pX:                      probability of X error
        :param pZ:                      probability of Z error
        :param new_errors: if true:     new array is generated with errors; if false; previous array is used (txt file)
        :param write_error: if true:    writes the generated array with pauli errors to txt files
        :param array_file:              name for the txt file
        '''

        self.pX = pX
        self.pZ = pZ

        # Generate X and Z errors or load from previous
        if new_errors:
            np.random.seed(int((time.time()%100)*10000000))
            self.errors = np.random.random([2,2,self.size, self.size])
            self.errors[0, :, :, :] = self.errors[0, :, :, :] < self.pX
            self.errors[1, :, :, :] = self.errors[1, :, :, :] < self.pZ
            if write_error:
                np.savetxt("./temp/X_" + array_file, self.errors[0, :, :, :].reshape(2 * self.size, self.size), fmt="%d")
                np.savetxt("./temp/Z_" + array_file, self.errors[1, :, :, :].reshape(2 * self.size, self.size), fmt="%d")
        else:
            X_errors = np.reshape(np.loadtxt("./temp/X_" + array_file), (2, self.size, self.size))
            Z_errors = np.reshape(np.loadtxt("./temp/Z_" + array_file), (2, self.size, self.size))
            self.errors = np.stack((X_errors, Z_errors), axis = 0)

        # Apply errors to array
        self.array = np.mod(self.array + self.errors, 2)

        # Save array locations that are not qubits
        non_bits = [(er, 1, y, 0) for y in range(self.size) for er in range(2)] + [(er, 1, self.size-1, x+1) for x in range(self.size - 1) for er in range(2)]

        for non_bit in non_bits:
            self.array[non_bit] = 2


        # Save locations for errors (y, x, TD{0,1}) for X, Z, and Y (X and Z) errors
        self.X_er_loc = []
        self.Z_er_loc = []
        self.Y_er_loc = []
        for iy in range(self.size):
            for ix in range(self.size):
                for hv in range(2):
                    if self.array[0,hv,iy,ix] == 0: self.X_er_loc.append((iy,ix,hv))
                    if self.array[1,hv,iy,ix] == 0: self.Z_er_loc.append((iy,ix,hv))

                    if self.plot_load:
                        if self.array[0,hv,iy,ix] == 0 and self.array[1,hv,iy,ix] == 0:
                            self.Y_er_loc.append((iy, ix, hv))

        if self.plot_load:
            self.L.plot_errors(self.X_er_loc, self.Z_er_loc, self. Y_er_loc)

    def measure_stab(self):
        '''
        self.stab is an array that stores the measurement outcomes for the stabilizer measurements
            It has dimension [XZ{0,1}, size, size]
            Measurements outcomes are either 0 or 1, analogous to -1 and 1 states
            The 0 values are the quasiparticles
        '''

        self.plaq = np.ones([self.size - 1, self.size], dtype=bool)
        self.star = np.ones([self.size, self.size - 1], dtype=bool)

        # Measure plaquettes
        for y in range(self.size-1):
            for x in range(self.size):
                # Get neighboring qubits for stabilizer
                if x not in [0, self.size -1]:
                    plaq_qubits = [(0, 0, y, x), (0, 1, y, x), (0, 0, y + 1, x), (0, 1, y,x + 1)]
                elif x == 0:
                    plaq_qubits = [(0, 0, y, x), (0, 0, y + 1, x), (0, 1, y, x + 1)]
                else:
                    plaq_qubits = [(0, 0, y, x), (0, 1, y, x), (0, 0, y + 1, x)]

                # Flip value of stabilizer measurement
                for qubit in plaq_qubits:
                    if self.array[qubit] == 0:
                        self.plaq[y, x] = 1 - self.plaq[y, x]

        # Measure stars
        for y in range(self.size):
            for x1 in range(self.size - 1):

                x = x1 + 1
                # Get neighboring qubits for stabilizer
                if y not in [0, self.size -1]:
                    star_qubits = [(1, 0, y, x), (1, 1, y, x), (1, 1, y - 1, x), (1, 0, y, x - 1)]
                elif y == 0:
                    star_qubits = [(1, 0, y, x), (1, 1, y, x), (1, 0, y, x - 1)]
                else:
                    star_qubits = [(1, 0, y, x), (1, 1, y - 1, x), (1, 0, y, x - 1)]

                # Flip value of stabilizer measurement
                for qubit in star_qubits:
                    if self.array[qubit] == 0:
                        self.star[y, x1] = 1 - self.star[y, x1]

        # Number of quasiparticles, syndromes, and total strings
        # Quasiparticles locations [(y,x),..]


        self.qua_loc =  [[(y, x) for y in range(self.size - 1) for x in range(self.size) if self.plaq[y, x] == 0]]
        self.qua_loc += [[(y, x) for y in range(self.size) for x in range(self.size - 1) if self.star[y, x] == 0]]
        self.N_qua = [len(qua) for qua in self.qua_loc]
        self.N_syn = [int(len(qua))/2 for qua in self.qua_loc]

        if self.plot_load:  self.L.plotXstrings(self.qua_loc)

    def get_matching(self):
        '''
        Uses the MWPM algorithm to get the matchings
        '''

        self.results = []

        for ertype in range(2):

            qua_loc_m = []

            # edges given to MWPM algorithm [[v0, v1, distance],...]
            edges = []

            # Get all possible strings - connections between the quasiparticles and their weights
            for v0 in range(self.N_qua[ertype]):

                (y0, x0) = self.qua_loc[ertype][v0]

                for v1 in range(self.N_qua[ertype] - v0 - 1):

                    (y1, x1) = self.qua_loc[ertype][v1 + v0 + 1]
                    wy = abs(y0 - y1)
                    wx = abs(x0 - x1)
                    weight = wy + wx
                    edges.append([v0, v1 + v0 + 1, weight])


            for loci in range(self.N_qua[ertype]):

                loc = self.qua_loc[ertype][loci]
                locm = list(copy.copy(loc))

                yx = loc[ertype]

                if yx + 1 <= self.size - yx:
                    weight = yx + 1
                    locm[ertype] = -1
                else:
                    weight = self.size - yx -1
                    locm[ertype] = self.size - 1

                qua_loc_m.append(tuple(locm))
                edges.append([loci, self.N_qua[ertype] + loci, weight])

            for v0 in range(self.N_qua[ertype]):
                for v1 in range(self.N_qua[ertype] - v0 - 1):
                    edges.append([self.N_qua[ertype] + v0, self.N_qua[ertype] + v1 + v0 + 1, 0])



            self.qua_loc[ertype] += qua_loc_m


            # Apply BlossomV algorithm if there are quasiparticles
            output = pm.getMatching(self.N_qua[ertype]*2, edges) if self.N_qua[ertype] != 0 else []

            # Save results to same format as self.syn_inf
            matching_pairs=[[i,output[i]] for i in range(self.N_qua[ertype]) if output[i]>i]
            result = [] if len(matching_pairs) == 0 else [[self.qua_loc[ertype][i] for i in x] for x in matching_pairs]
            self.results.append(result)

        if self.plot_load: self.L.drawlines(self.results)


    def apply_matching(self):

        '''
        Finds the qubits that needs to be flipped in order to correct the errors
        '''
        flips = []
        for ertype in range(2):
            for pair in self.results[ertype]:

                [y0, x0] = pair[0]
                [y1, x1] = pair[1]

                dy = abs(y0 - y1)
                dx = abs(x0 - x1)

                sy = min([y0, y1])
                sx = min([x0, x1])
                my = max([y0, y1])
                mx = max([x0, x1])

                for x in range(dx):
                    newx = sx + x + 1
                    newy = sy
                    if not all([ertype == 0, newx in [0, self.size]]):
                        flips.append((ertype, 1 - ertype, newy, newx))

                for y in range(dy):
                    newx = mx + ertype
                    newy = sy + y + 1 - ertype
                    if not all([ertype == 1, newy in [-1, self.size - 1]]):
                        flips.append((ertype, ertype, newy, newx))


        self.flips = flips
        # Apply flips on qubits
        for flip in flips:
            self.array[flip] = 1 - self.array[flip]



    def logical_error(self):

        # logical error in [Xhorizontal, Zvertical]
        logical_error = [0, 0]


        # Check number of flips around borders
        for q in range(self.size):
            if self.array[0, 0, 0, q] == 0:
                logical_error[0] = 1 - logical_error[0]
            if self.array[0, 1, q, 0] == 0:
                logical_error[1] = 1 - logical_error[1]


        return logical_error

    def plot_corrected(self):
        '''
        Plots the flipped correction-qubits over the inital lattice
        '''

        if self.plot_load:

            singles = []
            poly    = []
            for flip in self.flips:
                count = self.flips.count(flip)
                if count == 1:
                    singles.append(flip)
                elif count % 2 == 1 and flip not in poly:
                    singles.append(flip)
                    poly.append(flip)

            X_er_loc = []
            Z_er_loc = []
            Y_er_loc = []
            for flip in singles:
                plot = (flip[2], flip[3], flip[1])
                if flip[0] == 0 and plot not in Z_er_loc:
                    X_er_loc.append(plot)
                elif flip[0] == 1 and plot not in X_er_loc:
                    Z_er_loc.append(plot)
                else:
                    Y_er_loc.append(plot)

            self.L.plot_errors(X_er_loc, Z_er_loc, Y_er_loc, plot = "matching")
        else:
            print("Plot initially not loaded, nothing can be plotted")
