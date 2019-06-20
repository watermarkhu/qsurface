import matplotlib.pyplot as plt


class toric_peeling_plot:

    def __init__(self, lat, figure, plotstep_peel=False, plotstep_click=False):

        self.size = lat.size
        self.qua_loc = lat.qua_loc
        self.er_loc = lat.er_loc
        self.edge_data = lat.edge_data
        self.stab_data = lat.stab_data
        self.num_stab = lat.num_stab

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

        self.f = figure
        figure.set_figwidth(20)
        ax = figure.gca()
        ax.change_geometry(1, 2, 1)

        self.ax = figure.add_subplot(1, 2, 2)
        self.ax.cla()
        self.ax.invert_yaxis()
        self.ax.set_aspect('equal')


        for y in range(self.size):
            y1 = y - 1/2
            for x in range(self.size):
                x1 = x - 1/2

                self.ax.plot([x, x], [y, y-1], c=self.cl, lw=self.lw, ls='-')
                self.ax.plot([x1, x1+1], [y1, y1], c=self.cl, lw=self.lw, ls='--')

                self.ax.plot([x, x-1], [y, y], c=self.cl, lw=self.lw, ls='-')
                self.ax.plot([x1, x1], [y1, y1+1], c=self.cl, lw=self.lw, ls='--')

        plt.ion()
        plt.show()

    def waitforkeypress(self, str):
        print(str, "Press any key to continue...")
        keyboardClick = False
        while not keyboardClick:
            keyboardClick = plt.waitforbuttonpress(120)

    '''
    ________________________________________________________________________________

    main plot functions

    '''


    def plot_lattice(self):

        '''
        :param qua_loc          locations of the find_anyons (hv, y, x)
        :param erasures         locations of the erasures (hv, y, x)
        plots the edges and anyons/stabs of the peeling algorithm on a new lattice
        the qubits are represented by the edges and anyons appear on the stabs

        '''

        plt.sca(self.ax)

        for id in self.er_loc:
            (ertype, y, x, td) = self.edge_data[id][0:4]
            y1 = y-1/2
            x1 = x-1/2
            if td == 0:
                self.ax.plot([x, x], [y, y-1], c=self.cx, lw=self.lw, ls='-')
                self.ax.plot([x1, x1+1], [y1, y1], c=self.cz, lw=self.lw, ls='--')
            else:
                self.ax.plot([x, x-1], [y, y], c=self.cx, lw=self.lw, ls='-')
                self.ax.plot([x1, x1], [y1, y1+1], c=self.cz, lw=self.lw, ls='--')

        for id in self.qua_loc:
            (y, x) = self.stab_data[id][1:3]

            if id < self.size ** 2:
                c = self.cx
            else:
                c = self.cz
                y = y-1/2
                x = x-1/2

            circle0 = plt.Circle((x, y), self.qsize, facecolor=c, linewidth=0)
            self.ax.add_artist(circle0)

        plt.draw()
        self.waitforkeypress("Peeling lattice initiated.")


    def add_edge(self, edge):

        plt.figure(self.f.number)

        clusters = list(edge.halves.values())
        stabs = list(edge.halves.keys())

        if None in clusters:
            growindex = clusters.index(None)
            V0 = stabs[1 - growindex]
            V1 = stabs[growindex]
            (yb, xb) = V0.loc
            (yt, xt) = V1.loc

            if yb == 0 and yt == self.size - 1:
                yg = -0.5
            elif yb == self.size - 1 and yt == 0:
                yg = self.size - 0.5
            else:
                yg = (yt+yb)/2

            if xb == 0 and xt == self.size - 1:
                xg = -0.5
            elif xb == self.size - 1 and xt == 0:
                xg = self.size - 0.5
            else:
                xg = (xt+xb)/2

            trans = 0.3
        else:

            V0 = stabs[0]
            V1 = stabs[1]
            (yb, xb) = V0.loc
            (yg, xg) = V1.loc

            if V0.sID < self.num_stab/2:
                if yb == 0 and yg == self.size - 1:
                    yg = -1
                elif yb == self.size - 1 and yg == 0:
                    yb = -1
                if xb == 0 and xg == self.size - 1:
                    xg = -1
                elif xb == self.size - 1 and xg == 0:
                    xb = -1
            else:
                if yb == 0 and yg == self.size - 1:
                    yb = self.size
                elif yb == self.size - 1 and yg == 0:
                    yg = self.size
                if xb == 0 and xg == self.size - 1:
                    xb = self.size
                elif xb == self.size - 1 and xg == 0:
                    xg = self.size
            trans = 1

        if V0.sID < self.num_stab/2:
            self.ax.plot([xb, xg], [yb, yg], c=self.cx, lw=self.lw, ls='-', alpha=trans)
        else:
            self.ax.plot([xb-1/2, xg-1/2], [yb-1/2, yg-1/2], c=self.cz, lw=self.lw, ls='--', alpha=trans)


    def draw_plot(self, txt):

        plt.draw()
        if self.plotstep_click:
            self.waitforkeypress(txt)
        else:
            plt.pause(self.step)


    def plot_removed(self, rem_list, str):
        '''
        :param rem_list         list of edges
        plots the normal edge color over the edges that have been removed during the formation of the tree structure
        '''

        plt.sca(self.ax)

        for edge in rem_list:

            (V0, V1) = list(edge.halves.keys())
            (yb, xb) = V0.loc
            (yg, xg) = V1.loc

            if V0.sID < self.num_stab/2:
                if yb == 0 and yg == self.size - 1:
                    yg = -1
                elif yb == self.size - 1 and yg == 0:
                    yb = -1
                if xb == 0 and xg == self.size - 1:
                    xg = -1
                elif xb == self.size - 1 and xg == 0:
                    xb = -1
                self.ax.plot([xb, xg], [yb, yg], c=[1, 1, 1], lw=self.lw, ls='-')
                self.ax.plot([xb, xg], [yb, yg], c=self.cl, lw=self.lw, ls='-')
            else:
                if yb == 0 and yg == self.size - 1:
                    yb = self.size
                elif yb == self.size - 1 and yg == 0:
                    yg = self.size
                if xb == 0 and xg == self.size - 1:
                    xb = self.size
                elif xb == self.size - 1 and xg == 0:
                    xg = self.size
                self.ax.plot([xb-1/2, xg-1/2], [yb-1/2, yg-1/2], c=[1, 1, 1], lw=self.lw, ls='-')
                self.ax.plot([xb-1/2, xg-1/2], [yb-1/2, yg-1/2], c=self.cl, lw=self.lw, ls='--')


        plt.draw()
        self.waitforkeypress(str)

    '''
    ________________________________________________________________________________

    stepwise plot functions

    '''

    def plot_edge_step(self, edge, type):
        '''
        plots an edge that is to be removed from the plot
        1.  plots black edge as indication
        2.  plots normal edge color

        '''
        if type in ["remove", "peel"]:
            c1 = self.cl
            c2 = self.cl
        elif type == "tree":
            c1 = self.cX
            c2 = self.cZ
        elif type == "confirm":
            c1 = self.cx
            c2 = self.cz

        plt.sca(self.ax)


        (V0, V1) = list(edge.halves.keys())
        (yb, xb) = V0.loc
        (yg, xg) = V1.loc

        if V0.sID < self.num_stab/2:
            if yb == 0 and yg == self.size - 1:
                yg = -1
            elif yb == self.size - 1 and yg == 0:
                yb = -1
            if xb == 0 and xg == self.size - 1:
                xg = -1
            elif xb == self.size - 1 and xg == 0:
                xb = -1
            self.ax.plot([xb, xg], [yb, yg], c=[1, 1, 1], lw=self.lw, ls='-')
            self.ax.plot([xb, xg], [yb, yg], c='k', lw=self.lw, ls='-')
        else:
            if yb == 0 and yg == self.size - 1:
                yb = self.size
            elif yb == self.size - 1 and yg == 0:
                yg = self.size
            if xb == 0 and xg == self.size - 1:
                xb = self.size
            elif xb == self.size - 1 and xg == 0:
                xg = self.size
            self.ax.plot([xb-1/2, xg-1/2], [yb-1/2, yg-1/2], c=[1, 1, 1], lw=self.lw, ls='-')
            self.ax.plot([xb-1/2, xg-1/2], [yb-1/2, yg-1/2], c='k', lw=self.lw, ls='--')

        plt.draw()
        if self.plotstep_click:
            self.waitforkeypress(type + " edge qID #" + str(edge))
        else:
            plt.pause(self.step)

        if V0.sID < self.num_stab/2:
            self.ax.plot([xb, xg], [yb, yg], c=c1, lw=self.lw, ls='-')
        else:
            self.ax.plot([xb-1/2, xg-1/2], [yb-1/2, yg-1/2], c=c2, lw=self.lw, ls='--')


    def plot_strip_step_anyon(self, stab):
        '''
        plot function for the flips of the anyons
        plots the anyon in white (removal) or normal error edge color (addition)
        '''

        y, x = stab.loc
        ertype = 0 if stab.sID < self.num_stab/2 else 1

        if stab.anyon:
            if ertype == 0:
                color = self.cx
            else:
                color = self.cz
        else:
            color = [1, 1, 1]


        if ertype == 0:
            circle = plt.Circle((x, y), self.qsize, facecolor=color, linewidth=0)
            self.ax.add_artist(circle)
        else:
            y1 = y-1/2
            x1 = x-1/2
            circle = plt.Circle((x1, y1), self.qsize, facecolor=color, linewidth=0)
            self.ax.add_artist(circle)

        plt.draw()
        if not self.plotstep_click:
            plt.pause(self.step)
