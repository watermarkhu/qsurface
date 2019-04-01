import random
import math
import numpy as np
from operator import xor
import Toric_plot as tp

def printcode(A):
    size = A.shape
    for row in range(size[0]):
        if (row%2) == 0:
            line = ""
        else:
            line = "   "
        for col in range(size[1]):
            line += str(A[row, col]) + "     "
        print(line)
class Toric_lattice:

    def __init__(self,size,p,plot):
        self.size = size
        self.p = p
        self.L = tp.plotlattice(size,plot)

    def init_Z_errors(self,ploterrors,plotstrings):
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
        Z_errors = np.array(np.random.random([2*self.size,self.size]) < self.p)
        #Z_errors = np.array([[0,1,0],[0,0,0],[0,0,0],[0,1,0],[0,0,0],[0,0,0]], dtype = bool)
        self.L.plot_errors(Z_errors, "Z",ploterrors)
        (M,N) = find_Xvs(Z_errors,self.size)
        self.L.plotXstrings(M,N,plotstrings)
        (Yloc, Xloc) = np.where(M == True)
        self.N_err = Yloc.shape[0]
        self.inf = np.array(np.concatenate((Yloc[:, None], Xloc[:, None], np.ones([self.N_err, 1]) * (self.N_err - 1)), axis=1),
                          dtype=int)
        self.N_str = int(np.sum(range(self.N_err)))
        self.com = np.zeros([self.N_str, 4], dtype=int)

        str_i = 0
        for v1 in range(self.N_err):
            for v2 in np.arange(v1 + 1, self.N_err):
                self.com[str_i, 0] = v1
                self.com[str_i, 1] = v2
                loc1 = self.inf[v1, 0:2]
                loc2 = self.inf[v2, 0:2]
                dist = find_min_d([loc1[0], loc2[0]], self.size) + find_min_d([loc1[1], loc2[1]], self.size)
                self.com[str_i, 2] = dist
                str_i += 1


    def init_Z_MWPM(self):
        self.strings_to_remove = int(self.N_str - self.N_err / 2)
        self.rem_pin_type = []
        self.rem_pin_num =  []
        self.removed_options = []
        self.removed_notmaxl = []

    def Z_removestring(self):
        def kill_affair(INF, COM, bachelor):
            inf = INF
            com = COM


            mate = None
            for str in range(com.shape[0]):
                # Find mate of v1
                if com[str, 0] == bachelor and (com[str, 3] == 0 or com[str, 3] == 2):
                    mate = int(self.com[str, 1])
                elif com[str, 1] == bachelor and (com[str, 3] == 0 or com[str, 3] == 2):
                    mate = int(self.com[str, 0])

            removed_strings = []
            lonely_exists = False
            if inf[mate, 2] > 1:
                for str in range(com.shape[0]):
                    p1 = com[str, 0] == mate and com[str, 1] != bachelor and com[str, 3] == 0
                    p2 = com[str, 1] == mate and com[str, 0] != bachelor and com[str, 3] == 0
                    if p1:
                        affair = com[str, 1]
                    elif p2:
                        affair = com[str, 0]
                    if p1 or p2:
                        if inf[affair, 2] == 1:
                            lonely_exists = True
                        else:
                            com[str, 3] = 1
                            inf[mate, 2] -= 1
                            inf[affair, 2] -= 1
                            removed_strings.append(str)

            if lonely_exists:
                return INF, COM, removed_strings, False
            else:
                return inf, com, removed_strings, True

        stay_strings = [i for i, x in enumerate(self.com[:, 3].tolist()) if x == 0]
        repair_needed = len(stay_strings) == 0
        if repair_needed:
            for it in range(len(self.removed_notmaxl))[::-1]:
                self.removed_notmaxl[it] += 1
                if self.removed_notmaxl[it] > self.removed_options[it] or self.rem_pin_type[it] == [0]:
                    self.removed_notmaxl[it] = 1
                else:
                    backit = it
                    break

            print("repaired #str ",self.rem_pin_num[backit:])
            for repair_type,repair_num in zip(self.rem_pin_type[backit:],self.rem_pin_num[backit:]):
                for type,num in zip(repair_type,repair_num):
                    if type == 0: #pinned type
                        self.com[num, 3] = 0
                    elif type == 1: #removed type
                        self.com[num, 3] = 0
                        self.inf[self.com[num,0],2] += 1
                        self.inf[self.com[num,1],2] += 1
                        self.iter -= 1

            self.rem_pin_type = self.rem_pin_type[:backit+1]
            self.rem_pin_num  = self.rem_pin_num[:backit+1]
            self.removed_options = self.removed_options[:backit+1]
            self.removed_notmaxl = self.removed_notmaxl[:backit+1]
            stay_strings = [i for i, x in enumerate(self.com[:, 3].tolist()) if x == 0]
        else:
            self.removed_notmaxl.append(1)

        max_distance = max(self.com[stay_strings, 2])  # What is the max distance
        max_d_strings = [i for i, x in enumerate(self.com[:, 2].tolist()) if x == max_distance if i in stay_strings]

        numstr1 = self.inf[np.array(self.com[max_d_strings, 0].tolist(), dtype=int), 2]
        numstr2 = self.inf[np.array(self.com[max_d_strings, 1].tolist(), dtype=int), 2]
        doublestr = numstr1 + numstr2

        if repair_needed:
            self.removed_options[-1] = len(doublestr)
        else:
            self.removed_options.append(len(doublestr))

        sort_index = len(doublestr) - self.removed_notmaxl[-1]
        str_i = max_d_strings[list(doublestr.argsort()).index(sort_index)]

        v1 = int(self.com[str_i, 0])
        v2 = int(self.com[str_i, 1])

        if (self.inf[v1, 2] > 1) and (self.inf[v2, 2] > 1):
            com = self.com
            inf = self.inf

            com[str_i, 3] = 1
            inf[v1, 2] -= 1
            inf[v2, 2] -= 1

            good_match_1 = True
            good_match_2 = True

            remstrings = []
            if self.inf[v1, 2] == 1:
                (inf, com, rem_strings1, good_match_1) = kill_affair(inf, com, v1)
                remstrings += rem_strings1

            if self.inf[v2, 2] == 1:
                (inf, com, rem_strings2, good_match_2) = kill_affair(inf, com, v2)
                remstrings += rem_strings2


            if good_match_1 and good_match_2:
                self.com = com
                self.inf = inf
                self.iter += len(remstrings)


                if repair_needed:
                    self.rem_pin_num[-1] = [str_i] + remstrings
                    self.rem_pin_type[-1] = [1]* (1+len(remstrings))
                else:
                    self.rem_pin_num.append([str_i] + remstrings)
                    self.rem_pin_type.append([1]* (1+len(remstrings)))

                self.iter += 1
                print("removed #str", remstrings + [str_i], ", (", self.iter, "of", self.strings_to_remove, ")")
            else:
                self.com[str_i, 3] = 2

                if repair_needed:
                    self.rem_pin_num[-1]= [str_i]
                    self.rem_pin_type[-1]= [0]
                else:
                    self.rem_pin_num.append([str_i])
                    self.rem_pin_type.append([0])
                print("pinned #str", str_i, "containing vertices", v1, v2, "by indirect loner")
        else:
            self.com[str_i, 3] = 2
            if repair_needed:
                self.rem_pin_num[-1] = [str_i]
                self.rem_pin_type[-1] = [0]
            else:
                self.rem_pin_num.append([str_i])
                self.rem_pin_type.append([0])
            print("pinned #str", str_i, "containing vertices", v1, v2, "by direct loner")


    def Z_MWPM(self,plot):

        self.iter = 0

        while self.iter < self.strings_to_remove:
            self.Z_removestring()
            if plot:
                self.L.drawlines(self.inf, self.com)

        if all([num_str == 1 for num_str in self.inf[:,2]]):
            print("MWPM code finished successfully, all vertices paired")
        else:
            print("MWPM code finished unsuccessfully :(")

    def showplot(self):
        self.L.drawlines(self.inf, self.com)

size = 8
p = 0.1
TL = Toric_lattice(size,p,False)
TL.init_Z_errors(False,True)
TL.init_Z_MWPM()
TL.Z_MWPM(True)
TL.showplot()
