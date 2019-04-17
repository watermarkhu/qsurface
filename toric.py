import math
import numpy as np
import Toric_plot as tp
import blossom_cpp as bl
import copy
from matplotlib import pyplot as plt
import time

class Toric_lattice:

    def __init__(self, size = 10, p=0.1,loadplot = True, base_image_size=17, plot_indices = False, plotlattice= False):
        self.size = size
        self.p = p
        self.loadplot = loadplot
        if loadplot:
            self.L = tp.plotlattice(size, plotlattice, base_image_size, plot_indices)


    def update_syndrome(self,V_dis,V_new,Ycross,Xcross):
        # V_dis: Disappearing vertice, this vertices is already in a syndrome
        # V_new: New vertices, this vertice is not yet in a syndrome, and will be matched with V_con
        # V_con: Connected vertice to the disappearing vertice, will be matched to V_new as new syndrome

        # Get indices of dis and con
        ind_dis = [i for i, x in enumerate(self.Syn_list) if x == V_dis][0]
        ind_bas = math.floor(ind_dis / 2) * 2
        ind_con = ind_bas + (1 - ind_dis % 2)

        # M is the closest mate/neighbor of syndrome endpoints. It determines the path orientation
        M_dis = self.Mat_list[ind_dis]
        V_con = self.Syn_list[ind_con]
        M_con = self.Mat_list[ind_con]
        Ycr_con = self.Hom_list[ind_bas]
        Xcr_con = self.Hom_list[ind_bas + 1]

        # Center, Around this disappearing vertice are two points
        #   1. A new vertice
        #   2. A old vertice or a syndrome path
        Yc = V_dis[0]
        Xc = V_dis[1]

        # Get the respective distances of two points
        Pall = [M_dis[0] - Yc, M_dis[1] - Xc, V_new[0] - Yc, V_new[1] - Xc]
        Pt= [-i/abs(i) if abs(i) == self.size - 1 else i for i in Pall]
        Pc = [[Pt[0],Pt[1]],[Pt[2],Pt[3]]]

        # Define vectors
        Wvec = [0, -1]
        Evec = [0, 1]
        Nvec = [-1, 0]
        Svec = [1, 0]

        # Find which vectors are present, determine orientation or green path
        if Nvec in Pc and Evec in Pc:  # -
            self.Vline[Yc, Xc, 2] = True
            self.Vline[Yc, Xc, 1] = True
        elif Nvec in Pc and Wvec in Pc:
            self.Vline[Yc, Xc, 2] = True
            self.Vline[Yc, Xc, 0] = True
        elif Svec in Pc and Wvec in Pc:
            self.Vline[Yc, Xc, 3] = True
            self.Vline[Yc, Xc, 0] = True
        elif Svec in Pc and Evec in Pc:
            self.Vline[Yc, Xc, 3] = True
            self.Vline[Yc, Xc, 1] = True
        elif Nvec in Pc and Svec in Pc:
            self.Vline[Yc, Xc, 2] = True
            self.Vline[Yc, Xc, 3] = True
        elif Evec in Pc and Wvec in Pc:
            self.Vline[Yc, Xc, 0] = True
            self.Vline[Yc, Xc, 1] = True
        else:
            print("Error no path found")

        if Ycr_con: Ycross = not Ycross
        if Xcr_con: Xcross = not Xcross

        del self.Hom_list[ind_bas: ind_bas + 2]
        del self.Mat_list[ind_bas: ind_bas + 2]
        del self.Syn_list[ind_bas: ind_bas + 2]
        self.Syn_list += [V_con, V_new]
        self.Mat_list += [M_con, V_dis]
        self.Hom_list += [Ycross, Xcross]

        return V_con

    def init_Z_errors(self, ploterrors=False, plotstrings=False, new_errors=True, write_error = True, Error_file = "Z_errors.txt"):
        def find_min_d(p1, p2, size):
            ps = min([p1,p2])
            pb = max([p1,p2])
            d1 = pb - ps
            d2 = ps - pb + size
            if d1 <= d2:
                d = d1
                crosshom = False
            else:
                d = d2
                crosshom = True
            return (d,crosshom)

        if new_errors:
            self.Z_errors = np.array(np.random.random([self.size, self.size, 2]) < self.p)
            if write_error:
                np.savetxt(Error_file, self.Z_errors.reshape(2*self.size,self.size), fmt="%d")
        else:
            self.Z_errors = np.reshape(np.loadtxt(Error_file, dtype=bool), (self.size,self.size,2))

        if self.loadplot:
            self.L.plot_errors(self.Z_errors, "Z", ploterrors)

        # self.Vplus is matrix of vertices
        # self.Vline contains 4 lines per vertice
        self.Vplus = np.zeros([self.size, self.size], dtype=bool)
        self.Vline = np.zeros([self.size, self.size, 4], dtype=bool)

        # Syn_list is a list of syndromes, each syndrome as two vertices, appended directly afte reach other
        # Mat_list is the direct mate/neighbor of the two vertices of these syndromes, in the same order
        # Hom_list stores whether the syndrome suffers X or Y errors, luckily also two values.
        self.Syn_list = []
        self.Mat_list = []
        self.Hom_list = []
        Yloc, Xloc, HVloc = np.where(self.Z_errors == True)
        for Y, X, HV in zip(Yloc, Xloc, HVloc):
            V0 = [Y, X]
            Ycross = False
            Xcross = False

            # Find vertices for a certain error
            if HV == 0:                 # Horizontal
                if X == self.size - 1:  # right edge
                    V1 = [Y, 0]
                    Xcross = True
                else:                   # normal case
                    V1 = [Y, X + 1]
            else:                       # Vertical
                if Y == self.size - 1:  # bottom edge
                    V1 = [0, X]
                    Ycross = True
                else:                   # normal case
                    V1 = [Y + 1, X]

            # If both vertices are not yet in syndrome endpoints, append vertices as a new syndrome
            if self.Vplus[V0[0], V0[1]] == False and self.Vplus[V1[0], V1[1]] == False:
                self.Vplus[V0[0], V0[1]] = True
                self.Vplus[V1[0], V1[1]] = True
                self.Syn_list += [V0, V1]
                self.Mat_list += [V1, V0]
                self.Hom_list += [Ycross, Xcross]

            # If one of the vertices is already in a syndrome, apply syndrome algorithm
            elif self.Vplus[V0[0], V0[1]] == True and self.Vplus[V1[0], V1[1]] == False:
                self.Vplus[V0[0], V0[1]] = False
                self.Vplus[V1[0], V1[1]] = True
                V_new = V1
                V_dis = V0
                self.update_syndrome(V_dis, V_new, Ycross, Xcross)
            elif self.Vplus[V0[0], V0[1]] == False and self.Vplus[V1[0], V1[1]] == True:
                self.Vplus[V0[0], V0[1]] = True
                self.Vplus[V1[0], V1[1]] = False
                V_new = V0
                V_dis = V1
                self.update_syndrome(V_dis, V_new, Ycross, Xcross)

            # If both vertices al already in syndromes, apply syndrome algorithm to both
            #   If the syndrome is a closing loop, apply only to one
            else:
                self.Vplus[V0[0], V0[1]] = False
                self.Vplus[V1[0], V1[1]] = False
                V_new = V1
                V_dis = V0
                V_con = self.update_syndrome(V_dis, V_new, Ycross, Xcross)
                if V_con != V1:
                    V_new = V0
                    V_dis = V1
                    self.update_syndrome(V_dis, V_new, Ycross, Xcross)


            #print(Syn_list)
            #self.L.plotXstrings(self.Vplus, self.Vline, plotstrings, save=False)


        (Yplus, Xplus) = np.where(self.Vplus == True)
        if self.loadplot:
            self.L.plotXstrings(self.Vplus, self.Vline, plotstrings)

        # Number of quasiparticles (-1 measurements)
        self.N_qua = Yplus.shape[0]
        self.N_syn = int(self.N_qua / 2)

        # quasiparticle info: y, x, connectivity, #
        self.qui = np.array(np.concatenate((Yplus[:, None], Xplus[:, None], np.ones([self.N_qua, 1]) * (self.N_qua - 1), \
                                            np.reshape(np.arange(self.N_qua), (self.N_qua, 1))), axis=1), dtype=int)

        # Syndrome info: quasi_0, quasi_1, homology y, homology x
        self.syi = np.zeros([self.N_syn, 4], dtype=int)
        #self.get_syndromes()
        #print(self.syi)
        for iq in range(self.N_syn):
            V0 = self.Syn_list[int(2 * iq)]
            V1 = self.Syn_list[int(2 * iq) + 1]
            self.syi[iq, 2]  = self.Hom_list[int(2 * iq)]
            self.syi[iq, 3]  = self.Hom_list[int(2 * iq) + 1]
            for iv in range(self.N_qua):
                if Yplus[iv] == V0[0] and Xplus[iv] == V0[1]:
                    self.syi[iq, 0] = iv
                if Yplus[iv] == V1[0] and Xplus[iv] == V1[1]:
                    self.syi[iq, 1] = iv

        # number of total connected strings
        self.N_str = int(np.sum(range(self.N_qua)))

        # String info: quasi_0, quasi_1, distance, state, homology y, homology x, #
        self.sti = np.zeros([self.N_str, 7], dtype=int)

        str_i = 0
        for v1 in range(self.N_qua):
            for v2 in np.arange(v1 + 1, self.N_qua):
                self.sti[str_i, 6] = str_i
                self.sti[str_i, 0] = v1
                self.sti[str_i, 1] = v2
                loc1 = self.qui[v1, 0:2]
                loc2 = self.qui[v2, 0:2]
                (disty, self.sti[str_i, 4]) = find_min_d(loc1[0], loc2[0], self.size)
                (distx, self.sti[str_i, 5]) = find_min_d(loc1[1], loc2[1], self.size)
                self.sti[str_i, 2] = disty + distx
                str_i += 1


    def blossom(self):
        edges = [list(x[:3]) for x in self.sti]
        result = bl.blossom(self.N_qua,edges)
        self.qui[:,2] = 1
        self.sti[:,3] = 1

        self.result = np.zeros([self.N_syn, 7], dtype=int)

        res_i = 0
        for edge in result:
            p0 = edge[0]
            p1 = edge[1]
            for str in range(self.N_str):
                if self.sti[str,0] == p0 and self.sti[str,1] == p1:
                    self.sti[str,3] = 0
                    self.result[res_i,:] = self.sti[str,:]
                    res_i += 1
                    break

    def logical_error(self):

        #print(self.syi)
        #print(self.result)

        synY_n = np.sum(self.syi[:, 2])
        synX_n = np.sum(self.syi[:, 3])
        mwmY_n = np.sum(self.result[:, 4])
        mwmX_n = np.sum(self.result[:, 5])

        # L0 logical error
        # Returns True: if number of Y and X logical errors in syndrome and matching are equal
        if synY_n == mwmY_n and synX_n == mwmX_n:
            N_cross_eq = True
        else:
            N_cross_eq = False

        # L1 logical error
        # Returns True: if parity of number of Y, X logical errors (effective errors) matches in
        #     syndrome and matching
        if synY_n % 2 == mwmY_n % 2 and synX_n % 2 == mwmX_n % 2:
            cross_eq = True
        else:
            cross_eq = False

        # L2 logical error
        # Returns true if only all matchings are equal to the syndromes
        perfect_matching = True
        for syn_i in range(self.N_syn):
            p0 = self.syi[syn_i, 0]
            p1 = self.syi[syn_i, 1]

            num, locA = np.where(self.result[:,:2] == p0)
            locB = 1 - locA

            if self.result[num,locB] != p1:
                perfect_matching = False
                break

        return N_cross_eq, cross_eq, perfect_matching


    def showplot(self):

        if self.loadplot == True:
            im = self.L.drawlines(self.qui, self.sti)
            plt.figure()
            plt.imshow(im)
            plt.show()
        else:
            print("Plot not loaded during initialization")


    def new_yx(self, y, x, dy, dx):
        ny = y + dy
        nx = x + dx
        crossY = False
        crossX = False
        if ny < 0:
            ny = y + self.size + dy
            crossY = True
        if ny >= self.size:
            ny = y - self.size + dy
            crossY = True
        if nx < 0:
            nx = x + self.size + dx
            crossX = True
        if nx >= self.size:
            nx = x - self.size + dx
            crossX = True
        return [ny,nx, crossY, crossX]
    def star_get_Z(self,y,x):
        if x != 0:
            w = [2 * y, x -1]
        else:
            w = [2 * y, self.size-1]
        e = [2 * y, x]
        if y != 0:
            n = [2 * (y - 1) + 1, x]
        else:
            n = [2 * (self.size -1) + 1, x]
        s = [2 * y + 1, x]
        return [w,e,n,s]
    def get_syndromes(self):
        # West, East, North, South steps
        WENS = [[0, -1], [0, 1],[-1, 0], [1, 0]]
        qua_done = [True] * self.N_qua
        qua_list = []
        for syn_i in range(int(self.N_qua/2)):
            v1 = qua_done.index(True)
            self.syi[syn_i,0] = v1
            y = self.qui[v1, 0]
            x = self.qui[v1, 1]
            qua_done[v1] = False
            qua_list.append([y,x])

            crossY = False
            crossX = False

            # get neighbors
            neighbors = [self.new_yx(y, x, WENS[i][0], WENS[i][1]) for i in range(4)]
            star_z = self.star_get_Z(y, x)

            Path_search = False

            for n_i in range(4):
                y2 = int(2 * neighbors[n_i][0])
                x2 = int(2 * neighbors[n_i][1])
                line_w = self.Vline[y2, x2]
                line_e = self.Vline[y2, x2 + 1]
                line_n = self.Vline[y2 + 1, x2]
                line_s = self.Vline[y2 + 1, x2 + 1]

                ewsn = [line_e, line_w, line_s, line_n]

                if ewsn[n_i]:
                    Path_search = True
                    N_new = neighbors[n_i]
                    wind = n_i
                    break
                if (self.Vplus[neighbors[n_i][0], neighbors[n_i][1]] == True):
                    if self.Z_errors[star_z[n_i][0],star_z[n_i][1]] == True:

                        N_new = neighbors[n_i]
                        if N_new[2] == True: crossY = not crossY
                        if N_new[3] == True: crossX = not crossX

            while Path_search == True:
                y = N_new[0]
                x = N_new[1]
                if N_new[2] == True: crossY = not crossY
                if N_new[3] == True: crossX = not crossX
                y2 = int(2 * y)
                x2 = int(2 * x)
                line_w = self.Vline[y2, x2]
                line_e = self.Vline[y2, x2 + 1]
                line_n = self.Vline[y2 + 1, x2]
                line_s = self.Vline[y2 + 1, x2 + 1]

                # if green path found on new neighbor
                if any([line_w, line_e, line_n, line_s]):
                    # West
                    if any([wind == 0, wind == 2, wind == 3]) and line_w == True:
                        N_temp = self.new_yx(y, x, WENS[0][0], WENS[0][1])
                        if N_temp[:2] not in qua_list: N_new = N_temp
                        wind_temp = 0
                    # East
                    if any([wind == 1, wind == 2, wind == 3]) and line_e == True:
                        N_temp = self.new_yx(y, x, WENS[1][0], WENS[1][1])
                        if N_temp[:2] not in qua_list: N_new = N_temp
                        wind_temp = 1
                    # North
                    if any([wind == 0, wind == 1, wind == 2]) and line_n == True:
                        N_temp = self.new_yx(y, x, WENS[2][0], WENS[2][1])
                        if N_temp[:2] not in qua_list: N_new = N_temp
                        wind_temp = 2
                    # South
                    if any([wind == 0, wind == 1, wind == 3]) and line_s == True:
                        N_temp = self.new_yx(y, x, WENS[3][0], WENS[3][1])
                        if N_temp[:2] not in qua_list: N_new = N_temp
                        wind_temp = 3

                    wind = wind_temp
                else:
                    Path_search = False
            else:
                mate = N_new[:2]
                for i in range(self.N_qua):
                    if [self.qui[i,0], self.qui[i,1]] == mate:

                        self.syi[syn_i,1] = i
                        self.syi[syn_i,2] = crossY
                        self.syi[syn_i,3] = crossX
                        qua_done[i] = False
                        qua_list.append(mate)
    def Z_MWPM(self, plot = False, plot_percentage = 90, fps = 2):

        if plot:
            fig = plt.figure()
            fig.canvas.draw()
            ax = plt.gca()
            fig.canvas.draw()
            i_plot = ax.imshow(self.L.lattice)
            axbackground = fig.canvas.copy_from_bbox(ax.bbox)
            t_start = time.time()


        strings_to_remove = int(self.N_str - self.N_qua / 2)
        N_removed = 0
        iter = 0
        bad_matching = False

        while not all([num_str == 1 for num_str in self.qui[:, 2]]):

            ###############################################################################
            ###### Part 1: Selection #########

            com_s0 = self.qui[self.sti[:, 0], 2]
            com_s1 = self.qui[self.sti[:, 1], 2]

            # Find all available strings with v# != 0 and phi is 0 (still available)
            available_strings = [i for i,(s1, s2, phi) in
                                 enumerate(zip(com_s0 != 1, com_s1 != 1, self.sti[:, 3] == 0)) if all([s1, s2, phi])]

            # sort based on string distance and connected vertex v#
            available_distances = self.sti[available_strings, 2]
            available_sum_string = com_s0[available_strings] + com_s1[available_strings]
            sorted_indices = np.lexsort((available_distances, available_sum_string))[::-1]

            if len(sorted_indices) == 0:
                bad_matching = True
                break
            sort_index = sorted_indices[0]
            sort_string = available_strings[sort_index]


            ###############################################################################
            ######### Part 2: Removal #########

            none_alone = True

            # Removal action, picks a string with longest distance and highest vertices connections
            com = copy.deepcopy(self.sti)
            inf = copy.deepcopy(self.qui)
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
                done_vertices = [False]*self.N_qua
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
                com = copy.deepcopy(self.sti)
                inf = copy.deepcopy(self.qui)
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
            self.qui = copy.deepcopy(inf)
            self.sti = copy.deepcopy(com)

            N_removed += len(removed_strings)

            print(pre + "Removed #", removed_strings, ", pinned #", pinned_strings, "Iter:", iter,
                  "Strings removed:", N_removed, "of",strings_to_remove)

            if plot and N_removed/strings_to_remove*100 > plot_percentage:
                t_i = time.time()

                if t_i - t_start < 1/fps:
                    time.sleep(1/fps - t_i + t_start)

                im = self.L.drawlines(self.qui, self.sti)
                i_plot.set_data(im)
                fig.canvas.restore_region(axbackground)
                ax.draw_artist(i_plot)
                fig.canvas.blit(ax.bbox)
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.000000000001)

                t_start = t_i

        if bad_matching:
            bad_mates = [i for i,x in enumerate(self.qui[:,2]) if x == 2]
            connections = []
            connect_str = []
            for bad_mate in bad_mates:
                for str in range(self.N_str):
                    if self.sti[str, 0] == bad_mate and (self.sti[str, 3] == 2):  # or com[str, 3] == 2):
                        connections.append(self.sti[str, 1])
                        connect_str.append(str)
                    elif self.sti[str, 1] == bad_mate and (self.sti[str, 3] == 2):  # or com[str, 3] == 2):
                        connections.append(self.sti[str, 0])
                        connect_str.append(str)

            str_a = 0
            str_b = 2

            self.sti[connect_str[str_a],3] = 1
            self.sti[connect_str[str_b],3] = 1

            for str in range(self.N_str):
                if self.sti[str, 0] == connections[str_a] and self.sti[str,1] == connections[str_b]:
                    self.sti[str,3] = 0
                    break
                elif self.sti[str, 0] == connections[str_b] and self.sti[str,1] == connections[str_a]:
                    self.sti[str,3] = 0
                    break


        if all([num_str == 1 for num_str in self.qui[:, 2]]):
            print("MWPM code finished successfully, all vertices paired")
        else:
            print("MWPM code finished unsuccessfully :(, not best matching")
