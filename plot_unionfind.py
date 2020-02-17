'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/toric_code
_____________________________________________

Plotting function for the surface/planar uf-lattice.
A plot_2D object is initialized for a graph_2D graph, which plots onto a 2D axis
A plot_3D object is initialized for a graph_3D graph, which plots onto a 3D axis

Plot_2D object is inherited by Plot_3D object. Both inherit from the plot_graph_lattice objects.
Plot colors, linewidths, alpha and scatter sizes are defined in the plot_graph_lattice.plot_2D object.
Otherwise only minor plotting functions are inherited.
'''

import matplotlib.pyplot as plt
import plot_graph_lattice as gp
import printing as pr

class plot_2D(gp.plot_2D):
    '''
    2D axis plot for both toric/planar uf-lattices.

    Plots the anyons as a scatter, and qubits as edges. Each graph round can be dynamically plotted to show the size and form of the clusters.

    Inherits from the plot_graph.lattice.plot_2D object. Uses colors and other plotting parameters defined there. Also inherits the following helper methods:

        draw_plot()
        legend_circle()
        draw_line()
    '''

    '''
    #########################################################################
                            Init legend
    '''

    def init_legend(self, x, y, loc="upper right"):
        '''
        Initilizes the legend of the plot.
        The qubits, errors and stabilizers are added.
        Aditional legend items can be inputted through the items paramter
        '''

        self.ax.set_title("{} uf-lattice".format(self.graph.__class__.__name__))

        le_xv = self.legend_circle("X-vertex", mew=0, mfc=self.cX)
        le_zv = self.legend_circle("Z-vertex", mew=0, mfc=self.cZ)
        le_xe = self.legend_circle("X-edge", lw=self.lw, color=self.cx, marker=None)
        le_ze = self.legend_circle("Z-edge", ls="--", lw=self.lw, color=self.cz, marker=None)
        self.ax.legend(
            handles=[le_xv, le_zv, le_xe, le_ze],
            bbox_to_anchor=(x, y),
            loc=loc,
            ncol=1,
    )

        '''
    #########################################################################
                            Initialize plot
    '''

    def init_plot(self, z=0):
        '''
        Initilizes a 2D plot of torc/planar uf-lattice
        '''

        plt.figure(self.f.number)
        plt.ion()
        plt.show()
        plt.axis("off")
        self.ax = self.f.gca()
        self.ax.invert_yaxis()
        self.ax.set_aspect("equal")

        self.canvas = self.f.canvas
        self.text = self.ax.text(0.5, 0, "", fontsize=10, va ="top", ha="center", transform=self.ax.transAxes)

        # Initate legend
        self.init_legend(1.25, 0.95)

        # Initate plot
        plt.sca(self.ax)

        for qubit in self.graph.Q[z].values():
            self.draw_edge0(qubit)
            self.draw_edge1(qubit)

        for stab in self.graph.S[z].values():
            self.draw_vertex(stab)

        pr.printlog("Peeling lattice initiated.")
        self.waitforkeypress()


    def draw_edge0(self, qubit):
        '''
        Draw lines of the X-edges of the qubit
        '''
        (type, y0, x0) = qubit.qID

        (py1, px1) = (
            (y0, (x0 + 1) % self.size)
            if type == 0
            else ((y0 + 1) % self.size, x0)
        )

        if y0 == self.size - 1:
            y0 = self.size if y0 == 0 else y0
            py1 = self.size if py1 == 0 else py1
        if x0 == self.size - 1:
            x0 = self.size if x0 == 0 else x0
            px1 = self.size if px1 == 0 else px1

        pxm, pym = (x0 + px1)/2,  (y0 + py1)/2

        color, alpha = (self.C1[0], 1) if qubit.erasure else (self.cl, self.alpha2)

        up1 = self.draw_line([x0,  pxm], [y0,  pym], Z=qubit.z, color=color, lw=self.lw, ls=self.LS[0], alpha=alpha)
        up2 = self.draw_line([pxm,  px1], [pym,  py1], Z=qubit.z, color=color, lw=self.lw, ls=self.LS[0], alpha=alpha)
        qubit.E[0].pu = [up1, up2]


    def draw_edge1(self, qubit):
        '''
        Draw lines of the Z-edges of the qubit
        '''

        (type, y0, x0) = qubit.qID

        (sy1, sx1) = (
            (y0, (x0 - 1) % self.size)
            if type == 1
            else ((y0 - 1) % self.size, x0)
        )

        if y0 == 0:
            y0 = -0.5 if y0 == self.size - 1 else y0 + 0.5
            sy1 = -0.5 if sy1 == self.size - 1 else sy1 + 0.5
        else:
            y0 += 0.5
            sy1 += 0.5
        if x0 == 0:
            x0 = -0.5 if x0 == self.size - 1 else x0 + 0.5
            sx1 = -0.5 if sx1 == self.size - 1 else sx1 + 0.5
        else:
            x0 += 0.5
            sx1 += 0.5

        sxm, sym = (x0 + sx1)/2,  (y0 + sy1)/2

        color, alpha = (self.C1[1], 1) if qubit.erasure else (self.cl, self.alpha2)

        up1 = self.draw_line([x0,  sxm], [y0,  sym], Z=qubit.z, color=color, lw=self.lw, ls=self.LS[1], alpha=alpha)
        up2 = self.draw_line([sxm,  sx1], [sym,  sy1], Z=qubit.z, color=color, lw=self.lw, ls=self.LS[1], alpha=alpha)
        qubit.E[1].pu = [up1, up2]


    def draw_vertex(self, stab):
        '''
        Draws a circle of the stab object
        '''

        (ertype, y, x) = stab.sID
        if ertype == 1:
            y += 0.5
            x += 0.5

        fill, lw = (1, self.lw) if stab.state else (0,0)

        stab.pu = plt.Circle(
            (x, y),
            self.qsizeU,
            facecolor=self.C2[ertype],
            linewidth=lw,
            edgecolor=self.C1[ertype],
            fill=fill,
            zorder=10
        )
        self.ax.add_artist(stab.pu)


    """
    #########################################################################
                            main plot functions
    """

    def plot_edge(self, edge, num, color, alpha):

        p_edge = edge.pu[num]
        p_edge.set_color(color)
        p_edge.set_alpha(alpha)
        self.ax.draw_artist(p_edge)


    def plot_removed(self, z=0):
        """
        plots the normal edge color over the edges that have been removed during the formation of the tree structure
        """
        for qubit in self.graph.Q[z].values():
            for edge in [qubit.E[0], qubit.E[1]]:
                if edge.peeled and not edge.matching:
                    self.plot_edge(edge, 0, self.cl ,self.alpha2)
                    self.plot_edge(edge, 1, self.cl ,self.alpha2)


    def add_edge(self, edge, vertex):
        '''
        Plots a recently half-grown or fully-grown edge
        '''
        if edge.support == 1:
            (ye, xe) = edge.qubit.qID[1:3]
            (yv, xv) = vertex.sID[1:3]
            id = 0 if (ye == yv and xe == xv) else 1
            color = self.Cx if edge.ertype ==0 else self.Cz
            self.plot_edge(edge, id, color, self.alpha)
            self.plot_edge(edge, 1-id, self.cl ,self.alpha2)

        else:
            color = self.cx if edge.ertype == 0 else self.cz
            self.plot_edge(edge, 0, color, 1)
            self.plot_edge(edge, 1, color, 1)

    """
    #########################################################################
                            stepwise plot functions
    """

    def plot_edge_step(self, edge, type):
        """
        plots an edge that is to be removed from the plot
        1.  plots black edge as indication
        2.  plots normal edge color

        """
        if type == "remove":
            c1 = self.cl
            c2 = self.cl
            text = "☒ remove"
            alpha = self.alpha2
        elif type == "confirm":
            c1 = self.cx
            c2 = self.cz
            text = "☑ confirm"
            alpha = 1
        elif type == "peel":
            c1 = self.cl
            c2 = self.cl
            text = "☒ peeling"
            alpha = self.alpha2
        elif type == "match":
            c1 = self.cX
            c2 = self.cZ
            text = "☑ matching"
            alpha = 1

        plt.sca(self.ax)

        self.plot_edge(edge, 0, "k", 1)
        self.plot_edge(edge, 1, "k", 1)

        line = text + " edge " + str(edge)
        self.draw_plot(line)

        color = c1 if edge.ertype == 0 else c2
        self.plot_edge(edge, 0, color, alpha)
        self.plot_edge(edge, 1, color, alpha)


    def plot_strip_step_anyon(self, stab):
        """
        plot function for the flips of the anyons
        plots the anyon in white (removal) or normal error edge color (addition)
        """

        if stab.state:
            stab.pu.set_linewidth(self.lw)
        else:
            stab.pu.set_linewidth(0)

        self.ax.draw_artist(stab.pu)


class plot_3D(plot_2D, gp.plot_3D):
    '''
    3D axis plot for both toric/planar uf-lattices.

    Plots the anyons as a scatter, and qubits as edges. Each graph round can be dynamically plotted to show the size and form of the clusters.

    Inherits from the plot_graph.lattice.plot_2D object. Uses colors and other plotting parameters defined there. Also inherits the following helper methods:

        draw_plot()
        legend_circle()
        init_axis()
        set_axes_equal()
        draw_line()
        plot_scatter()
    '''

    '''
    #########################################################################
                            Initalize plot
    '''

    def init_plot(self, *args, **kwargs):
        '''
        Initializes 3D plot of toric/planar lattice
        Stabilizers are plotted with Axes3D.line objects
        Qubits are plotted with Axes3D.scatter objects
        '''

        self.init_axis(1, 1, 1, 0, 0, 0)

        for layer in self.graph.Q.values():
            for qubit in layer.values():
                self.draw_edge0(qubit)
                self.draw_edge1(qubit)

        for layer in self.graph.G.values():
            for bridge in layer.values():
                self.draw_bridge(bridge)

        self.scatter = {}
        for z, layer in self.graph.S.items():
            X, Y, fC, eC, i, stab_locs = [], [], [], [], 0, {}

            for stab in layer.values():

                (ertype, y, x) = stab.sID

                if ertype == 0:
                    X.append(x)
                    Y.append(y)
                else:
                    X.append(x+.5)
                    Y.append(y+.5)

                if stab.state:
                    fC.append(self.C2[ertype] + [1])
                    eC.append(self.C1[ertype] + [1])
                else:
                    fC.append([0, 0, 0, 0])
                    eC.append([0, 0, 0, 0])

                stab_locs[stab.sID] = i
                i += 1

            self.scatter[z] = {
                "plot"  : None,
                "locs"  : stab_locs,
                "fC"    : fC,
                "eC"    : eC,
                "X"     : X,
                "Y"     : Y,
                "Z"     : z
            }
            self.plot_scatter(z)

        self.init_legend(1.05, 0.95)
        self.set_axes_equal()
        self.draw_plot("Peeling lattice plotted.")


    def draw_bridge(self, bridge):
        '''
        Draw lines of the vertical edges connecting the layers
        '''

        (ertype, y, x), z = bridge.qID, bridge.z
        if ertype == 1:
            y += 0.5
            x += 0.5

        up1 = self.draw_line([x,  x], [y,  y], Z=[z, z-.5], color=self.cl, lw=self.lw, ls=self.LS[ertype], alpha=self.alpha2)
        up2 = self.draw_line([x,  x], [y,  y], Z=[z-.5, z-1], color=self.cl, lw=self.lw, ls=self.LS[ertype], alpha=self.alpha2)

        bridge.E.pu = [up1, up2]

    '''
    #########################################################################
                            Plotting functions
    '''
    def plot_removed(self):
        """
        plots the normal edge color over the edges that have been removed during the formation of the tree structure
        """
        for z in self.graph.Q:
            super().plot_removed(z)
        for z in self.graph.G:
            for bridge in self.graph.G[z].values():
                edge = bridge.E
                if edge.peeled and not edge.matching:
                    self.plot_edge(edge, 0, self.cl ,self.alpha)
                    self.plot_edge(edge, 1, self.cl ,self.alpha)


    def add_edge(self, edge, vertex):
        '''
        Plots a recently half-grown or fully-grown edge
        '''
        if edge.support == 1:
            (ye, xe), ze = edge.qubit.qID[1:3], edge.z
            (yv, xv), zv = vertex.sID[1:3], vertex.z

            if edge.edge_type == 0:
                id = 0 if (ye == yv and xe == xv) else 1
            else:
                id = 0 if ze == zv else 1
            color = self.Cx if edge.ertype ==0 else self.Cz
            self.plot_edge(edge, id, color, self.alpha)
            self.plot_edge(edge, 1-id, self.cl, self.alpha2)
        else:
            color = self.cx if edge.ertype == 0 else self.cz
            self.plot_edge(edge, 0, color, 1)
            self.plot_edge(edge, 1, color, 1)


    def plot_strip_step_anyon(self, stab):
        """
        plot function for the flips of the anyons
        plots the anyon in white (removal) or normal error edge color (addition)
        """

        loc = self.scatter[stab.z]["locs"][stab.sID]
        ertype = stab.sID[0]


        if stab.state:
            self.scatter[stab.z]["eC"][loc] = self.C1[ertype] + [1]
        else:
            self.scatter[stab.z]["eC"][loc] = [0, 0, 0, 0]

        self.plot_scatter(stab.z)
