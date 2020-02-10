from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import random


class plot_2D:
    def __init__(self, graph, z=0, plot_size=8, line_width=0.5, **kwargs):

        self.plot_base = 1
        self.plot_error = 1
        self.plot_anyons = 1
        self.plot_matching = 1
        self.plot_correction = 1
        self.plot_result = 1
        self.size = graph.size
        self.graph = graph
        self.plot_size = plot_size

        self.qsize = 0.5
        self.qsize2 = 0.25
        self.qsizeE = 0.7
        self.lw = line_width
        self.slw = 2

        self.stabs = {}
        self.qubits = {}

        # Define colors
        self.cw = [1, 1, 1]
        self.cl = [0.8, 0.8, 0.8]  # Line color
        self.cc = [0.7, 0.7, 0.7]  # Qubit color
        self.cx = [0.9, 0.3, 0.3]  # X error color
        self.cz = [0.5, 0.5, 0.9]  # Z error color
        self.cy = [0.9, 0.9, 0.5]  # Y error color
        self.cX = [0.9, 0.7, 0.3]  # X quasiparticle color
        self.cZ = [0.3, 0.9, 0.3]  # Z quasiparticle color
        self.cE = [0.3, 0.5, 0.9]  # Erasure color

        self.f = plt.figure(figsize=(self.plot_size, self.plot_size))

        self.init_plot(z)

    def init_plot(self, z=0):

        plt.figure(self.f.number)

        # Initiate figure
        plt.ion()
        plt.cla()
        plt.show()
        plt.axis("off")
        self.ax = self.f.gca()
        self.canvas = self.f.canvas
        self.ax.invert_yaxis()
        self.ax.set_aspect("equal")
        self.text = self.ax.text(0.5, 0, "", fontsize=10, va ="top", ha="center", transform=self.ax.transAxes)

        # Initate legend
        le_qubit = Line2D(
            [0],
            [0],
            lw=0,
            marker="o",
            color="w",
            mec="k",
            mew=2,
            mfc="w",
            ms=10,
            label="Qubit",
        )
        le_xer = Line2D(
            [0],
            [0],
            lw=0,
            marker="o",
            color="w",
            mec="k",
            mew=2,
            mfc=self.cx,
            ms=10,
            label="X-error",
        )
        le_zer = Line2D(
            [0],
            [0],
            lw=0,
            marker="o",
            color="w",
            mec="k",
            mew=2,
            mfc=self.cz,
            ms=10,
            label="Y-error",
        )
        le_yer = Line2D(
            [0],
            [0],
            lw=0,
            marker="o",
            color="w",
            mec="k",
            mew=2,
            mfc=self.cy,
            ms=10,
            label="Z-error",
        )
        le_err = Line2D(
            [0],
            [0],
            lw=0,
            marker="$\u25CC$",
            color="w",
            mec=self.cE,
            mew=1,
            mfc="w",
            ms=12,
            label="Erasure",
        )
        le_ver = Line2D([0], [0], ls="-", lw=self.lw, color=self.cX, label="Vertex")
        le_pla = Line2D([0], [0], ls="--", lw=self.lw, color=self.cZ, label="Plaquette")
        self.lh = [le_qubit, le_xer, le_zer, le_yer, le_err, le_ver, le_pla]

        legend = plt.legend(
            handles=self.lh, bbox_to_anchor=(-0.25, 0.95), loc="upper left", ncol=1
        )
        self.ax.add_artist(legend)

        # Plot empty lattice
        # Loop over all indices

        def plot_stab(neighbor, y, x, type, alpha=1):
            y += 2*type
            x += 2*type
            ls = "-" if type == 0 else "--"
            if neighbor == "w":
                return plt.plot(
                    [x + 0, x + 1], [y + 1, y + 1], c=self.cl, lw=self.lw, ls=ls, alpha=alpha
                )
            elif neighbor == "e":
                 return plt.plot(
                    [x + 1, x + 2], [y + 1, y + 1], c=self.cl, lw=self.lw, ls=ls, alpha=alpha
                )
            elif neighbor == "n":
                return plt.plot(
                    [x + 1, x + 1], [y + 0, y + 1], c=self.cl, lw=self.lw, ls=ls, alpha=alpha
                )
            elif neighbor == "s":
                return plt.plot(
                    [x + 1, x + 1], [y + 1, y + 2], c=self.cl, lw=self.lw, ls=ls, alpha=alpha
                )
            else:
                return [None]

        # Plot stabilizers
        for stab in self.graph.S[z].values():
            (type, yb, xb) = stab.sID
            y, x = yb * 4, xb * 4
            stab.pg = {}
            for neighbor in stab.neighbors.keys():
                stab.pg[neighbor] = plot_stab(neighbor, y, x, type)[0]

        # Plot open boundaries if exists
        if hasattr(self.graph, 'B'):
            for bound in self.graph.B[z].values():
                (type, yb, xb) = bound.sID
                y, x = yb * 4, xb * 4
                bound.pg = {}
                for neighbor in bound.neighbors.keys():
                    bound.pg[neighbor] = plot_stab(neighbor, y, x, type, alpha=0.3)[0]

        # Plot qubits
        for qubit in self.graph.Q[z].values():
            (td, yb, xb) = qubit.qID
            y, x = yb * 4, xb * 4
            if td == 0:
                qubit.pg = plt.Circle(
                    (x + 3, y + 1),
                    self.qsize,
                    edgecolor=self.cc,
                    fill=False,
                    linewidth=self.lw,
                )
                self.ax.add_artist(qubit.pg)
            else:
                qubit.pg = plt.Circle(
                    (x + 1, y + 3),
                    self.qsize,
                    edgecolor=self.cc,
                    fill=False,
                    linewidth=self.lw,
                )
                self.ax.add_artist(qubit.pg)

        self.canvas.draw()
        if self.plot_base:
            self.waitforkeypress("Lattice plotted.")

    def waitforkeypress(self, str):
        txt = str + " Press to continue..."
        print(txt)
        self.text.set_text(txt)

        keyboardClick = False
        while not keyboardClick:
            keyboardClick = plt.waitforbuttonpress(120)

    def plot_erasures(self):
        """
        :param erasures         list of locations (TD, y, x) of the erased stab_qubits
        plots an additional blue cicle around the qubits which has been erased
        """
        plt.sca(self.ax)

        for qubit in self.graph.Q[0].values():
            qplot = qubit.pg
            if qubit.erasure:
                qplot.set_linestyle(":")
                self.ax.draw_artist(qplot)


    def plot_errors(self, z=0, plot_qubits=False):
        """
        :param arrays       array of qubit states
        plots colored circles within the qubits if there is an error
        """
        plt.sca(self.ax)

        for qubit in self.graph.Q[z].values():
            qplot = qubit.pg
            X_error = qubit.E[0].state
            Z_error = qubit.E[1].state

            if X_error and not Z_error:
                qplot.set_fill(True)
                qplot.set_facecolor(self.cx)
                self.ax.draw_artist(qplot)

            elif Z_error and not X_error:
                qplot.set_fill(True)
                qplot.set_facecolor(self.cz)
                self.ax.draw_artist(qplot)

            elif X_error and Z_error:
                qplot.set_fill(True)
                qplot.set_facecolor(self.cy)
                self.ax.draw_artist(qplot)

            else:
                if plot_qubits:
                    qplot.set_fill(False)
                    self.ax.draw_artist(qplot)

        if self.plot_error:
            self.canvas.blit(self.ax.bbox)
            self.waitforkeypress("Errors plotted.")


    def plot_syndrome(self, z=0):
        """
        :param qua_loc      list of quasiparticle/anyon positions (y,x)
        plots the vertices of the anyons on the lattice
        """

        plt.sca(self.ax)
        C = [self.cX, self.cZ]

        for stab in self.graph.S[z].values():
            (ertype, yb, xb) = stab.sID
            gplotlot = stab.pg
            if stab.parity:
                for dir in self.graph.dirs:
                    if dir in stab.neighbors:
                        gplotlot = stab.pg[dir]
                        gplotlot.set_color(C[ertype])
                        self.ax.draw_artist(gplotlot)

        if self.plot_anyons:
            self.canvas.blit(self.ax.bbox)
            self.waitforkeypress("Syndromes plotted.")


    def plot_lines(self, matchings):
        """
        :param results      list of matchings of anyon
        plots strings between the two anyons of each match
        """

        plt.sca(self.ax)

        P = [1, 3]
        LS = ["-.", ":"]

        for _, _, v0, v1 in matchings:

            color = [random.random() * 0.8 + 0.2 for _ in range(3)]

            (type, topy, topx) = v0.sID
            (type, boty, botx) = v1.sID

            p, ls = P[type], LS[type]

            plt.plot(
                [topx * 4 + p, botx * 4 + p],
                [topy * 4 + p, boty * 4 + p],
                c=color,
                lw=self.slw,
                ls=ls,
            )
            circle1 = plt.Circle(
                (topx * 4 + p, topy * 4 + p), 0.25, fill=True, facecolor=color
            )
            circle2 = plt.Circle(
                (botx * 4 + p, boty * 4 + p), 0.25, fill=True, facecolor=color
            )
            self.ax.add_artist(circle1)
            self.ax.add_artist(circle2)

        if self.plot_matching:
            self.canvas.blit(self.ax.bbox)
            self.waitforkeypress("Matchings plotted.")


    def plot_final(self):
        """
        param: flips        qubits that have flipped in value (y,x)
        param: arrays       data array of the (corrected) qubit states
        plots the applied stabilizer measurements over the lattices
        also, in the qubits that have flipped in value a smaller white circle is plotted

        optionally, the axis is clear and the final state of the lattice is plotted
        """

        plt.sca(self.ax)

        for qubit in self.graph.Q[0].values():
            qplot = qubit.pg
            X_error = qubit.E[0].matching
            Z_error = qubit.E[1].matching

            if X_error and not Z_error:
                qplot.set_edgecolor(self.cx)
                self.ax.draw_artist(qplot)

            elif Z_error and not X_error:
                qplot.set_edgecolor(self.cz)
                self.ax.draw_artist(qplot)

            elif X_error and Z_error:
                qplot.set_edgecolor(self.cy)
                self.ax.draw_artist(qplot)


        if self.plot_correction:
            self.canvas.blit(self.ax.bbox)
            self.waitforkeypress("Corrections plotted.")

        if self.plot_result:

            for qubit in self.graph.Q[0].values():
                qplot = qubit.pg
                X_error = qubit.E[0].state
                Z_error = qubit.E[1].state
                if X_error or Z_error:
                    qplot.set_edgecolor(self.cc)
                    self.ax.draw_artist(qplot)

            self.plot_errors(plot_qubits=True)
            print("Final lattice plotted. Press on the plot to continue")


from mpl_toolkits.mplot3d import Axes3D


class plot_3D(plot_2D):

    def waitforkeypress(self, str):
        txt = str + " Press to continue..."
        print(txt)

        keyboardClick = False
        while not keyboardClick:
            keyboardClick = plt.waitforbuttonpress(120)

    def init_plot(self, *args, **kwargs):

        plt.figure(self.f.number)
        self.canvas = self.f.canvas
        plt.ion()
        plt.cla()

        self.ax = plt.axes(projection='3d', label="main")
        self.ax.set_axis_off()

        # Plot stabilizers
        for layer in self.graph.S.values():
            for stab in layer.values():
                (type, yb, xb), zb = stab.sID, stab.z
                y, x, z = yb * 4, xb * 4, zb * 4
                stab.pg = {}
                for neighbor in stab.neighbors.keys():
                    stab.pg[neighbor] = self.plot_stab(neighbor, y, x, z, type)[0]


        # Plot open boundaries if exists
        if hasattr(self.graph, 'B'):
            for layer in self.graph.B.values():
                for bound in layer.values():
                    (type, yb, xb), zb = bound.sID, bound.z
                    y, x, z = yb * 4, xb * 4, zb*4
                    bound.pg = {}
                    for neighbor in bound.neighbors.keys():
                        bound.pg[neighbor] = self.plot_stab(neighbor, y, x, z, type, alpha=0.3)[0]

        self.stab_plots = {}
        for z, layer in self.graph.Q.items():

            X, Y, i, stab_locs = [], [], 0, {}
            for qubit in layer.values():
                (td, yb, xb) = qubit.qID

                if td == 0:
                    X.append(xb*4+3)
                    Y.append(yb*4+1)
                else:
                    X.append(xb*4+1)
                    Y.append(yb*4+3)

                stab_locs[qubit.qID] = i
                i += 1

            color = [self.cc for _ in range(len(X))]

            self.stab_plots[z] = {
                "plot"  : None,
                "locs"  : stab_locs,
                "X"     : X,
                "Y"     : Y,
                "Z"     : z*4
            }

            self.plot_qubit(z, color)

        self.set_axes_equal()
        self.canvas.draw()
        if self.plot_base:
            self.waitforkeypress("Lattice plotted.")


    def plot_qubit(self, z, color):

        X = self.stab_plots[z]["X"]
        Y = self.stab_plots[z]["Y"]
        Z = self.stab_plots[z]['Z']

        if self.stab_plots[z]["plot"]:
            self.stab_plots[z]["plot"].remove()

        self.stab_plots[z]["plot"] = self.ax.scatter(X, Y, Z, s=50, c=color)


    def set_axes_equal(self):
        '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
        cubes as cubes, etc..  This is one possible solution to Matplotlib's
        ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

        Input
          ax: a matplotlib axis, e.g., as output from plt.gca().
        '''

        x_limits = self.ax.get_xlim3d()
        y_limits = self.ax.get_ylim3d()
        z_limits = self.ax.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = sum(x_limits)/len(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = sum(y_limits)/len(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = sum(z_limits)/len(z_limits)

        # The plot bounding box is a sphere in the sense of the infinity
        # norm, hence I call half the max range the plot radius.
        plot_radius = 0.5*max([x_range, y_range, z_range])

        self.ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        self.ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        self.ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

    def plot_stab(self, neighbor, y, x, z, type, alpha=1):
        y += 2*type
        x += 2*type
        ls = "-" if type == 0 else "--"
        if neighbor == "w":
            return self.ax.plot(
                [x + 0, x + 1], [y + 1, y + 1], zs=z, c=self.cl, lw=self.lw, ls=ls, alpha=alpha
            )
        elif neighbor == "e":
             return self.ax.plot(
                [x + 1, x + 2], [y + 1, y + 1], zs=z,  c=self.cl, lw=self.lw, ls=ls, alpha=alpha
            )
        elif neighbor == "n":
            return self.ax.plot(
                [x + 1, x + 1], [y + 0, y + 1], zs=z, c=self.cl, lw=self.lw, ls=ls, alpha=alpha
            )
        elif neighbor == "s":
            return self.ax.plot(
                [x + 1, x + 1], [y + 1, y + 2], zs=z, c=self.cl, lw=self.lw, ls=ls, alpha=alpha
            )
        else:
            return [None]


    def plot_errors(self, z, plot_qubits=False):
        plt.sca(self.ax)

        qubits = self.graph.Q[z].values()
        plocs = self.stab_plots[z]["locs"]
        color = [self.cc for _ in range(len(qubits))]

        for qubit in qubits:
            X_error = qubit.E[0].state
            Z_error = qubit.E[1].state

            if X_error or Z_error or plot_qubits:

                if X_error and not Z_error:
                    color[plocs[qubit.qID]] = self.cx

                elif Z_error and not X_error:
                    color[plocs[qubit.qID]] = self.cz

                elif X_error and Z_error:
                    color[plocs[qubit.qID]] = self.cy

                elif plot_qubits:
                    color[plocs[qubit.qID]] = self.cc

        self.plot_qubit(z, color)

        if self.plot_error:
            self.canvas.blit(self.ax.bbox)
            self.waitforkeypress(f"Layer {z} errors plotted. ")


    def plot_syndrome(self, z):
        """
        :param qua_loc      list of quasiparticle/anyon positions (y,x)
        plots the vertices of the anyons on the lattice
        """

        plt.sca(self.ax)
        C = [self.cX, self.cZ]

        for stab in self.graph.S[z].values():
            (ertype, yb, xb) = stab.sID
            gplotlot = stab.pg
            if stab.parity:
                for dir in self.graph.dirs:
                    if dir in stab.neighbors:
                        gplotlot = stab.pg[dir]
                        gplotlot.set_color(C[ertype])
                        self.ax.draw_artist(gplotlot)
            if stab.state:
                X, Y, Z = xb * 4 + 2*ertype, yb * 4 + 2*ertype, z*4 - 2
                stab.ap = self.ax.scatter(X, Y, Z, s=50, c=[C[ertype]], alpha=1, marker="*")

        if self.plot_anyons:
            self.canvas.blit(self.ax.bbox)
            self.waitforkeypress(f"Layer {z} syndromes plotted. ")


    def plot_lines(self, matchings):
        """
        :param results      list of matchings of anyon
        plots strings between the two anyons of each match
        """

        plt.sca(self.ax)

        P = [0, 2]
        LS = ["-.", ":"]

        for _, _, v0, v1 in matchings:

            color = [random.random() * 0.8 + 0.2 for _ in range(3)]

            (type, topy, topx), topz = v0.sID, v0.z
            (type, boty, botx), botz = v1.sID, v1.z

            p, ls = P[type], LS[type]

            self.ax.plot(
                [topx * 4 + p, botx * 4 + p],
                [topy * 4 + p, boty * 4 + p],
                [topz * 4 - 2, botz * 4 - 2],
                c=color,
                lw=self.slw,
                ls=ls,
            )

        if self.plot_matching:
            self.canvas.blit(self.ax.bbox)
            self.waitforkeypress("Matchings plotted.")

    def plot_final(self):

        z = self.graph.size - 1

        fp = plot_2D(self.graph, z=z)
        fp.plot_errors(z=z)
