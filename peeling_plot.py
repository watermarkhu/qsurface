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

        self.cl = [0.2, 0.2, 0.2]       # Line color
        self.cx = [0.9, 0.3, 0.3]       # X error color
        self.cz = [0.5, 0.5, 0.9]       # Z error color
        self.Cx = [0.5, 0.1, 0.1]
        self.Cz = [0.1, 0.1, 0.5]
        self.cX = [0.9, 0.7, 0.3]
        self.cZ = [0.3, 0.9, 0.3]

        self.alpha = 0.3


        self.qsize = 0.1
        self.lw = 1

        self.plotstep_click = plotstep_click

        self.f = figure
        figure.set_figwidth(2*lat.plot_size)
        ax = figure.gca()
        ax.change_geometry(1, 2, 1)

        self.ax = figure.add_subplot(1, 2, 2)
        self.ax.cla()
        self.ax.invert_yaxis()
        self.ax.set_aspect('equal')

        plt.ion()
        plt.show()
        plt.axis('off')
        self.ax = self.f.gca()
        self.canvas = self.f.canvas

        self.edges = {}
        self.vertices = {}

        le_xv = Line2D([0], [0], lw=0, marker='o', color='w', mew=0, mfc=self.cx, ms=10, label='X-vertex')
        le_zv = Line2D([0], [0], lw=0, marker='o', color='w', mew=0, mfc=self.cz, ms=10, label='Z-vertex')
        le_xe = Line2D([0], [0], ls='-', lw=self.lw, color=self.cx, label='X-edge')
        le_ze = Line2D([0], [0], ls='--', lw=self.lw, color=self.cz, label='Z-edge')

        self.ax.legend(handles=[le_xv, le_zv, le_xe, le_ze], bbox_to_anchor=(1.15, 0.95), loc='upper right', ncol=1)


    def waitforkeypress(self, str=""):
        if str != "":
            str += " "
        print(str + "Press any key (on plot) to continue...")
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
        C1 = [self.cx, self.cz]
        C2 = [self.cX, self.cZ]
        LS = ["-", "--"]

        plt.sca(self.ax)

        for edge in self.G.E.values():

            (ertype, y, x, _) = edge.qID
            (_, y0, x0) = edge.vertices[0].sID
            (_, y1, x1) = edge.vertices[1].sID

            if ertype == 0:
                if y == self.size - 1:
                    y0 = self.size if y0 == 0 else y0
                    y1 = self.size if y1 == 0 else y1
                if x == self.size - 1:
                    x0 = self.size if x0 == 0 else x0
                    x1 = self.size if x1 == 0 else x1
            else:
                if y == 0:
                    y0 = -.5 if y0 == self.size - 1 else y0 + .5
                    y1 = -.5 if y1 == self.size - 1 else y1 + .5
                else:
                    y0 += .5
                    y1 += .5
                if x == 0:
                    x0 = -.5 if x0 == self.size - 1 else x0 + .5
                    x1 = -.5 if x1 == self.size - 1 else x1 + .5
                else:
                    x0 += .5
                    x1 += .5

            if edge.erasure:
                color = C1[ertype]
                alpha = 1
            else:
                color = self.cl
                alpha = self.alpha

            xm = (x0 + x1)/2
            ym = (y0 + y1)/2
            id0 = (edge.qID, edge.vertices[0].sID)
            id1 = (edge.qID, edge.vertices[1].sID)
            self.edges[id0] = self.ax.plot([x0, xm], [y0, ym], c=color, lw=self.lw, ls=LS[ertype], alpha=alpha)
            self.edges[id1] = self.ax.plot([xm, x1], [ym, y1], c=color, lw=self.lw, ls=LS[ertype], alpha=alpha)

        for vertex in self.G.V.values():

            (ertype, y, x) = vertex.sID
            if ertype == 1:
                y += .5
                x += .5

            if vertex.state:
                fill = True
                lw = self.lw
            else:
                fill = False
                lw = 0

            self.vertices[vertex.sID] = plt.Circle((x, y), self.qsize, facecolor=C2[ertype], linewidth=lw, edgecolor=C1[ertype], fill=fill)
            self.ax.add_artist(self.vertices[vertex.sID])

        self.canvas.blit(self.ax.bbox)
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

                edge0 = self.edges[(edge.qID, V0.sID)][0]
                edge1 = self.edges[(edge.qID, V1.sID)][0]
                edge0.set_color(self.cl)
                edge1.set_color(self.cl)
                edge0.set_alpha(self.alpha)
                edge1.set_alpha(self.alpha)
                self.ax.draw_artist(edge0)
                self.ax.draw_artist(edge1)

        self.canvas.blit(self.ax.bbox)
        self.waitforkeypress(str)


    def add_edge(self, edge, vertex):

        plt.figure(self.f.number)

        if edge.cluster == 0:

            halfedge = self.edges[(edge.qID, vertex.sID)][0]
            halfedge.set_alpha(0.5)
            if edge.qID[0] == 0:
                halfedge.set_color(self.Cx)
            else:
                halfedge.set_color(self.Cz)
            self.ax.draw_artist(halfedge)

        else:

            (V0, V1) = edge.vertices

            edge0 = self.edges[(edge.qID, V0.sID)][0]
            edge1 = self.edges[(edge.qID, V1.sID)][0]
            edge0.set_alpha(1)
            edge1.set_alpha(1)
            if edge.qID[0] == 0:
                edge0.set_color(self.cx)
                edge1.set_color(self.cx)
            else:
                edge0.set_color(self.cz)
                edge1.set_color(self.cz)
            self.ax.draw_artist(edge0)
            self.ax.draw_artist(edge1)

    def draw_plot(self, txt):

        self.canvas.blit(self.ax.bbox)
        if self.plotstep_click:
            self.waitforkeypress(txt)
        else:
            print(txt)


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
            text = "❌ remove"
            alpha = self.alpha
        elif type == "confirm":
            c1 = self.cx
            c2 = self.cz
            text = "☑ confirm"
            alpha = 1
        elif type == "peel":
            c1 = self.cl
            c2 = self.cl
            text = "❌ peeling"
            alpha = self.alpha
        elif type == "match":
            c1 = self.cX
            c2 = self.cZ
            text = "☑ matching"
            alpha = 1

        plt.sca(self.ax)

        (V0, V1) = edge.vertices

        (V0, V1) = edge.vertices

        edge0 = self.edges[(edge.qID, V0.sID)][0]
        edge1 = self.edges[(edge.qID, V1.sID)][0]
        edge0.set_alpha(1)
        edge1.set_alpha(1)
        edge0.set_color('k')
        edge1.set_color('k')
        self.ax.draw_artist(edge0)
        self.ax.draw_artist(edge1)

        (ertype, yb, xb) = V0.sID
        (ertype, yg, xg) = V1.sID

        self.canvas.blit(self.ax.bbox)

        line = text + " edge " + str(edge)
        if self.plotstep_click:
            self.waitforkeypress(line)
        else:
            print(line)


        edge0.set_alpha(alpha)
        edge1.set_alpha(alpha)
        if edge.qID[0] == 0:
            edge0.set_color(c1)
            edge1.set_color(c1)
        else:
            edge0.set_color(c2)
            edge1.set_color(c2)
        self.ax.draw_artist(edge0)
        self.ax.draw_artist(edge1)

    def plot_strip_step_anyon(self, vertex):
        '''
        plot function for the flips of the anyons
        plots the anyon in white (removal) or normal error edge color (addition)
        '''

        type, y, x = vertex.sID

        plotvertex = self.vertices[vertex.sID]

        if vertex.state:
            plotvertex.set_linewidth(self.lw)
        else:
            plotvertex.set_linewidth(0)

        self.ax.draw_artist(plotvertex)

        self.canvas.blit(self.ax.bbox)
