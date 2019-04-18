import math
import numpy as np
import Toric_plot as tp
import blossom_cpp as bl
import blossom5.pyMatch as pm
from matplotlib import pyplot as plt


class toric_lattice:

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

        if plot_load:
            self.L = tp.plotlattice(size)

        self.array = np.ones([2, 2, self.size, self.size])

    def init_errors(self, pX = 0.1, pZ=0.1,  new_errors=True, write_error = True, array_file = "array.txt"):

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

        # Save locations for errors (y, x, TD{0,1}) for X, Z, and Y (X and Z) errors
        self.X_er_loc = []
        self.Z_er_loc = []
        self.Y_er_loc = []
        for iy in range(self.size):
            for ix in range(self.size):
                for hv in range(2):
                    if self.array[0,hv,iy,ix] == 0:
                        self.X_er_loc.append((iy,ix,hv))
                    if self.array[1,hv,iy,ix] == 0:
                        self.Z_er_loc.append((iy,ix,hv))

                    if self.plot_load:
                        if self.array[0,hv,iy,ix] == 0 and self.array[1,hv,iy,ix] == 0:
                            self.Y_er_loc.append((iy, ix, hv))

        if self.plot_load:
            self.L.plot_errors(self.X_er_loc, self.Z_er_loc, self. Y_er_loc)


    def connect_syndrome(self, ertype, S_dis, S_new):
        '''
        :param ertype:  error type: 0 for X, 1 for Z

        param S_dis:   disappearing syndrome endpoint, this 0-valued stabilizer measurement is corrected by another error
        param S_con:    the other syndrome endpoint, will be matched to new syndrome endpoint
        param M_dis:    the 1-to-last body element of the disappearing syndrome endpoint, this will decide the bend in the syndrome body
        param M_con:    the 1-to-last body element of S_con

        If len(S_dis) == 1: connects one existing syndrome to a new one
        If len(S_dis) == 2: connects two existing syndromes
        '''
        if len(S_dis) == 2:
            S_new = [S_dis[1], S_dis[0]]

        ind_dis = []
        ind_bas = []
        ind_con = []
        M_dis = []
        S_con = []
        M_con = []

        for i in range(len(S_dis)):
            # Get indices of dis and con
            ind_dis += [self.Syn_list.index(S_dis[i])]
            ind_bas += [math.floor(ind_dis[i] / 2) * 2]
            ind_con += [ind_bas[i] + (1 - ind_dis[i] % 2)]

            # M is the closest mate/neighbor of syndrome endpoints. It determines the path orientation
            M_dis += [self.Mat_list[ind_dis[i]]]
            S_con += [self.Syn_list[ind_con[i]]]
            M_con += [self.Mat_list[ind_con[i]]]

            if self.plot_load:
                # Center, Around this disappearing vertice are two points
                #   1. A new vertice
                #   2. A old vertice or a syndrome path
                Yc = S_dis[i][0]
                Xc = S_dis[i][1]

                # Get the respective distances of two points
                Pall = [M_dis[i][0] - Yc, M_dis[i][1] - Xc, S_new[i][0] - Yc, S_new[i][1] - Xc]
                Pt = [-i / abs(i) if abs(i) == self.size - 1 else i for i in Pall]
                Pc = [[Pt[0], Pt[1]], [Pt[2], Pt[3]]]

                # Define vectors
                Wvec = [0, -1]
                Evec = [0, 1]
                Nvec = [-1, 0]
                Svec = [1, 0]

                # Find which vectors are present, determine orientation or green path
                if Nvec in Pc and Evec in Pc:  # -
                    self.body[ertype, Yc, Xc, 2] = 0
                    self.body[ertype, Yc, Xc, 1] = 0
                elif Nvec in Pc and Wvec in Pc:
                    self.body[ertype, Yc, Xc, 2] = 0
                    self.body[ertype, Yc, Xc, 0] = 0
                elif Svec in Pc and Wvec in Pc:
                    self.body[ertype, Yc, Xc, 3] = 0
                    self.body[ertype, Yc, Xc, 0] = 0
                elif Svec in Pc and Evec in Pc:
                    self.body[ertype, Yc, Xc, 3] = 0
                    self.body[ertype, Yc, Xc, 1] = 0
                elif Nvec in Pc and Svec in Pc:
                    self.body[ertype, Yc, Xc, 2] = 0
                    self.body[ertype, Yc, Xc, 3] = 0
                elif Evec in Pc and Wvec in Pc:
                    self.body[ertype, Yc, Xc, 0] = 0
                    self.body[ertype, Yc, Xc, 1] = 0
                else:
                    print("Error no path found")

        ind_bas_0 = max(ind_bas)
        ind_bas_1 = min(ind_bas)

        # Delete previous syndrome
        del self.Mat_list[ind_bas_0: ind_bas_0 + 2]
        del self.Syn_list[ind_bas_0: ind_bas_0 + 2]

        if len(S_dis) == 1:
            # Add new extended syndrome
            self.Syn_list += [S_con[0], S_new[0]]
            self.Mat_list += [M_con[0], S_dis[0]]
        else:
            # Two syndromes are connected, an extra syndrome needs to be removed, and the new extended syndrome is added
            # But only if the syndrome is not closed, as it is then just a stabilizer measurements, and enough actions has been done
            if S_dis[0] not in S_con and S_dis[1] not in S_con:
                del self.Mat_list[ind_bas_1: ind_bas_1 + 2]
                del self.Syn_list[ind_bas_1: ind_bas_1 + 2]
                self.Syn_list += S_con
                self.Mat_list += M_con


    def measure_stab(self, p_stab = [0,0]):

        '''
        :param p_stab:  probability of measurement error [p_stab_X, p_stab_Z]
        
        self.stab is an array that stores the measurement outcomes for the stabilizer measurements
            It has dimension [XY{0,1}, size, size]
            Measurements outcomes are either 0 or 1, analogous to -1 and 1 states
            The 0 values are the quasiparticles
        
        self.body stores the syndrome body information, e.g. the stabilizers for which the value 
            has been corrected by another error, in syndromes with length > 2.
            It has dimension [XY{0,1}, size, size, Wind{0,1,2,3}],
            where Wind stands for the direction. For example, on a star operator:
            
                  North 2
                     | 
             West 0 - - East 1
                     |
                  South 3
        '''

        self.stab = np.ones([2, self.size, self.size], dtype=bool)
        self.body = np.ones([2, self.size, self.size, 4], dtype=bool)

        # Number of quasiparticles, syndromes, and total strings
        self.N_qua = []
        self.N_syn = []
        self.N_str = []

        # Quasiparticles locations [(y,x),..] and syndromes info [[v0, v1],..]
        self.qua_loc = []
        self.syn_inf = []

        for ertype in range(2):

            if ertype == 0:
                erloc = self.X_er_loc
            else:
                erloc = self.Z_er_loc

            # Syn_list is a list of syndromes, each syndrome as two vertices, appended directly after reach other
            # Mat_list is the direct mate/neighbor of the two vertices of these syndromes, in the same order
            self.Syn_list = []
            self.Mat_list = []

            for (Y, X, HV) in erloc:
                
                # First quasiparticle is always in the same unit cell
                V0 = (Y, X)

                # Find Find other quasiparticle, (toric specific)
                if (ertype == 0 and HV == 0):       # Z error vertical
                    if Y == 0:                      # top edge
                        V1 = (self.size - 1, X)
                    else:
                        V1 = (Y - 1, X)
                elif (ertype == 0 and HV == 1):     # Z error horizontal
                    if X == 0:                      # left edge
                        V1 = (Y, self.size - 1)
                    else:
                        V1 = (Y, X - 1)
                elif (ertype == 1 and HV == 0):     # X error horizontal
                    if X == self.size - 1:          # right edge
                        V1 = (Y, 0)
                    else:
                        V1 = (Y, X + 1)
                else:                               # X error vertical
                    if Y == self.size - 1:          # bottom edge
                        V1 = (0, X)
                    else:
                        V1 = (Y + 1, X)

                # If both vertices are not yet in syndrome endpoints, append vertices as a new syndrome
                if self.stab[ertype, V0[0], V0[1]] == 1 and self.stab[ertype, V1[0], V1[1]] == 1:
                    self.stab[ertype, V0[0], V0[1]] = 0
                    self.stab[ertype, V1[0], V1[1]] = 0
                    self.Syn_list += [V0, V1]
                    self.Mat_list += [V1, V0]

                # If one of the vertices is already in a syndrome, apply syndrome algorithm
                elif self.stab[ertype, V0[0], V0[1]] == 0 and self.stab[ertype, V1[0], V1[1]] == 1:
                    self.stab[ertype, V0[0], V0[1]] = 1
                    self.stab[ertype, V1[0], V1[1]] = 0
                    S_new = [V1]
                    S_dis = [V0]
                    self.connect_syndrome(ertype, S_dis, S_new)
                elif self.stab[ertype, V0[0], V0[1]] == 1 and self.stab[ertype, V1[0], V1[1]] == 0:
                    self.stab[ertype, V0[0], V0[1]] = 0
                    self.stab[ertype, V1[0], V1[1]] = 1
                    S_new = [V0]
                    S_dis = [V1]
                    self.connect_syndrome(ertype, S_dis, S_new)
                # If both vertices al already in syndromes, apply syndrome algorithm to both
                else:
                    self.stab[ertype, V0[0], V0[1]] = 1
                    self.stab[ertype, V1[0], V1[1]] = 1
                    S_new = []
                    S_dis = [V0, V1]
                    self.connect_syndrome(ertype, S_dis, S_new)


            self.N_syn += [int(len(self.Syn_list) / 2)]
            self.N_qua += [int(len(self.Syn_list))]
            self.N_str += [int(np.sum(range(self.N_qua[ertype])))]


            # Save syndromes in [[v0, v1, crossY, crossX]] format
            syndromes = []
            for syn_i in range(self.N_syn[ertype]):
                syndromes.append([int(2 * syn_i), int(2 * syn_i + 1)])

            self.qua_loc.append(self.Syn_list)
            self.syn_inf.append(syndromes)

        if self.plot_load:
            self.L.plotXstrings(self.stab, self.body, self.qua_loc)

    def find_min_d(self, p1, p2):
        ps = min([p1,p2])
        pb = max([p1,p2])
        d1 = pb - ps
        d2 = ps - pb + self.size
        if d1 <= d2:
            d = d1
        else:
            d = d2
        return d

    def get_matching(self):

        self.results = []

        for ertype in range(2):


            # edges given to MWPM algorithm [[v0, v1, distance],...]
            edges = []

            # Get all possible strings - connections between the quasiparticles, their weights and the homology class
            for v0 in range(self.N_qua[ertype]):
                for v1 in np.arange(v0 + 1, self.N_qua[ertype]):
                    loc1 = self.qua_loc[ertype][v0]
                    loc2 = self.qua_loc[ertype][v1]
                    disty = self.find_min_d(loc1[0], loc2[0])
                    distx = self.find_min_d(loc1[1], loc2[1])
                    edges.append([v0, v1, disty + distx])

            # Apply BlossomV algorithm if there are quasiparticles
            if self.N_qua[ertype] != 0:
                output = pm.getMatching(self.N_qua[ertype], edges)
            else:
                output = []

            # Save results to same format as self.syn_inf
            result = []
            for syn_i in range(self.N_syn[ertype]):
                v0 = output[int(2 * syn_i)]
                v1 = output[int(2 * syn_i + 1)]

                result.append([self.qua_loc[ertype][v0],self.qua_loc[ertype][v1]])

            self.results.append(result)

        if self.plot_load:
            self.L.drawlines(self.results)


    def apply_matching(self):
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












    def logical_error(self):

        #print(self.array)
        # logical error in [[Xvertical, Xhorizontal], [Zvertical, Zhorizontal]]
        logical_error = [[False, False], [False, False]]


        for q in range(self.size):
            if self.array[0, 0, 0, q] == 0:
                logical_error[0][0] = not logical_error[0][0]
            if self.array[0, 1, q, 0] == 0:
                logical_error[0][1] = not logical_error[0][1]
            if self.array[1, 1, self.size - 1, q] == 0:
                logical_error[1][0] = not logical_error[1][0]
            if self.array[1, 0, q, self.size - 1] == 0:
                logical_error[1][1] = not logical_error[1][1]



        return logical_error

    def plot_corrected(self):

        singles = []
        poly    = []

        for flip in self.flips:
            count = self.flips.count(flip)
            if count == 1:
                singles.append(flip)
            elif count % 2 == 1 and flip not in poly:
                singles.append(flip)
                poly.append(flip)

        if self.plot_load:

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
