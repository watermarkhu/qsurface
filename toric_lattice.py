import math
import random
import numpy as np
import toric_plot2 as tp
import blossom5.pyMatch as pm
import peeling as pel
import time
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
        if plot_load:
            self.L = tp.lattice_plot(size)
            self.L.plot_lattice()

        self.array = np.ones([2, 2, self.size, self.size])

    def init_erasure(self, pE = 0.05, new_errors=True, write_errors=True, array_file = "error.txt"):

        '''
        :param pE:                      probability of erasure error
        :param new_errors: if true:     new array is generated with errors; if false; previous array is used (txt file)
        :param write_error: if true:    writes the generated array with pauli errors to txt files
        :param array_file:              name for the txt file
        '''

        self.pE = pE
        if new_errors:
            # Generate erasure errors
            self.erasures = np.random.random([2, self.size, self.size])
            self.erasures[:, :, :] = self.erasures[:, :, :] < self.pE


            # Increase error size, make blob
            extra = []
            for y in range(self.size):
                for x in range(self.size):
                    if self.erasures[0, y, x] == 1:
                        extra.append((0, y, (x-1)%self.size))
                        extra.append((0, y, (x+1)%self.size))
                        extra.append((1, y, x))
                        extra.append((1, (y-1)%self.size, x))
                        extra.append((1, y, (x+1)%self.size))
                        extra.append((1, (y-1)%self.size, (x+1)%self.size))
                    if self.erasures[1, y, x] == 1:
                        extra.append((1, (y-1)%self.size, x))
                        extra.append((1, (y+1)%self.size, x))
                        extra.append((0, y, (x-1)%self.size))
                        extra.append((0, y, x))
                        extra.append((0, (y+1)%self.size, (x-1)%self.size))
                        extra.append((0, (y+1)%self.size, x))
            for bound in extra:
                self.erasures[bound] = 1
            # Uniform I, X, Y, Z
            for y in range(self.size):
                for x in range(self.size):
                    for td in range(2):
                        if self.erasures[td, y, x] == 1:
                            rand = random.random()
                            if rand < 0.25:
                                self.erasures[td, y, x] = 2
                            elif rand >= 0.25 and rand < 0.5:
                                self.erasures[td, y, x] = 3
                            elif rand >= 0.5 and rand < 0.75:
                                self.erasures[td, y, x] = 4

            if write_errors:
                np.savetxt("./temp/Erasure_" + array_file, self.erasures.reshape(2 * self.size, self.size), fmt="%d")
        else:
            self.erasures = np.reshape(np.loadtxt("./temp/Erasure_" + array_file), (2, self.size, self.size))

        if self.plot_load:   self.L.plot_erasures(self.erasures)


        # Apply erasure errors to array
        for td in range(2):
            for x in range(self.size):
                for y in range(self.size):
                    if self.erasures[td, y, x] in [2, 4]:
                        self.array[0, td, y, x] = 1 - self.array[0, td, y, x]
                    if self.erasures[td, y, x] in [3, 4]:
                        self.array[1, td, y, x] = 1 - self.array[1, td, y, x]


    def init_pauli(self, pX = 0.1, pZ=0.1, pE=0.05, new_errors=True, write_errors = True, array_file = "error.txt"):

        '''
        :param pX:                      probability of X error
        :param pZ:                      probability of Z error
        :param new_errors: if true:     new array is generated with errors; if false; previous array is used (txt file)
        :param write_error: if true:    writes the generated array with pauli errors to txt files
        :param array_file:              name for the txt file
        '''

        self.pX = pX
        self.pZ = pZ
        if new_errors:

            # Generate X and Z errors or load from previous
            np.random.seed(int((time.time()%100)*10000000))
            self.errors = np.random.random([2,2,self.size, self.size])
            self.errors[0, :, :, :] = self.errors[0, :, :, :] < self.pX
            self.errors[1, :, :, :] = self.errors[1, :, :, :] < self.pZ


            if write_errors:
                np.savetxt("./temp/PauliX_" + array_file, self.errors[0, :, :, :].reshape(2 * self.size, self.size), fmt="%d")
                np.savetxt("./temp/PauliZ_" + array_file, self.errors[1, :, :, :].reshape(2 * self.size, self.size), fmt="%d")
        else:
            X_errors = np.reshape(np.loadtxt("./temp/PauliX_" + array_file), (2, self.size, self.size))
            Z_errors = np.reshape(np.loadtxt("./temp/PauliZ_" + array_file), (2, self.size, self.size))
            self.errors = np.stack((X_errors, Z_errors), axis = 0)

        # Apply pauli errors to array
        self.array = np.mod(self.array + self.errors, 2)

        if self.plot_load: self.L.plot_errors(self.array)


    def measure_stab(self):
        '''
        self.stab is an array that stores the measurement outcomes for the stabilizer measurements
            It has dimension [XZ{0,1}, size, size]
            Measurements outcomes are either 0 or 1, analogous to -1 and 1 states
            The 0 values are the quasiparticles
        '''

        self.stab = np.ones([2, self.size, self.size], dtype=bool)

        # Measure plaquettes and stars
        for er in range (2):
            for y in range(self.size):
                for x in range(self.size):

                    # Get neighboring qubits for stabilizer
                    stab_qubits = [(er, 0, y, x), (er, 1, y, x), (er, er, (y + 1 - 2*er) % self.size, x), (er, 1 - er, y, (x + 1 - 2*er) % self.size)]

                    # Flip value of stabilizer measurement
                    for qubit in stab_qubits:
                        if self.array[qubit] == 0:
                            self.stab[er, y, x] = 1 - self.stab[er, y, x]

        # Number of quasiparticles, syndromes
        # Quasiparticles locations [(y,x),..]
        self.N_qua = []
        self.N_syn = []
        self.qua_loc = []
        for er in range(2):

            qua_loc = [(y, x) for y in range(self.size) for x in range(self.size) if self.stab[er, y, x] == 0]

            self.qua_loc.append(qua_loc)
            self.N_qua.append(len(qua_loc))
            self.N_syn.append(int(len(qua_loc) / 2))

        if self.plot_load:  self.L.plotXstrings(self.qua_loc)

    def get_matching_peeling(self):
        '''
        Uses the Peeling algorithm to get the matchings
        '''

        erloc = [(hv, y, x) for hv in range(2) for y in range(self.size) for x in range(self.size) if self.erasures[hv, y, x] != 0]
        pel.toric(self.size, self.qua_loc, erloc)



    def get_matching_MWPM(self):
        '''
        Uses the MWPM algorithm to get the matchings
        '''

        self.results = []

        for ertype in range(2):

            # edges given to MWPM algorithm [[v0, v1, distance],...]
            edges = []

            # Get all possible strings - connections between the quasiparticles and their weights
            for v0 in range(self.N_qua[ertype] - 1):

                (y0, x0) = self.qua_loc[ertype][v0]

                for v1 in range(self.N_qua[ertype] - v0 - 1):

                    (y1, x1) = self.qua_loc[ertype][v1 + v0 + 1]
                    wy = (y0 - y1) % (self.size)
                    wx = (x0 - x1) % (self.size)
                    weight = min([wy, self.size - wy]) + min([wx, self.size - wx])
                    edges.append([v0, v1 + v0 + 1, weight])

            # Apply BlossomV algorithm if there are quasiparticles
            output = pm.getMatching(self.N_qua[ertype], edges) if self.N_qua[ertype] != 0 else []

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

                # Get distance between endpoints, take modulo to find min distance
                dy = (y1 - y0) % self.size
                dx = (x1 - x0) % self.size

                # Make path from y0 to y1
                if dy < self.size - dy:
                    endy = y1
                    for y in range(dy):
                        flips.append((ertype, ertype, (y0 + y + 1 - ertype) % self.size, x0))

                # Make path from y1 to y0
                else:
                    endy = y0
                    for y in range(self.size - dy):
                        flips.append((ertype, ertype, (y1 + y + 1 - ertype) % self.size, x1))

                # Make path from x0 to x1
                if dx < self.size - dx:
                    for x in range(dx):
                        flips.append((ertype, 1 - ertype, endy, (x0 + x + 1 - ertype) % self.size))

                # Make path from x1 to x0
                else:
                    for x in range(self.size - dx):
                        flips.append((ertype, 1 - ertype, endy, (x1 + x + 1 - ertype) % self.size))

        self.flips = flips

        # Apply flips on qubits
        for flip in flips:
            self.array[flip] = 1 - self.array[flip]


        if self.plot_load: self.L.plot_final(flips, self.array)



    def logical_error(self):

        # logical error in [Xvertical, Xhorizontal, Zvertical, Zhorizontal]
        logical_error = [0, 0, 0, 0]


        # Check number of flips around borders
        for q in range(self.size):
            if self.array[0, 0, 0, q] == 0:
                logical_error[0] = 1 - logical_error[0]
            if self.array[0, 1, q, 0] == 0:
                logical_error[1] = 1 - logical_error[1]
            if self.array[1, 1, self.size - 1, q] == 0:
                logical_error[2] = 1 - logical_error[2]
            if self.array[1, 0, q, self.size - 1] == 0:
                logical_error[3] = 1 - logical_error[3]


        return logical_error


    # def connect_syndrome(self, ertype, S_dis, S_new):
    #     '''
    #     :param ertype:  error type: 0 for X, 1 for Z
    #
    #     param S_dis:   disappearing syndrome endpoint, this 0-valued stabilizer measurement is corrected by another error
    #     param S_con:    the other syndrome endpoint, will be matched to new syndrome endpoint
    #     param M_dis:    the 1-to-last body element of the disappearing syndrome endpoint, this will decide the bend in the syndrome body
    #     param M_con:    the 1-to-last body element of S_con
    #
    #     If len(S_dis) == 1: connects one existing syndrome to a new one
    #     If len(S_dis) == 2: connects two existing syndromes
    #     '''
    #     if len(S_dis) == 2:
    #         S_new = [S_dis[1], S_dis[0]]
    #
    #     ind_dis = []
    #     ind_bas = []
    #     ind_con = []
    #     M_dis = []
    #     S_con = []
    #     M_con = []
    #
    #     for i in range(len(S_dis)):
    #         # Get indices of dis and con
    #         ind_dis += [self.Syn_list.index(S_dis[i])]
    #         ind_bas += [math.floor(ind_dis[i] / 2) * 2]
    #         ind_con += [ind_bas[i] + (1 - ind_dis[i] % 2)]
    #
    #         # M is the closest mate/neighbor of syndrome endpoints. It determines the path orientation
    #         M_dis += [self.Mat_list[ind_dis[i]]]
    #         S_con += [self.Syn_list[ind_con[i]]]
    #         M_con += [self.Mat_list[ind_con[i]]]
    #
    #         if self.plot_load:
    #             # Center, Around this disappearing vertice are two points
    #             #   1. A new vertice
    #             #   2. A old vertice or a syndrome path
    #             Yc = S_dis[i][0]
    #             Xc = S_dis[i][1]
    #
    #             # Get the respective distances of two points
    #             Pall = [M_dis[i][0] - Yc, M_dis[i][1] - Xc, S_new[i][0] - Yc, S_new[i][1] - Xc]
    #             Pt = [-i / abs(i) if abs(i) == self.size - 1 else i for i in Pall]
    #             Pc = [[Pt[0], Pt[1]], [Pt[2], Pt[3]]]
    #
    #             # Define vectors
    #             Wvec = [0, -1]
    #             Evec = [0, 1]
    #             Nvec = [-1, 0]
    #             Svec = [1, 0]
    #
    #             # Find which vectors are present, determine orientation or green path
    #             if Nvec in Pc and Evec in Pc:  # -
    #                 self.body[ertype, Yc, Xc, 2] = 0
    #                 self.body[ertype, Yc, Xc, 1] = 0
    #             elif Nvec in Pc and Wvec in Pc:
    #                 self.body[ertype, Yc, Xc, 2] = 0
    #                 self.body[ertype, Yc, Xc, 0] = 0
    #             elif Svec in Pc and Wvec in Pc:
    #                 self.body[ertype, Yc, Xc, 3] = 0
    #                 self.body[ertype, Yc, Xc, 0] = 0
    #             elif Svec in Pc and Evec in Pc:
    #                 self.body[ertype, Yc, Xc, 3] = 0
    #                 self.body[ertype, Yc, Xc, 1] = 0
    #             elif Nvec in Pc and Svec in Pc:
    #                 self.body[ertype, Yc, Xc, 2] = 0
    #                 self.body[ertype, Yc, Xc, 3] = 0
    #             elif Evec in Pc and Wvec in Pc:
    #                 self.body[ertype, Yc, Xc, 0] = 0
    #                 self.body[ertype, Yc, Xc, 1] = 0
    #             else:
    #                 print("Error no path found")
    #
    #     ind_bas_0 = max(ind_bas)
    #     ind_bas_1 = min(ind_bas)
    #
    #     # Delete previous syndrome
    #     del self.Mat_list[ind_bas_0: ind_bas_0 + 2]
    #     del self.Syn_list[ind_bas_0: ind_bas_0 + 2]
    #
    #     if len(S_dis) == 1:
    #         # Add new extended syndrome
    #         self.Syn_list += [S_con[0], S_new[0]]
    #         self.Mat_list += [M_con[0], S_dis[0]]
    #     else:
    #         # Two syndromes are connected, an extra syndrome needs to be removed, and the new extended syndrome is added
    #         # But only if the syndrome is not closed, as it is then just a stabilizer measurements, and enough actions has been done
    #         if S_dis[0] not in S_con and S_dis[1] not in S_con:
    #             del self.Mat_list[ind_bas_1: ind_bas_1 + 2]
    #             del self.Syn_list[ind_bas_1: ind_bas_1 + 2]
    #             self.Syn_list += S_con
    #             self.Mat_list += M_con
    # def measure_stab_body(self):
    #
    #     '''
    #     :param p_stab:  probability of measurement error [p_stab_X, p_stab_Z]
    #
    #     self.stab is an array that stores the measurement outcomes for the stabilizer measurements
    #         It has dimension [XY{0,1}, size, size]
    #         Measurements outcomes are either 0 or 1, analogous to -1 and 1 states
    #         The 0 values are the quasiparticles
    #
    #     self.body stores the syndrome body information, e.g. the stabilizers for which the value
    #         has been corrected by another error, in syndromes with length > 2.
    #         It has dimension [XY{0,1}, size, size, Wind{0,1,2,3}],
    #         where Wind stands for the direction. For example, on a star operator:
    #
    #               North 2
    #                  |
    #          West 0 - - East 1
    #                  |
    #               South 3
    #     '''
    #
    #     self.stab = np.ones([2, self.size, self.size], dtype=bool)
    #     self.body = np.ones([2, self.size, self.size, 4], dtype=bool)
    #
    #     # Number of quasiparticles, syndromes, and total strings
    #     self.N_qua = []
    #     self.N_syn = []
    #     self.N_str = []
    #
    #     # Quasiparticles locations [(y,x),..] and syndromes info [[v0, v1],..]
    #     self.qua_loc = []
    #     self.syn_inf = []
    #
    #     for ertype in range(2):
    #
    #         if ertype == 0:
    #             erloc = self.X_er_loc
    #         else:
    #             erloc = self.Z_er_loc
    #
    #         # Syn_list is a list of syndromes, each syndrome as two vertices, appended directly after reach other
    #         # Mat_list is the direct mate/neighbor of the two vertices of these syndromes, in the same order
    #         self.Syn_list = []
    #         self.Mat_list = []
    #
    #         for (Y, X, HV) in erloc:
    #
    #             # First quasiparticle is always in the same unit cell
    #             V0 = (Y, X)
    #
    #             # Find Find other quasiparticle, (toric specific)
    #             if (ertype == 0 and HV == 0):  # Z error vertical
    #                 if Y == 0:  # top edge
    #                     V1 = (self.size - 1, X)
    #                 else:
    #                     V1 = (Y - 1, X)
    #             elif (ertype == 0 and HV == 1):  # Z error horizontal
    #                 if X == 0:  # left edge
    #                     V1 = (Y, self.size - 1)
    #                 else:
    #                     V1 = (Y, X - 1)
    #             elif (ertype == 1 and HV == 0):  # X error horizontal
    #                 if X == self.size - 1:  # right edge
    #                     V1 = (Y, 0)
    #                 else:
    #                     V1 = (Y, X + 1)
    #             else:  # X error vertical
    #                 if Y == self.size - 1:  # bottom edge
    #                     V1 = (0, X)
    #                 else:
    #                     V1 = (Y + 1, X)
    #
    #             # If both vertices are not yet in syndrome endpoints, append vertices as a new syndrome
    #             if self.stab[ertype, V0[0], V0[1]] == 1 and self.stab[ertype, V1[0], V1[1]] == 1:
    #                 self.stab[ertype, V0[0], V0[1]] = 0
    #                 self.stab[ertype, V1[0], V1[1]] = 0
    #                 self.Syn_list += [V0, V1]
    #                 self.Mat_list += [V1, V0]
    #
    #             # If one of the vertices is already in a syndrome, apply syndrome algorithm
    #             elif self.stab[ertype, V0[0], V0[1]] == 0 and self.stab[ertype, V1[0], V1[1]] == 1:
    #                 self.stab[ertype, V0[0], V0[1]] = 1
    #                 self.stab[ertype, V1[0], V1[1]] = 0
    #                 S_new = [V1]
    #                 S_dis = [V0]
    #                 self.connect_syndrome(ertype, S_dis, S_new)
    #             elif self.stab[ertype, V0[0], V0[1]] == 1 and self.stab[ertype, V1[0], V1[1]] == 0:
    #                 self.stab[ertype, V0[0], V0[1]] = 0
    #                 self.stab[ertype, V1[0], V1[1]] = 1
    #                 S_new = [V0]
    #                 S_dis = [V1]
    #                 self.connect_syndrome(ertype, S_dis, S_new)
    #             # If both vertices al already in syndromes, apply syndrome algorithm to both
    #             else:
    #                 self.stab[ertype, V0[0], V0[1]] = 1
    #                 self.stab[ertype, V1[0], V1[1]] = 1
    #                 S_new = []
    #                 S_dis = [V0, V1]
    #                 self.connect_syndrome(ertype, S_dis, S_new)
    #
    #         self.N_syn += [int(len(self.Syn_list) / 2)]
    #         self.N_qua += [int(len(self.Syn_list))]
    #         self.N_str += [int(np.sum(range(self.N_qua[ertype])))]
    #
    #         # Save syndromes in [[v0, v1, crossY, crossX]] format
    #         syndromes = []
    #         for syn_i in range(self.N_syn[ertype]):
    #             syndromes.append([int(2 * syn_i), int(2 * syn_i + 1)])
    #
    #         self.qua_loc.append(self.Syn_list)
    #         self.syn_inf.append(syndromes)
    #
    #     if self.plot_load:
    #         self.L.plotXstrings(self.stab, self.qua_loc, self.body)
