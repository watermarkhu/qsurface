import matplotlib.pyplot as plt
import numpy as np
import time

class toric_peeling_plot:

    def __init__(self, lat, plotstep_peel = False, plotstep_click = False):

        self.size = lat.size
        self.qua_loc = lat.qua_loc
        self.er_loc = lat.er_loc
        self.edge_data = lat.qubit_data
        self.anyon_data = lat.stab_data

        self.cl = [0.8, 0.8, 0.8]       # Line color
        self.cx = [0.9, 0.3, 0.3]       # X error color
        self.cz = [0.5, 0.5, 0.9]       # Z error color
        self.cX = [0.9, 0.7, 0.3]
        self.cZ = [0.3, 0.9, 0.3]


        self.qsize = 0.1
        self.lw = 2

        self.step = 0.01
        self.plotstep_peel = plotstep_peel
        self.plotstep_click = plotstep_click

        self.f = plt.figure(2, figsize = (10, 10))
        self.ax = plt.gca()
        self.ax.invert_yaxis()
        self.ax.set_aspect('equal')


        for y in range(self.size):
            y1 = y - 1/2
            for x in range(self.size):
                x1 = x - 1/2

                self.ax.plot([x, x], [y, y-1], c = self.cl, lw = self.lw, ls = '-')
                self.ax.plot([x1, x1+1], [y1, y1], c = self.cl, lw = self.lw, ls = '--')

                self.ax.plot([x, x-1], [y, y], c = self.cl, lw = self.lw, ls = '-')
                self.ax.plot([x1, x1], [y1, y1+1], c = self.cl, lw = self.lw, ls = '--')

        plt.ion()
        plt.show()

    '''
    ________________________________________________________________________________

    main plot functions

    '''


    def plot_lattice(self):

        '''
        :param qua_loc          locations of the find_anyons (hv, y, x)
        :param erasures         locations of the erasures (hv, y, x)
        plots the edges and anyons/vertices of the peeling algorithm on a new lattice
        the qubits are represented by the edges and anyons appear on the vertices

        '''

        plt.figure(self.f.number)

        for id in self.er_loc:
            (ertype, y, x, td) = self.edge_data[id][0:4]
            y1 = y-1/2
            x1 = x-1/2
            if td == 0:
                self.ax.plot([x, x], [y, y-1], c = self.cx, lw = self.lw, ls = '-')
                self.ax.plot([x1, x1+1], [y1, y1], c = self.cz, lw = self.lw, ls = '--')
            else:
                self.ax.plot([x, x-1], [y, y], c = self.cx, lw = self.lw, ls = '-')
                self.ax.plot([x1, x1], [y1, y1+1], c = self.cz, lw = self.lw, ls = '--')

        for id in self.qua_loc:
            (y, x) = self.anyon_data[id][1:3]

            if id < self.size **2:
                c = self.cx
            else:
                c = self.cz
                y = y-1/2
                x = x-1/2

            circle0 = plt.Circle((x, y), self.qsize, facecolor = c, linewidth = 0)
            self.ax.add_artist(circle0)

        plt.draw()
        print("Peeling lattice initiated. Press on the plot to continue")
        plt.waitforbuttonpress()

    def plot_growth(self, Fusion_edges):

        plt.figure(self.f.number)

        for id in Fusion_edges:
            (ertype, y, x, td) = self.edge_data[id][0:4]
            y1 = y-1/2
            x1 = x-1/2

            if ertype == 0 and td == 0:
                self.ax.plot([x, x], [y, y-1], c = self.cx, lw = self.lw, ls = '-')
            elif ertype == 0 and td == 1:
                self.ax.plot([x, x-1], [y, y], c = self.cx, lw = self.lw, ls = '-')
            elif ertype == 1 and td == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = self.cz, lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = self.cz, lw = self.lw, ls = '--')

        plt.draw()
        print("Clusters grown. Press on the plot to continue")
        plt.waitforbuttonpress()


    def plot_removed(self, rem_list):
        '''
        :param rem_list         list of edges
        plots the normal edge color over the edges that have been removed during the formation of the tree structure
        '''

        plt.figure(self.f.number)

        for edge in rem_list:

            (ertype, hv, y, x) = self.edge_data[edge][0:4]

            if ertype == 0:
                if hv == 0:
                    self.ax.plot([x, x], [y, y-1], c = self.cl, lw = self.lw, ls = '-')
                else:
                    self.ax.plot([x, x-1], [y, y], c = self.cl, lw = self.lw, ls = '-')

            if ertype == 1:
                y1 = y-1/2
                x1 = x-1/2
                if hv == 0:
                    self.ax.plot([x1, x1+1], [y1, y1], c = self.cl, lw = self.lw, ls = '--')
                else:
                    self.ax.plot([x1, x1], [y1, y1+1], c = self.cl, lw = self.lw, ls = '--')

        plt.draw()
        print("Tree-like structure formed. Press on the plot to continue")
        plt.waitforbuttonpress()

    def plot_matching(self, qua_loc, erasures, match_loc):
        '''
        :param qua_loc          locations of the find_anyons (hv, y, x)
        :param erasures         locations of the erasures (hv, y, x)
        :param matching         locations of the edges that remain in the matching (hv, y, x)

        plots the normal edge color over the edges that are removed during the peeling process
        plots the anyons again
        '''

        plt.figure(self.f.number)

        if self.plotstep_peel:


            for (y, x) in qua_loc[0]:
                circle = plt.Circle((x, y), self.qsize, facecolor = self.cx, linewidth = 0)
                self.ax.add_artist(circle)

            for (y, x) in qua_loc[1]:
                y1 = y - 1/2
                x1 = x - 1/2
                circle = plt.Circle((x1, y1), self.qsize, facecolor = self.cz, linewidth = 0)
                self.ax.add_artist(circle)
        else:

            for (hv, y, x) in [edge for edge in erasures if edge not in match_loc[0]]:
                if hv == 0:
                    self.ax.plot([x, x], [y, y-1], c = self.cl, lw = self.lw, ls = '-')
                else:
                    self.ax.plot([x, x-1], [y, y], c = self.cl, lw = self.lw, ls = '-')

            for (hv, y, x) in [edge for edge in erasures if edge not in match_loc[1]]:
                y1 = y - 1/2
                x1 = x - 1/2
                if hv == 0:
                    self.ax.plot([x1, x1+1], [y1, y1], c = self.cl, lw = self.lw, ls = '--')
                else:
                    self.ax.plot([x1, x1], [y1, y1+1], c = self.cl, lw = self.lw, ls = '--')

        plt.draw()
        print("Peeling completed. Press on the plot to continue")
        plt.waitforbuttonpress()




    '''
    ________________________________________________________________________________

    stepwise plot functions

    '''

    def plot_removed_step(self, edge):
        '''
        plots an edge that is to be removed from the plot
        1.  plots black edge as indication
        2.  plots normal edge color

        '''

        plt.figure(self.f.number)

        (ertype, hv, y, x) = self.edge_data[edge][0:4]

        if ertype == 0:
            if hv == 0:
                self.ax.plot([x, x], [y, y-1], c = 'k', lw = self.lw, ls = '-')
            else:
                self.ax.plot([x, x-1], [y, y], c = 'k', lw = self.lw, ls = '-')
        else:
            y1 = y-1/2
            x1 = x-1/2
            if hv == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = 'k', lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = 'k', lw = self.lw, ls = '--')

        plt.draw()
        if self.plotstep_click: plt.waitforbuttonpress()
        else: plt.pause(self.step)

        if ertype == 0:
            if hv == 0:
                self.ax.plot([x, x], [y, y-1], c = self.cl, lw = self.lw, ls = '-')
            else:
                self.ax.plot([x, x-1], [y, y], c = self.cl, lw = self.lw, ls = '-')
        else:
            y1 = y-1/2
            x1 = x-1/2
            if hv == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = self.cl, lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = self.cl, lw = self.lw, ls = '--')

    def plot_tree_step(self, edge):
        '''
        plots an edge that is confirmed into the tree structure
        changes color slightly

        '''

        plt.figure(self.f.number)

        (ertype, hv, y, x) = self.edge_data[edge][0:4]

        if ertype == 0:
            if hv == 0:
                self.ax.plot([x, x], [y, y-1], c = self.cX, lw = self.lw, ls = '-')
            else:
                self.ax.plot([x, x-1], [y, y], c = self.cX, lw = self.lw, ls = '-')
        else:
            y1 = y-1/2
            x1 = x-1/2
            if hv == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = self.cZ, lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = self.cZ, lw = self.lw, ls = '--')

        plt.draw()
        if self.plotstep_click: plt.waitforbuttonpress()
        else: plt.pause(self.step)

    def plot_strip_step(self, edge):
        '''
        plots an edge that is added tot the matching
        1.  plots black edge as indication
        2.  plots standard error edge color

        '''

        plt.figure(self.f.number)

        (ertype, hv, y, x) = self.edge_data[edge][0:4]

        if ertype == 0:
            if hv == 0:
                self.ax.plot([x, x], [y, y-1], c = 'k', lw = self.lw, ls = '-')
            else:
                self.ax.plot([x, x-1], [y, y], c = 'k', lw = self.lw, ls = '-')
        else:
            y1 = y-1/2
            x1 = x-1/2
            if hv == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = 'k', lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = 'k', lw = self.lw, ls = '--')


        plt.draw()
        if self.plotstep_click: plt.waitforbuttonpress()
        else: plt.pause(self.step)

        if ertype == 0:
            if hv == 0:
                self.ax.plot([x, x], [y, y-1], c = self.cx, lw = self.lw, ls = '-')
            else:
                self.ax.plot([x, x-1], [y, y], c = self.cx, lw = self.lw, ls = '-')
        else:
            y1 = y-1/2
            x1 = x-1/2
            if hv == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = self.cz, lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = self.cz, lw = self.lw, ls = '--')



    def plot_strip_step_anyon(self, ertype, loc, rem = 0):
        '''
        plot function for the flips of the anyons
        plots the anyon in white (removal) or normal error edge color (addition)
        '''

        y = loc[0]
        x = loc[1]

        if rem == 1:
            color = [1,1,1]
        else:
            if ertype == 0:
                color = self.cx
            else:
                color = self.cz

        if ertype == 0:
            circle = plt.Circle((x, y), self.qsize, facecolor = color, linewidth = 0)
            self.ax.add_artist(circle)
        else:
            y1 = y-1/2
            x1 = x-1/2
            circle = plt.Circle((x1, y1), self.qsize, facecolor = color, linewidth = 0)
            self.ax.add_artist(circle)

        plt.draw()
        if self.plotstep_click: plt.waitforbuttonpress()
        else: plt.pause(self.step)
