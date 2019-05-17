from matplotlib import pyplot as plt
import os
import copy
import numpy as np

class lattice_plot:


    def __init__(self, size, qubit_data, stab_data):

        self.plot_base = False
        self.plot_error = True
        self.plot_syndrome = True
        self.plot_matching = True
        self.plot_correction = True
        self.plot_result = True
        self.size = size
        self.qubit_data = qubit_data
        self.stab_data = stab_data

        self.qsize = 0.5
        self.qsize2 = 0.25
        self.qsizeE = 0.7
        self.lw = 3
        self.slw = 2

        # Define colors
        self.cw = [1, 1, 1]
        self.cl = [0.8, 0.8, 0.8]       # Line color
        self.cc = [0.2, 0.2, 0.2]       # Qubit color
        self.cx = [0.9, 0.5, 0.5]       # X error color
        self.cz = [0.5, 0.9, 0.5]       # Z error color
        self.cy = [0.9, 0.9, 0.5]       # Y error color
        self.cX = [0.9, 0.5, 0.5]       # X quasiparticle color
        self.cZ = [0.5, 0.9, 0.5]       # Z quasiparticle color
        self.cE = [0.3, 0.5, 0.9]       # Erasure color


        # Initiate figure
        self.f = plt.figure(1, figsize = (10, 10))
        plt.ion()
        plt.show()
        self.ax = self.f.gca()


    def plot_lattice(self):
        '''
        Plots the toric lattice.
        Which includes the vertices on the initial and secundary lattices, and two qubits per cell
        '''

        plt.figure(self.f.number)
        self.ax.invert_yaxis()
        self.ax.set_aspect('equal')

        # Loop over all indices
        for yb in range(self.size):
            y = yb * 4
            for xb in range(self.size):
                x = xb * 4

                # Plot primary lattice
                plt.plot([x+0, x+1], [y+1, y+1], c = self.cl, lw = self.lw, ls = '-')
                plt.plot([x+1, x+2], [y+1, y+1], c = self.cl, lw = self.lw, ls = '-')
                plt.plot([x+1, x+1], [y+0, y+1], c = self.cl, lw = self.lw, ls = '-')
                plt.plot([x+1, x+1], [y+1, y+2], c = self.cl, lw = self.lw, ls = '-')

                # Plot secundary lattice
                plt.plot([x+2, x+3], [y+3, y+3], c = self.cl, lw = self.lw, ls = '--')
                plt.plot([x+3, x+4], [y+3, y+3], c = self.cl, lw = self.lw, ls = '--')
                plt.plot([x+3, x+3], [y+2, y+3], c = self.cl, lw = self.lw, ls = '--')
                plt.plot([x+3, x+3], [y+3, y+4], c = self.cl, lw = self.lw, ls = '--')

                # Plot qubits
                circlet = plt.Circle((x+3, y+1), self.qsize, edgecolor = self.cc, fill = False, linewidth = self.lw)
                circled = plt.Circle((x+1, y+3), self.qsize, edgecolor = self.cc, fill = False, linewidth = self.lw)
                self.ax.add_artist(circlet)
                self.ax.add_artist(circled)

        if self.plot_base:
            plt.draw()
            print("Lattice plotted. Press on the plot to continue")
            plt.waitforbuttonpress()

    def plot_erasures(self, erasures):
        '''
        :param erasures         list of locations (TD, y, x) of the erased stab_qubits
        plots an additional blue cicle around the qubits which has been erased
        '''
        plt.figure(self.f.number)

        for yb in range(self.size):
            y = yb * 4
            for xb in range(self.size):
                x = xb * 4

                if erasures[0][yb][xb] != 0:
                    circle = plt.Circle((x+3, y+1), self.qsizeE, edgecolor = self.cE, fill = False, linewidth = self.lw, linestyle = ":")
                    self.ax.add_artist(circle)
                if erasures[1][yb][xb] != 0:
                    circle = plt.Circle((x+1, y+3), self.qsizeE, edgecolor = self.cE, fill = False, linewidth = self.lw, linestyle = ":")
                    self.ax.add_artist(circle)


    def plot_errors(self, array):
        '''
        :param arrays       array of qubit states
        plots colored circles within the qubits if there is an error
        '''
        Xer = []
        Zer = []

        for id in [id for id, state in enumerate(array[:self.size*self.size*2]) if state == False]:
            Xer.append(id)
        for id in [id for id, state in enumerate(array[self.size*self.size*2:]) if state == False]:
            Zer.append(id)
        Yer = []

        for iX in Xer:
            if iX in Zer:
                Yer.append(iX)
        for iY in Yer:
            Xer.remove(iY)
            Zer.remove(iY)

        plt.figure(self.f.number)

        loc = [3, 1]

        # Plot X errors
        for iX in Xer:
            (Y , X , TD) = self.qubit_data[iX][1:4]
            circle = plt.Circle((X*4+loc[TD], Y*4+loc[1-TD]), self.qsize, fill = True, facecolor = self.cx, edgecolor = self.cc, linewidth = self.lw)
            self.ax.add_artist(circle)

        # Plot Z errors
        for iZ in Zer:
            (Y , X , TD) = self.qubit_data[iZ][1:4]
            circle = plt.Circle((X*4+loc[TD], Y*4+loc[1-TD]), self.qsize, fill = True, facecolor = self.cz, edgecolor = self.cc, linewidth = self.lw)
            self.ax.add_artist(circle)

        # Plot Y errors
        for iY in Yer:
            (Y , X , TD) = self.qubit_data[iY][1:4]
            circle = plt.Circle((X*4+loc[TD], Y*4+loc[1-TD]), self.qsize, fill = True, facecolor = self.cy, edgecolor = self.cc, linewidth = self.lw)
            self.ax.add_artist(circle)


        if self.plot_error:
            plt.draw()
            print("Errors plotted. Press on the plot to continue")
            plt.waitforbuttonpress()


    def plot_anyons(self, qua_loc):
        '''
        :param qua_loc      list of quasiparticle/anyon positions (y,x)
        plots the vertices of the anyons on the lattice
        '''

        plt.figure(self.f.number)
        ploc = [2, 0]
        C = [self.cX, self.cZ]
        LS = ['--', '-']

        # Plot errors on primary and secondary lattice
        for type, id_type in enumerate(qua_loc):
            for id in id_type:
                (yb, xb) = self.stab_data[id][1:3]
                y = yb * 4
                x = xb * 4
                plt.plot([x+0+ploc[type], x+1+ploc[type]], [y+1+ploc[type], y+1+ploc[type]], c = C[type], lw = self.lw, ls = LS[type])
                plt.plot([x+1+ploc[type], x+2+ploc[type]], [y+1+ploc[type], y+1+ploc[type]], c = C[type], lw = self.lw, ls = LS[type])
                plt.plot([x+1+ploc[type], x+1+ploc[type]], [y+0+ploc[type], y+1+ploc[type]], c = C[type], lw = self.lw, ls = LS[type])
                plt.plot([x+1+ploc[type], x+1+ploc[type]], [y+1+ploc[type], y+2+ploc[type]], c = C[type], lw = self.lw, ls = LS[type])

        if self.plot_syndrome:
            plt.draw()
            print("Syndromes plotted. Press on the plot to continue")
            plt.waitforbuttonpress()


    def plot_lines(self, results):
        '''
        :param results      list of matchings of anyon
        plots strings between the two anyons of each match
        '''

        plt.figure(self.f.number)
        ploc = [3, 1]
        C = [self.cX, self.cZ]
        LS = ['-.', ':']

        for type in range(2):

            np.random.seed(1)
            color = np.random.random([len(results[type]),3])*0.8 + 0.2

            for string in range(len(results[type])):
                C = color[string,:]

                topx = self.stab_data[results[type][string][0]][2] * 4
                topy = self.stab_data[results[type][string][0]][1] * 4
                botx = self.stab_data[results[type][string][1]][2] * 4
                boty = self.stab_data[results[type][string][1]][1] * 4

                plt.plot([topx + ploc[type], botx + ploc[type]], [topy + ploc[type], boty + ploc[type]], c = C, lw = self.slw, ls = LS[type])
                circle1 = plt.Circle((topx + ploc[type], topy + ploc[type]), 0.25, fill = True, facecolor = C)
                circle2 = plt.Circle((botx + ploc[type], boty + ploc[type]), 0.25, fill = True, facecolor = C)
                self.ax.add_artist(circle1)
                self.ax.add_artist(circle2)


        if self.plot_matching:
            plt.draw()
            print("Matchings plotted. Press on the plot to continue")
            plt.waitforbuttonpress()

    def plot_final(self, flips, array):
        '''
        param: flips        qubits that have flipped in value (y,x)
        param: arrays       data array of the (corrected) qubit states
        plots the applied stabilizer measurements over the lattices
        also, in the qubits that have flipped in value a smaller white circle is plotted

        optionally, the axis is clear and the final state of the lattice is plotted
        '''

        plt.figure(self.f.number)

        singles = []
        poly    = []


        for flip in flips:
            count = flips.count(flip)
            if count == 1:
                singles.append(flip)
            elif count % 2 == 1 and flip not in poly:
                singles.append(flip)
                poly.append(flip)

        Xer = []
        Zer = []
        Yer = []
        for flip in singles:
            if flip < self.size*self.size*2:
                Xer.append(flip)
            else:
                Zer.append(flip - self.size*self.size*2)

        for iX in Xer:
            if iX in Zer:
                Yer.append(iX)
        for iY in Yer:
            Xer.remove(iY)
            Zer.remove(iY)

        # Plot X errors
        for iX in Xer:
            (Y , X , TD) = self.qubit_data[iX][1:4]
            if TD == 0:
                circle = plt.Circle((X*4+3, Y*4+1), self.qsize2, fill = True, facecolor = self.cw, edgecolor = self.cx, linewidth = self.lw)
            else:
                circle = plt.Circle((X*4+1, Y*4+3), self.qsize2, fill = True, facecolor = self.cw, edgecolor = self.cx, linewidth = self.lw)
            self.ax.add_artist(circle)

        # Plot Z errors
        for iZ in Zer:
            (Y , X , TD) = self.qubit_data[iZ][1:4]
            if TD == 0:
                circle = plt.Circle((X*4+3, Y*4+1), self.qsize2, fill = True, facecolor = self.cw, edgecolor = self.cz, linewidth = self.lw)
            else:
                circle = plt.Circle((X*4+1, Y*4+3), self.qsize2, fill = True, facecolor = self.cw, edgecolor = self.cz, linewidth = self.lw)
            self.ax.add_artist(circle)

        # Plot Y errors
        for iY in Yer:
            (Y , X , TD) = self.qubit_data[iY][1:4]
            if TD == 0:
                circle = plt.Circle((X*4+3, Y*4+1), self.qsize2, fill = True, facecolor = self.cw, edgecolor = self.cy, linewidth = self.lw)
            else:
                circle = plt.Circle((X*4+1, Y*4+3), self.qsize2, fill = True, facecolor = self.cw, edgecolor = self.cy, linewidth = self.lw)
            self.ax.add_artist(circle)

        if self.plot_correction:
            plt.draw()
            print("Corrections plotted. Press on the plot to continue")
            plt.waitforbuttonpress()

        if self.plot_result:
            plt.cla()
            self.plot_lattice()
            self.plot_errors(array)
            print("Final lattice plotted. Press on the plot to continue")
