import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


class toric_peeling_plot:

    def __init__(self, lat, figure, plotstep_click=False):

        self.size = lat.size
        # self.qua_loc = lat.qua_loc
        # self.er_loc = lat.er_loc
        # self.edge_data = lat.edge_data
        # self.vertex_data = lat.vertex_data
        # self.num_vertex = lat.num_vertex

        self.G = lat.G

        self.cl = [0.8, 0.8, 0.8]       # Line color
        self.cx = [0.9, 0.3, 0.3]       # X error color
        self.cz = [0.5, 0.5, 0.9]       # Z error color
        self.cX = [0.9, 0.7, 0.3]
        self.cZ = [0.3, 0.9, 0.3]


        self.qsize = 0.1
        self.lw = 2

        self.step = 0.01
        self.plotstep_click = plotstep_click

        self.f = figure
        figure.set_figwidth(20)
        ax = figure.gca()
        ax.change_geometry(1, 2, 1)

        self.ax = figure.add_subplot(1, 2, 2)
        self.ax.cla()
        self.ax.invert_yaxis()
        self.ax.set_aspect('equal')

        plt.ion()
        plt.show()
        plt.axis('off')

        le_xv = Line2D([0], [0], lw=0, marker='o', color='w', mew=0, mfc=self.cx, ms=10, label='X-vertex')
        le_zv = Line2D([0], [0], lw=0, marker='o', color='w', mew=0, mfc=self.cz, ms=10, label='Z-vertex')
        le_xe = Line2D([0], [0], ls='-', lw=self.lw, color=self.cx, label='X-edge')
        le_ze = Line2D([0], [0], ls='--', lw=self.lw, color=self.cz, label='Z-edge')

        self.ax.legend(handles=[le_xv, le_zv, le_xe, le_ze], bbox_to_anchor=(1.15, 0.95), loc='upper right', ncol=1)


    def waitforkeypress(self, str):
        print(str, "Press any key (on plot) to continue...")
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
        plots the edges and anyons/vertices of the peeling algorithm on a new lattice
        the qubits are represented by the edges and anyons appear on the vertices

        '''
        C = [self.cx, self.cz]
        pos = [-.5, 0]

        plt.sca(self.ax)

        for ertype, (c, p) in enumerate(zip(C, pos)):
            for y in range(self.size):
                y1 = y-1/2
                for x in range(self.size):
                    x1 = x-1/2

                    if self.G.E[(ertype, y, x, 0)].erasure:
                        self.ax.plot([x, x], [y, y-1], c=self.cz, lw=self.lw, ls='--')
                        self.ax.plot([x1, x1+1], [y1, y1], c=self.cx, lw=self.lw, ls='-')
                    else:
                        self.ax.plot([x, x], [y, y-1], c=self.cl, lw=self.lw, ls='--')
                        self.ax.plot([x1, x1+1], [y1, y1], c=self.cl, lw=self.lw, ls='-')

                    if self.G.E[(ertype, y, x, 1)].erasure:
                        self.ax.plot([x, x-1], [y, y], c=self.cz, lw=self.lw, ls='--')
                        self.ax.plot([x1, x1], [y1, y1+1], c=self.cx, lw=self.lw, ls='-')
                    else:
                        self.ax.plot([x, x-1], [y, y], c=self.cl, lw=self.lw, ls='--')
                        self.ax.plot([x1, x1], [y1, y1+1], c=self.cl, lw=self.lw, ls='-')

        for ertype, (c, p) in enumerate(zip(C, pos)):
            for y in range(self.size):
                for x in range(self.size):
                    if self.G.V[(ertype, y, x)].state:
                        circle = plt.Circle((x + p, y + p), self.qsize, facecolor=c, linewidth=0)
                        self.ax.add_artist(circle)

        plt.draw()
        self.waitforkeypress("Peeling lattice initiated.")


    def plot_removed(self, str):
        '''
        :param rem_list         list of edges
        plots the normal edge color over the edges that have been removed during the formation of the tree structure
        '''

        plt.sca(self.ax)

        for edge in self.G.E.values():
            if edge.peeled and not edge.matching:

                (V0, V1) = edge.vertices
                (type, yb, xb) = V0.sID
                (type, yg, xg) = V1.sID

                if type == 0:
                    if yb == 0 and yg == self.size - 1:
                        yb = self.size
                    elif yb == self.size - 1 and yg == 0:
                        yg = self.size
                    if xb == 0 and xg == self.size - 1:
                        xb = self.size
                    elif xb == self.size - 1 and xg == 0:
                        xg = self.size
                    self.ax.plot([xb-.5, xg-.5], [yb-.5, yg-.5], c=[1, 1, 1], lw=self.lw, ls='-')
                    self.ax.plot([xb-.5, xg-.5], [yb-.5, yg-.5], c=self.cl, lw=self.lw, ls='-')
                else:
                    if yb == 0 and yg == self.size - 1:
                        yg = -1
                    elif yb == self.size - 1 and yg == 0:
                        yb = -1
                    if xb == 0 and xg == self.size - 1:
                        xg = -1
                    elif xb == self.size - 1 and xg == 0:
                        xb = -1
                    self.ax.plot([xb, xg], [yb, yg], c=[1, 1, 1], lw=self.lw, ls='-')
                    self.ax.plot([xb, xg], [yb, yg], c=self.cl, lw=self.lw, ls='--')

        plt.draw()
        self.waitforkeypress(str)


    def add_edge(self, edge, vertex=None):

        plt.figure(self.f.number)

        if edge.cluster == 0:
            V0 = vertex
            V1 = edge.vertices[1 - edge.vertices.index(vertex)]
            (type, yb, xb) = V0.sID
            (type, yt, xt) = V1.sID

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

            V0 = edge.vertices[0]
            V1 = edge.vertices[1]
            (type, yb, xb) = V0.sID
            (type, yg, xg) = V1.sID

            if type == 0:
                if yb == 0 and yg == self.size - 1:
                    yb = self.size
                elif yb == self.size - 1 and yg == 0:
                    yg = self.size
                if xb == 0 and xg == self.size - 1:
                    xb = self.size
                elif xb == self.size - 1 and xg == 0:
                    xg = self.size
            else:
                if yb == 0 and yg == self.size - 1:
                    yg = -1
                elif yb == self.size - 1 and yg == 0:
                    yb = -1
                if xb == 0 and xg == self.size - 1:
                    xg = -1
                elif xb == self.size - 1 and xg == 0:
                    xb = -1
            trans = 1

        if type == 0:
            self.ax.plot([xb-.5, xg-.5], [yb-.5, yg-.5], c=self.cx, lw=self.lw, ls='-', alpha=trans)
        else:
            self.ax.plot([xb, xg], [yb, yg], c=self.cz, lw=self.lw, ls='--', alpha=trans)


    def draw_plot(self, txt):

        plt.draw()
        if self.plotstep_click:
            self.waitforkeypress(txt)
        else:
            plt.pause(self.step)


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
        if type == "remove":
            c1 = self.cl
            c2 = self.cl
            text = "☒ remove"
        elif type == "confirm":
            c1 = self.cx
            c2 = self.cz
            text = "☑ confirm"
        elif type == "peel":
            c1 = self.cl
            c2 = self.cl
            text = "☒ peeling"
        elif type == "match":
            c1 = self.cX
            c2 = self.cZ
            text = "☑ matching"

        plt.sca(self.ax)

        (V0, V1) = edge.vertices

        (ertype, yb, xb) = V0.sID
        (ertype, yg, xg) = V1.sID

        if ertype == 0:
            if yb == 0 and yg == self.size - 1:
                yb = self.size
            elif yb == self.size - 1 and yg == 0:
                yg = self.size
            if xb == 0 and xg == self.size - 1:
                xb = self.size
            elif xb == self.size - 1 and xg == 0:
                xg = self.size
            self.ax.plot([xb-.5, xg-.5], [yb-.5, yg-.5], c=[1, 1, 1], lw=self.lw, ls='-')
            self.ax.plot([xb-.5, xg-.5], [yb-.5, yg-.5], c='k', lw=self.lw, ls='-')
        else:
            if yb == 0 and yg == self.size - 1:
                yg = -1
            elif yb == self.size - 1 and yg == 0:
                yb = -1
            if xb == 0 and xg == self.size - 1:
                xg = -1
            elif xb == self.size - 1 and xg == 0:
                xb = -1
            self.ax.plot([xb, xg], [yb, yg], c=[1, 1, 1], lw=self.lw, ls='-')
            self.ax.plot([xb, xg], [yb, yg], c='k', lw=self.lw, ls='--')

        plt.draw()

        if self.plotstep_click:
            self.waitforkeypress(text + " edge " + str(edge))
        else:
            plt.pause(self.step)

        if ertype == 0:
            self.ax.plot([xb-.5, xg-.5], [yb-.5, yg-.5], c=c1, lw=self.lw, ls='-')
        else:
            self.ax.plot([xb, xg], [yb, yg], c=c2, lw=self.lw, ls='--')


    def plot_strip_step_anyon(self, vertex):
        '''
        plot function for the flips of the anyons
        plots the anyon in white (removal) or normal error edge color (addition)
        '''

        type, y, x = vertex.sID

        if vertex.state:
            if type == 0:
                color = self.cx
            else:
                color = self.cz
        else:
            color = [1, 1, 1]


        if type == 0:
            circle = plt.Circle((x-.5, y-.5), self.qsize, facecolor=color, linewidth=0)
            self.ax.add_artist(circle)
        else:
            circle = plt.Circle((x, y), self.qsize, facecolor=color, linewidth=0)
            self.ax.add_artist(circle)

        plt.draw()
        if not self.plotstep_click:
            plt.pause(self.step)
