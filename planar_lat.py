import os
import csv
import math
import random
import planar_plot2 as pp
import blossom_cpp as bl
import blossom5.pyMatch as pm
import copy
from matplotlib import pyplot as plt


# TODO: add erasure code


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
        if plot_load:
            self.L = pp.lattice_plot(size)
            self.L.plot_lattice()

        self.array = [[[[True for _ in range(self.size)] for _ in range(self.size)] for _ in range(2)] for _ in range(2)]

        if not os.path.exists("./errors/"):
            os.makedirs("./errors/")

    def init_stab_data(self):
        '''
        Initializes a multidimentional tuple containing the qubit locations for each stabilizers
        This is especially handy when dealing with multiple iterations, such that the qubit locations needs not to be
            calculated for each round of stabilizer measurements
        Each stabilizer has the tuple (errortype, num_qubits, (td, y, x), ...)

        '''
        plaq_list = []
        star_list = []

        # Measure plaquettes
        for y in range(self.size - 1):
            for x in range(self.size):
                # Get neighboring qubits for stabilizer
                if x not in [0, self.size - 1]:
                    plaq_list.append(((0, y, x), (1, y, x), (0, y + 1, x), (1, y,x + 1)))
                elif x == 0:
                    plaq_list.append(((0, y, x), (0, y + 1, x), (1, y, x + 1)))
                else:
                    plaq_list.append(((0, y, x), (1, y, x), (0, y + 1, x)))

        # Measure stars
        for y in range(self.size):
            for x1 in range(self.size - 1):
                x = x1 + 1
                # Get neighboring qubits for stabilizer
                if y not in [0, self.size - 1]:
                    star_list.append(((0, y, x), (1, y, x), (1, y - 1, x), (0, y, x - 1)))
                elif y == 0:
                    star_list.append(((0, y, x), (1, y, x), (0, y, x - 1)))
                else:
                    star_list.append(((0, y, x), (1, y - 1, x), (0, y, x - 1)))

        self.plaq_data = tuple(plaq_list)
        self.star_data = tuple(star_list)
        return (self.plaq_data, self.star_data)


    def write_error(self, array, file_name):
        '''
        :param array        2D list of L x L new_errors
        :param file_name    name of the file to write to
        Writes the error list to a csv file to check for the errors
        '''
        a1 = array[0]
        a2 = array[1]
        write_array = a1 + a2
        with open(file_name, "w") as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(write_array)
        csvFile.close()

    def read_error(self, file_name):
        '''
        :param file_name    name of the file to read
        Reads the csv file to load errors made in a previous round or made manually
        '''
        with open(file_name, "r") as csvFile:
            read_array = [list(map(bool,rec)) for rec in csv.reader(csvFile)]
        csvFile.close()
        a1 = read_array[:self.size]
        a2 = read_array[self.size:]
        array = [a1, a2]
        return array

    def init_pauli(self, pX = 0.1, pZ=0.1, new_errors=True, write_errors = True, array_file = "error.txt"):

        '''
        :param pX:                      probability of X error
        :param pZ:                      probability of Z error
        :param new_errors: if true:     new array is generated with errors; if false; previous array is used (txt file)
        :param write_error: if true:    writes the generated array with pauli errors to txt files
        :param array_file:              name for the txt file
        '''

        self.pX = pX
        self.pZ = pZ
        X_name = "./errors/L" + str(self.size) + "_X_pauli_error.csv"
        Z_name = "./errors/L" + str(self.size) + "_Z_pauli_error.csv"

        if new_errors:

            # Generate X and Z errors or load from previous
            eX = [[[1 if random.random() < self.pX else 0 for x in range(self.size)] for y in range(self.size)] for td in range(2)]
            eZ = [[[1 if random.random() < self.pZ else 0 for x in range(self.size)] for y in range(self.size)] for td in range(2)]

            if write_errors:
                self.write_error(eX, X_name)
                self.write_error(eZ, Z_name)
        else:
            eX = self.read_error(X_name)
            eZ = self.read_error(Z_name)

        # Apply pauli errors to array
        for y in range(self.size):
            for x in range(self.size):
                for td in range(2):
                    if eX[td][y][x] == 1:
                        self.array[0][td][y][x] = not self.array[0][td][y][x]
                    if eZ[td][y][x] == 1:
                        self.array[1][td][y][x] = not self.array[0][td][y][x]

        if self.plot_load: self.L.plot_errors(self.array)

    def measure_stab(self, star_data = [], plaq_data = []):
        '''
        self.stab is an array that stores the measurement outcomes for the stabilizer measurements
            It has dimension [XZ{0,1}, size, size]
            Measurements outcomes are either 0 or 1, analogous to -1 and 1 states
            The 0 values are the quasiparticles
        '''
        # if not stab_data not inputted, used self data. This is the case for single simulations
        if plaq_data == []: plaq_data = self.plaq_data
        if star_data == []: star_data = self.star_data


        plaq = [[True for _ in range(self.size)] for _ in range(self.size - 1)]
        star = [[True for _ in range(self.size - 1)] for _ in range(self.size)]

        # Measure plaquettes
        for plaq_qubits in plaq_data:
            y = plaq_qubits[0][1]
            x = plaq_qubits[0][2]

            # Flip value of stabilizer measurement
            for (tds, ys, xs) in plaq_qubits:
                if self.array[0][tds][ys][xs] == False:
                    plaq[y][x] = not plaq[y][x]

        # Measure stars
        for star_qubits in star_data:
            y = star_qubits[0][1]
            x = star_qubits[0][2]

            # Flip value of stabilizer measurement
            for (tds, ys, xs) in star_qubits:
                if self.array[1][tds][ys][xs] == False:
                    star[y][x] = not star[y][x]


        # Number of quasiparticles, syndromes, and total strings
        # Quasiparticles locations [(y,x),..]
        plaq_qua_loc = [(y, x) for y in range(self.size - 1) for x in range(self.size) if plaq[y][x] == False]
        star_qua_loc = [(y, x) for y in range(self.size) for x in range(self.size - 1) if star[y][x] == False]
        self.qua_loc = [plaq_qua_loc, star_qua_loc]
        self.N_qua = tuple([len(qua) for qua in self.qua_loc])
        self.N_syn = tuple([int(len(qua))/2 for qua in self.qua_loc])

        if self.plot_load:  self.L.plot_anyons(self.qua_loc)

    def get_matching_MWPM(self):
        '''
        Uses the MWPM algorithm to get the matchings
        A list of combinations of all the anyons and their respective weights are feeded to the blossom5 algorithm
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

            # Get all strings between mirror anyons
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
            self.qua_loc[ertype] = tuple(self.qua_loc[ertype])

            # Apply BlossomV algorithm if there are quasiparticles
            output = pm.getMatching(self.N_qua[ertype]*2, edges) if self.N_qua[ertype] != 0 else []

            # Save results to same format as self.syn_inf
            matching_pairs=[[i,output[i]] for i in range(self.N_qua[ertype]) if output[i]>i]
            result = [] if len(matching_pairs) == 0 else [[self.qua_loc[ertype][i] for i in x] for x in matching_pairs]
            self.results.append(result)

        if self.plot_load: self.L.plot_lines(self.results)


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

                mx = [x0, x1][[y0, y1].index(max([y0, y1]))]

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
        for (ertype, td, y, x) in flips:
            self.array[ertype][td][y][x] = not self.array[ertype][td][y][x]

        if self.plot_load: self.L.plot_final(flips, self.array)



    def logical_error(self):

        # logical error in [Xhorizontal, Zvertical]
        logical_error = [False, False]


        # Check number of flips around borders
        for q in range(self.size):
            if self.array[0][0][0][q] == 0:
                logical_error[0] = not logical_error[0]
            if self.array[1][0][q][0] == 0:
                logical_error[1] = not logical_error[1]


        return logical_error
