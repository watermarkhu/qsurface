'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

Plotting function for the surface/planar uf-lattice.
A plot_2D object is initialized for a graph_2D graph, which plots onto a 2D axis
A plot_3D object is initialized for a graph_3D graph, which plots onto a 3D axis`

Plot_2D object is inherited by Plot_3D object. Both inherit from the plot_graph_lattice objects.
Plot colors, linewidths, alpha and scatter sizes are defined in the plot_graph_lattice.plot_2D object.
Otherwise only minor plotting functions are inherited.
'''

import matplotlib.pyplot as plt
from . import plot_graph_lattice as gp


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
        le_xe = self.legend_circle("X-edge", ls="--", lw=self.linewidth, color=self.cx, marker=None)
        le_ze = self.legend_circle("Z-edge", ls="-", lw=self.linewidth, color=self.cz, marker=None)
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
        plt.sca(self.ax)
        self.init_axis(0-.2, self.size+.2)
        plt.setp(self.rax, visible=0)

        for qubit in self.graph.Q[z].values():
            if qubit.erasure:
                self.draw_edge(qubit, 0)
                self.draw_edge(qubit, 1)
            else:
                qubit.E[0].pu = None
                qubit.E[1].pu = None

        for stab in self.graph.S[z].values():

            if stab.state:
                self.draw_vertex(stab)
            else:
                stab.pu = None

        self.init_legend(1.25, 0.95)
        self.canvas.draw()
        self.draw_plot()


    def get_edge_data(self, ertype, type, y0, x0):

        if ertype == 1:
            (y1, x1) = (
                (y0, (x0 + 1) % self.size)
                if type == 0
                else ((y0 + 1) % self.size, x0)
            )

            if y0 == self.size - 1:
                y0 = self.size if y0 == 0 else y0
                y1 = self.size if y1 == 0 else y1
            if x0 == self.size - 1:
                x0 = self.size if x0 == 0 else x0
                x1 = self.size if x1 == 0 else x1

            xm, ym = (x0 + x1)/2,  (y0 + y1)/2

        else:
            (y1, x1) = (
                (y0, (x0 - 1) % self.size)
                if type == 1
                else ((y0 - 1) % self.size, x0)
            )

            if y0 == 0:
                y0 = -0.5 if y0 == self.size - 1 else y0 + 0.5
                y1 = -0.5 if y1 == self.size - 1 else y1 + 0.5
            else:
                y0 += 0.5
                y1 += 0.5
            if x0 == 0:
                x0 = -0.5 if x0 == self.size - 1 else x0 + 0.5
                x1 = -0.5 if x1 == self.size - 1 else x1 + 0.5
            else:
                x0 += 0.5
                x1 += 0.5

            xm, ym = (x0 + x1)/2,  (y0 + y1)/2

        return x0, y0, xm, ym, x1, y1


    def draw_edge(self, qubit, ertype):
        '''
        Draw lines of the X-edges of the qubit
        '''
        color, alpha = (self.C1[ertype], 1) if qubit.erasure else (self.cl, self.alpha2)

        (type, y0, x0) = qubit.qID

        x0, y0, xm, ym, x1, y1 = self.get_edge_data(ertype, type, y0, x0)

        up1 = self.draw_line([x0,  xm], [y0,  ym], Z=qubit.z, color=color, lw=self.linewidth, ls=self.LS[ertype-1], alpha=alpha)
        up2 = self.draw_line([xm,  x1], [ym,  y1], Z=qubit.z, color=color, lw=self.linewidth, ls=self.LS[ertype-1], alpha=alpha)
        up1.object = up2.object = qubit.E[ertype]
        qubit.E[ertype].pu = [up1, up2]


    def draw_vertex(self, stab):
        '''
        Draws a circle of the stab object
        '''

        (ertype, y, x) = stab.sID
        if ertype == 1:
            y += 0.5
            x += 0.5

        fc, lw = (self.C2[ertype], self.linewidth) if stab.state else (None ,0)

        stab.pu = plt.scatter(
            x, y,
            s = self.scatter_size,
            facecolor=fc,
            linewidth=lw,
            edgecolor=self.C1[ertype],
            zorder=10,
            picker = self.pick
        )
        stab.pu.object = stab


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
                    self.new_attributes(edge.pu[0], dict(color=self.cl, alpha=self.alpha2))
                    self.new_attributes(edge.pu[1], dict(color=self.cl, alpha=self.alpha2))


    def add_edge(self, edge, vertex):
        '''
        Plots a recently half-grown or fully-grown edge
        '''
        if edge.support == 1:
            if not edge.pu:
                self.draw_edge(edge.qubit, edge.ertype)

            (ye, xe) = edge.qubit.qID[1:3]
            (yv, xv) = vertex.sID[1:3]
            id = 0 if (ye == yv and xe == xv) else 1
            color = self.Cx if edge.ertype ==0 else self.Cz
            self.new_attributes(edge.pu[id], dict(color=color, alpha=self.alpha))
            self.new_attributes(edge.pu[1-id], dict(color=self.cl, alpha=self.alpha2))
        elif edge.support == 2:
            color = self.cx if edge.ertype == 0 else self.cz
            self.new_attributes(edge.pu[0], dict(color=color, alpha=1), 1)
            self.new_attributes(edge.pu[1], dict(color=color, alpha=1), 1)
        else:
            self.new_attributes(edge.pu[0], dict(color=self.cw, alpha=0), 1)
            self.new_attributes(edge.pu[1], dict(color=self.cw, alpha=0), 1)

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

        line = text + " edge " + str(edge)
        self.new_iter(line)

        color = c1 if edge.ertype == 0 else c2
        self.new_attributes(edge.pu[0], dict(color=color, alpha=alpha))
        self.new_attributes(edge.pu[1], dict(color=color, alpha=alpha))

        self.draw_plot()


    def plot_strip_step_anyon(self, stab):
        """
        plot function for the flips of the anyons
        plots the anyon in white (removal) or normal error edge color (addition)
        """
        lw = self.linewidth if stab.state else 0
        if not stab.pu:
            self.draw_vertex(stab)
            self.new_attributes(stab.pu, dict(linewidth=lw, facecolor=[1,1,1,0]))
        else:
            self.new_attributes(stab.pu, dict(linewidth=lw))





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

    Method resoluation order is defined as:

    plot_3D -> plot_2D -> plot_graph_lattice.plot_3D -> plot_graph_lattice.plot_2D
    '''

    '''
    #########################################################################
                            Initalize plot
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha2 = 0.01

    def init_plot(self, *args, **kwargs):
        '''
        Initializes 3D plot of toric/planar lattice
        Stabilizers are plotted with Axes3D.line objects
        Qubits are plotted with Axes3D.scatter objects
        '''

        self.init_axis(0, self.size, 1)
        plt.setp(self.rax, visible=0)

        for layer in self.graph.Q.values():
            for qubit in layer.values():
                if qubit.erasure:
                    self.draw_edge(qubit, 0)
                    self.draw_edge(qubit, 1)
                else:
                    qubit.E[0].pu = None
                    qubit.E[1].pu = None

        for layer in self.graph.G.values():
            for bridge in layer.values():
                bridge.E.pu = None

        for Z, layer in self.graph.S.items():
            for stab in layer.values():
                (ertype, y, x) = stab.sID
                X, Y = (x, y) if ertype == 0 else (x+.5, y+.5)
                if stab.state:
                    (stab.pu, _) = self.plot_scatter(X, Y, Z, object=stab, facecolor=self.C2[ertype], edgecolor=self.C1[ertype])
                else:
                    stab.pu = {
                        "pos"       : (X, Y, Z),
                        "edgecolor" : self.C2[ertype],
                        "facecolor" : self.C1[ertype],
                        "object"    : stab
                    }

        self.init_legend(1.05, 0.95)
        self.set_axes_equal()
        self.canvas.draw()
        self.draw_plot()


    def draw_bridge(self, bridge):
        '''
        Draw lines of the vertical edges connecting the layers
        '''
        (ertype, y, x), z = bridge.qID, bridge.z
        if ertype == 1:
            y += 0.5
            x += 0.5

        up1 = self.draw_line([x,  x], [y,  y], Z=[z, z-.5], color=self.cl, lw=self.linewidth, ls=self.LS[ertype], alpha=self.alpha2)
        up2 = self.draw_line([x,  x], [y,  y], Z=[z-.5, z-1], color=self.cl, lw=self.linewidth, ls=self.LS[ertype], alpha=self.alpha2)
        up1.object = up2.object = bridge

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
                    self.new_attributes(edge.pu[0], dict(color=self.cl, alpha=self.alpha2))
                    self.new_attributes(edge.pu[1], dict(color=self.cl, alpha=self.alpha2))


    def add_edge(self, edge, vertex):
        '''
        Plots a recently half-grown or fully-grown edge
        '''
        if edge.support == 1:
            (ye, xe), ze = edge.qubit.qID[1:3], edge.z
            (yv, xv), zv = vertex.sID[1:3], vertex.z

            color = self.Cx if (edge.ertype == edge.edge_type) else self.Cz

            if edge.edge_type == 0:
                id = 0 if (ye == yv and xe == xv) else 1
            else:
                id = 0 if ze == zv else 1

            if not edge.pu:
                if edge.edge_type == 0:
                    self.draw_edge(edge.qubit, edge.ertype)
                else:
                    self.draw_bridge(edge.qubit)

            self.new_attributes(edge.pu[id], dict(color=color, alpha=self.alpha))
            self.new_attributes(edge.pu[1-id], dict(color=self.cl, alpha=self.alpha2))

        elif edge.support == 2:
            color = self.cx if edge.ertype == edge.edge_type else self.cz
            self.new_attributes(edge.pu[0], dict(color=color, alpha=1), 1)
            self.new_attributes(edge.pu[1], dict(color=color, alpha=1), 1)
        else:
            self.new_attributes(edge.pu[0], dict(color=self.cw, alpha=0), 1)
            self.new_attributes(edge.pu[1], dict(color=self.cw, alpha=0), 1)



    # def plot_strip_step_anyon(self, stab):
    #     """
    #     plot function for the flips of the anyons
    #     plots the anyon in white (removal) or normal error edge color (addition)
    #     """
    #     lw = self.linewidth if stab.state else 0

    #     if "key" not in stab.pu:
    #         self.new_attributes(stab.pu, dict(linewidth=lw))
    #     else:
    #         self.new_attributes(stab.pu, dict(edgecolor=self.C1[stab.sID[0]]))


    def plot_strip_step_anyon(self, stab):
        """
        plot function for the flips of the anyons
        plots the anyon in white (removal) or normal error edge color (addition)
        """
        lw = self.linewidth if stab.state else 0
        if "key" not in stab.pu:
            self.new_attributes(stab.pu, dict(linewidth=lw, edgecolor=stab.pu["facecolor"]))
        else:
            self.new_attributes(stab.pu, dict(linewidth=lw, edgecolor=[1,1,1,0]))

