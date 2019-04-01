import math
import numpy as np
from operator import xor
import Toric_plot as tp
import copy
import time

class Toric_lattice:

    def __init__(self, size, p, plot):
        self.size = size
        self.p = p
        self.L = tp.plotlattice(size, plot)

    def init_Z_errors(self, ploterrors=False, plotstrings=False, new_errors=True, Error_file = "Z_errors.txt"):
        def find_min_d(p, size):
            ps = min(p)
            pb = max(p)
            diff = min([pb - ps, ps - pb + size])
            return diff

        def find_Xvs(Z_errors, size):
            M = np.zeros([size, size], dtype=bool)
            N = np.zeros([2 * size, 2 * size], dtype=bool)
            Yloc, Xloc = np.where(Z_errors == 1)
            for Y2, X in zip(Yloc, Xloc):
                Y = math.floor(Y2 / 2)
                M[Y, X] = xor(M[Y, X], True)
                if Y2 % 2 == 0:  # Even rows
                    N[2 * Y, 2 * X + 1] = True
                    if X == size - 1:
                        M[Y, 0] = xor(M[Y, 0], True)
                        N[2 * Y, 0] = True
                    else:
                        M[Y, X + 1] = xor(M[Y, X + 1], True)
                        N[2 * Y, 2 * X + 2] = True
                else:  # Odd rows
                    N[2 * Y + 1, 2 * X + 1] = True
                    if Y == size - 1:
                        M[0, X] = xor(M[0, X], True)
                        N[1, 2 * X] = True
                    else:
                        M[Y + 1, X] = xor(M[Y + 1, X], True)
                        N[2 * Y + 3, 2 * X] = True
            return (M, N)

        if new_errors:
            Z_errors = np.array(np.random.random([2 * self.size, self.size]) < self.p)
            np.savetxt(Error_file, Z_errors, fmt="%d")
        else:
            Z_errors = np.loadtxt(Error_file, dtype=int)

        self.L.plot_errors(Z_errors, "Z", ploterrors)
        (M, N) = find_Xvs(Z_errors, self.size)
        self.L.plotXstrings(M, N, plotstrings)
        (Yloc, Xloc) = np.where(M == True)
        self.N_err = Yloc.shape[0]
        self.inf = np.array(np.concatenate((Yloc[:, None], Xloc[:, None], np.ones([self.N_err, 1]) * (self.N_err - 1), \
                                            np.reshape(np.arange(self.N_err), (self.N_err, 1))), axis=1), dtype=int)
        self.N_str = int(np.sum(range(self.N_err)))
        self.com = np.zeros([self.N_str, 5], dtype=int)

        str_i = 0
        for v1 in range(self.N_err):
            for v2 in np.arange(v1 + 1, self.N_err):
                self.com[str_i, 4] = str_i
                self.com[str_i, 0] = v1
                self.com[str_i, 1] = v2
                loc1 = self.inf[v1, 0:2]
                loc2 = self.inf[v2, 0:2]
                dist = find_min_d([loc1[0], loc2[0]], self.size) + find_min_d([loc1[1], loc2[1]], self.size)
                self.com[str_i, 2] = dist
                str_i += 1

    def Z_MWPM(self, plot, plot_iter):

        strings_to_remove = int(self.N_str - self.N_err / 2)
        N_removed = 0
        iter = 0


        while not all([num_str == 1 for num_str in self.inf[:, 2]]):

            ###############################################################################
            ###### Part 1: Selection #########

            com_s0 = self.inf[self.com[:, 0], 2]
            com_s1 = self.inf[self.com[:, 1], 2]

            # Find all available strings with v# != 0 and phi is 0 (still available)
            available_strings = [i for i,(s1, s2, phi) in
                                 enumerate(zip(com_s0 != 1, com_s1 != 1, self.com[:, 3] == 0)) if all([s1, s2, phi])]

            # sort based on string distance and connected vertex v#
            available_distances = self.com[available_strings, 2]
            available_sum_string = com_s0[available_strings] + com_s1[available_strings]
            sorted_indices = np.lexsort((available_distances, available_sum_string))[::-1]
            sort_index = sorted_indices[0]
            sort_string = available_strings[sort_index]


            ###############################################################################
            ######### Part 2: Removal #########

            none_alone = True

            # Removal action, picks a string with longest distance and highest vertices connections
            com = copy.deepcopy(self.com)
            inf = copy.deepcopy(self.inf)
            removed_strings = []
            pinned_strings = []

            # Get vertices of string to remove
            b0 = com[sort_string, 0]
            b1 = com[sort_string, 1]

            # Apply removal
            com[sort_string, 3] = 1
            inf[b0, 2] -= 1
            inf[b1, 2] -= 1
            removed_strings.append(sort_string)

            # Check if vertices are bachelors
            bachelors = []
            if inf[b0, 2] == 1:
                bachelors.append(b0)
            if inf[b1, 2] == 1:
                bachelors.append(b1)

            # Loop over bachelors, lone affairs of mates of removed mate-affair string are added
            tree = 0
            while tree < len(bachelors):

                # Find mate of bachelor, only 1 mate possible (definition of bachelor)
                # Pin the bachelor-mate string
                for str in range(self.N_str):
                    if com[str, 0] == bachelors[tree] and (com[str, 3] == 0 or com[str, 3] == 2):
                        mate = int(com[str, 1])
                        pinned_strings.append(str)
                        com[str, 3] = 2
                        break
                    elif com[str, 1] == bachelors[tree] and (com[str, 3] == 0 or com[str, 3] == 2):
                        mate = int(com[str, 0])
                        pinned_strings.append(str)
                        com[str, 3] = 2
                        break

                # Find affairs of mate, if mate has more than 1 (with bachelor) connections
                if inf[mate, 2] > 1:
                    mate_is_0 = com[:, 0] == mate
                    mate_is_1 = com[:, 1] == mate
                    available = com[:, 3] == 0
                    affair_strings = [i for i, (m0, m1, av) in enumerate(zip(mate_is_0, mate_is_1, available)) if
                                      (m0 or m1) and av]

                    # Remove all mate-affair connections
                    for str in affair_strings:
                        if mate_is_0[str]:
                            affair = com[str, 1]
                        else:  # mate is 1
                            affair = com[str, 0]
                        removed_strings.append(str)
                        com[str, 3] = 1
                        inf[mate, 2] -= 1
                        inf[affair, 2] -= 1

                        # If after removal, # connections of affairs = 1, it is a new bachelor
                        if inf[affair, 2] == 1:
                            bachelors.append(affair)

                        if inf[affair, 2] == 0:
                            none_alone = False
                            break
                tree += 1

            ###############################################################################
            ############# Part 3a: Check T-section #############

            check_T_section = False

            if check_T_section:
                if 3 in inf[:,2]:

                    tri_points = inf[:,2] == 3
                    valid_strings = [s0 or s2 for s0, s2 in zip(com[:, 3] == 0, com[:, 3] == 2)]
                    T_section_found = True

                    for tri_point in tri_points:
                        s0 = com[:,0] == tri_point
                        s1 = com[:,1] == tri_point
                        triangle = [i for i,(x,y,z) in enumerate(zip(s0,s1,valid_strings)) if (x or y) and z]

                        for point in triangle:
                            p0 = com[:, 0] == point
                            p1 = com[:, 1] == point
                            p_connects = [i for i,(x,y,z) in enumerate(zip(p0,p1,valid_strings)) if (x or y) and z]

                            for p_connect in p_connects:
                                if p_connect in triangle:
                                    T_section_found = False
                                    break

                            if T_section_found:
                                break
                        if T_section_found:
                            break
                    if T_section_found:
                        print("Error: remove", removed_strings, ", pin", pinned_strings,
                              "not valid. Triple T-section found")
                        none_alone = False

            ###############################################################################
            ############# Part 3b: Check blobs #############

            # Once 2 connected vertices are present, check for uneven blobs
            elif 2 in inf[:,2]:
                done_vertices = [False]*self.N_err
                done_strings = [False]*self.N_str
                valid_strings = [s0 or s2 for s0,s2 in zip(com[:, 3] == 0, com[:,3] == 2)]

                # while there are still vertices present that are not considered
                while any([not done_v for done_v in done_vertices]):

                    # initiate blob with first unconsidered vertice
                    v_blob = []
                    start_v = done_vertices.index(False)
                    v_blob.append(start_v)
                    tree = 0

                    # v_blob is extended, vertices are added to the blob, all vertices in blob will be checked
                    while tree < len(v_blob):

                        # check this vertice as considered
                        done_vertices[v_blob[tree]] = True

                        # Find connected strings to this vertice
                        str0 = com[:, 0] == v_blob[tree]
                        str1 = com[:, 1] == v_blob[tree]
                        connected_s0 = [i for i, (x, y) in enumerate(zip(str0, valid_strings)) if x and y]
                        connected_s1 = [i for i, (x, y) in enumerate(zip(str1, valid_strings)) if x and y]

                        # Find vertices on other end of strings, add to blob if not already
                        for connected_s in connected_s0:
                            if done_strings[connected_s] == False:
                                done_strings[connected_s] = True
                                connected_v = com[connected_s, 1]
                                if connected_v not in v_blob:
                                    v_blob.append(connected_v)
                        for connected_s in connected_s1:
                            if done_strings[connected_s] == False:
                                done_strings[connected_s] = True
                                connected_v = com[connected_s, 0]
                                if connected_v not in v_blob:
                                    v_blob.append(connected_v)
                        tree += 1

                    # If blob has uneven number of vertices, last removal was invalid
                    if len(v_blob)%2 == 1:
                        print("Error: remove", removed_strings, ", pin", pinned_strings,
                              "not valid. Uneven blobs of errors left")
                        none_alone = False
                        break

            ###############################################################################
            #################### Part 4: Pinning #########################

            # If none uneven blobs found, removal was valid. Continue to next removal
            if none_alone:
                iter += 1
                pre = ""
            # Otherwise, pin string chosen for removal.
            else:
                pre = ">> "
                com = copy.deepcopy(self.com)
                inf = copy.deepcopy(self.inf)
                removed_strings = []
                pinned_strings = []

                # Pinning action, initiate mates vector
                com[sort_string, 3] = 2
                pinned_strings.append(sort_string)
                mates = [com[sort_string, 0], com[sort_string, 1]]

                tree = 0
                while tree < len(mates):

                    # Find affairs of mates
                    mate_is_0 = com[:, 0] == mates[tree]
                    mate_is_1 = com[:, 1] == mates[tree]
                    available = com[:, 3] == 0
                    affair_strings = [i for i, (m0, m1, av) in enumerate(zip(mate_is_0, mate_is_1, available)) if
                                      (m0 or m1) and av]

                    # Loop over all found affairs, removal of mate-affair string
                    for str in affair_strings:
                        if mate_is_0[str]:
                            affair = com[str, 1]
                        else:  # mate is 1
                            affair = com[str, 0]
                        removed_strings.append(str)
                        com[str, 3] = 1
                        inf[mates[tree], 2] -= 1
                        inf[affair, 2] -= 1

                        # If affair is possible sole mate of a new vertice, called brad, add brad to mates vector
                        if inf[affair, 2] == 1:
                            for str in range(self.N_str):
                                # Find brad of affair
                                if com[str, 0] == affair and (com[str, 3] == 0):# or com[str, 3] == 2):
                                    brad = int(com[str, 1])
                                    mates.append(brad)
                                    com[str, 3] = 2
                                    pinned_strings.append(str)
                                    break
                                elif com[str, 1] == affair and (com[str, 3] == 0):# or com[str, 3] == 2):
                                    brad = int(com[str, 0])
                                    mates.append(brad)
                                    com[str, 3] = 2
                                    pinned_strings.append(str)
                                    break

                    tree += 1

            # Save removed or pinned action.
            self.inf = copy.deepcopy(inf)
            self.com = copy.deepcopy(com)

            N_removed += len(removed_strings)

            print(pre + "Removed #", removed_strings, ", pinned #", pinned_strings, "Iter:", iter,
                  "Strings removed:", N_removed, "of",strings_to_remove)

            if plot and plot_iter <= iter:
                self.L.drawlines(self.inf, self.com)


            time.sleep(0.001)

        if all([num_str == 1 for num_str in self.inf[:, 2]]):
            print("MWPM code finished successfully, all vertices paired")
        else:
            print("MWPM code finished unsuccessfully :(")

    def showplot(self):
        self.L.drawlines(self.inf, self.com)
