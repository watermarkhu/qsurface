from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import printing as pr
import random


class plot_2D:

    def __init__(self, graph, z=0, plot_size=8, line_width=0.5, click=1, **kwargs):

        self.size = graph.size
        self.graph = graph
        self.plot_size = plot_size
        self.click = click

        self.qsize = 0.5
        self.qsize2 = 0.25
        self.qsizeE = 0.7
        self.qsizeU = 0.1
        self.lw = line_width
        self.slw = 2

        self.alpha = 0.3
        self.alpha2 = 0.3

        # Define colors
        self.cw = [1, 1, 1]
        self.cl = [0.8, 0.8, 0.8]  # Line color
        self.cc = [0.7, 0.7, 0.7]  # Qubit color
        self.ec = [0.3, 0.3, 0.3]  # Erasure color
        self.cx = [0.9, 0.3, 0.3]  # X error color
        self.cz = [0.5, 0.5, 0.9]  # Z error color
        self.cy = [0.9, 0.9, 0.5]  # Y error color
        self.cX = [0.9, 0.7, 0.3]  # X quasiparticle color
        self.cZ = [0.3, 0.9, 0.3]  # Z quasiparticle color
        self.Cx = [0.5, 0.1, 0.1]
        self.Cz = [0.1, 0.1, 0.5]
        self.cE = [0.3, 0.5, 0.9]  # Erasure color
        self.C1 = [self.cx, self.cz]
        self.C2 = [self.cX, self.cZ]
        self.LS = ["-", "--"]
        self.LS2 = [":", "--"]

        self.scatter_size = 200/graph.size
        self.z_distance = 8

        self.f = plt.figure(figsize=(self.plot_size, self.plot_size))

        self.init_plot(z)

    def draw_plot(self, txt=None):
        if txt is not None:
            self.text.set_text(txt)
            pr.printlog(txt)
        self.canvas.blit(self.ax.bbox)
        if self.click: self.waitforkeypress()

    def waitforkeypress(self):
        keyboardClick = False
        while not keyboardClick:
            keyboardClick = plt.waitforbuttonpress(120)

    def legend_circle(self, label, mfc=None, marker="o", mec="k", ms=10, color="w", lw=0, mew=2, ls="-"):
        return Line2D(
            [0],
            [0],
            lw=lw,
            ls=ls,
            marker=marker,
            color=color,
            mec=mec,
            mew=mew,
            mfc=mfc,
            ms=ms,
            label=label,
        )

    def init_plot(self, z=0):
        '''
        param: z        z layer to plot, defaults to 0
        Initializes 2D plot of toric/planar lattice
        Stabilizers are plotted with line objects
        Qubits are plotted with Circle objects
        '''

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
        le_qubit    = self.legend_circle("Qubit", mfc="w")
        le_xer      = self.legend_circle("X-error", mfc=self.cx)
        le_zer      = self.legend_circle("Y-error", mfc=self.cz)
        le_yer      = self.legend_circle("Z-error", mfc=self.cy)
        le_err      = self.legend_circle("Erasure", mfc="w", marker="$\u25CC$", mec=self.cE, mew=1, ms=12)
        le_ver      = self.legend_circle("Vertex", ls="-", lw=self.lw, color=self.cX)
        le_pla      = self.legend_circle("Plaquette", ls="--", lw=self.lw, color=self.cZ)
        self.lh = [le_qubit, le_xer, le_zer, le_yer, le_err, le_ver, le_pla]

        legend = plt.legend(
            handles=self.lh, bbox_to_anchor=(-0.25, 0.95), loc="upper left", ncol=1
        )
        self.ax.add_artist(legend)

        # Plot empty lattice
        # Loop over all indices

        # Plot stabilizers
        for stab in self.graph.S[z].values():
            self.plot_stab(stab, alpha=self.alpha2)

        # Plot open boundaries if exists
        if hasattr(self.graph, 'B'):
            for bound in self.graph.B[z].values():
                self.plot_stab(bound, alpha=self.alpha)

        # Plot qubits
        for qubit in self.graph.Q[z].values():
            self.plot_qubit(qubit)

        self.draw_plot("Lattice plotted.")


    def draw_line(self, X, Y, color="w", lw=2, ls=2, alpha=1, **kwargs):
        return self.ax.plot(X, Y, c=color, lw=lw, ls=ls, alpha=alpha)[0]


    def plot_stab(self, stab, alpha=1):
        '''
        param: stab         graph.stab object
        param: alpha        alpha for all line objects of this stab
        Plots stabilizers as line objects.
        Loop over layer neighbor keys to ensure compatibility with planar/toric lattices
        '''
        (type, yb, xb), zb = stab.sID, stab.z
        y, x = yb * 4, xb * 4
        y += 2*type
        x += 2*type
        ls = "-" if type == 0 else "--"

        stab.pg = {}
        for dir in [dir for dir in self.graph.dirs if dir in stab.neighbors]:
            if dir == "w":
                X, Y = [x + 0, x + 1], [y + 1, y + 1]
            elif dir == "e":
                X, Y = [x + 1, x + 2], [y + 1, y + 1]
            elif dir == "n":
                X, Y = [x + 1, x + 1], [y + 0, y + 1]
            elif dir == "s":
                X, Y = [x + 1, x + 1], [y + 1, y + 2]

            stab.pg[dir] = self.draw_line(X, Y, Z=zb * self.z_distance, color=self.cl, lw=self.lw, ls=ls, alpha=alpha)


    def plot_qubit(self, qubit):
        '''
        param: qubit        graph.qubit object
        Patch.Circle object for each qubit on the lattice
        '''
        (td, yb, xb) = qubit.qID
        X, Y = (xb*4+3, yb*4+1) if td == 0 else (xb*4+1, yb*4+3)
        qubit.pg = plt.Circle(
            (X, Y),
            self.qsize,
            edgecolor=self.cc,
            fill=False,
            linewidth=self.lw,
        )
        self.ax.add_artist(qubit.pg)


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

        self.draw_plot("Erasures plotted.")


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

        self.draw_plot("Errors plotted.")


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

        self.draw_plot("Syndromes plotted.")


    def plot_lines(self, matchings):
        """
        :param results      list of matchings of anyon
        plots strings between the two anyons of each match
        """
        plt.sca(self.ax)
        P = [1, 3]

        for _, _, v0, v1 in matchings:

            color = [random.random() * 0.8 + 0.2 for _ in range(3)]

            (type, topy, topx) = v0.sID
            (type, boty, botx) = v1.sID

            p, ls = P[type], self.LS2[type]

            plt.plot(
                [topx * 4 + p, botx * 4 + p],
                [topy * 4 + p, boty * 4 + p],
                c=color,
                lw=self.slw,
                ls=ls,
                alpha=self.alpha2
            )

        self.draw_plot("Matchings plotted.")


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


        self.draw_plot("Corrections plotted.")

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

    def draw_plot(self, txt=None):
        if txt is not None:
            pr.printlog(txt)
        self.canvas.blit(self.ax.bbox)
        if self.click: self.waitforkeypress()

    def set_axes_equal(self):
        '''
        Sets equal axes for a 3D mplot3d axis.
        Doesn't work fully as intended, as axes still scales in z direction
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


    def init_plot(self, *args, **kwargs):
        '''
        Initializes 3D plot of toric/planar lattice
        Stabilizers are plotted with Axes3D.line objects
        Qubits are plotted with Axes3D.scatter objects
        '''

        plt.figure(self.f.number)
        self.canvas = self.f.canvas
        plt.ion()
        plt.cla()

        self.ax = plt.axes(projection='3d', label="main")
        self.ax.set_axis_off()

        # Plot stabilizers
        for layer in self.graph.S.values():
            for stab in layer.values():
                self.plot_stab(stab, alpha=1)

        # Plot open boundaries if exists
        if hasattr(self.graph, 'B'):
            for layer in self.graph.B.values():
                for bound in layer.values():
                    self.plot_stab(bound, alpha=self.alpha)

        # Plot plot_qubits, store qubit plots in self due to update bug
        self.scatter = {}
        for z, layer in self.graph.Q.items():
            X, Y, i, locs = [], [], 0, {}
            for qubit in layer.values():
                (td, yb, xb) = qubit.qID

                if td == 0:
                    X.append(xb*4+3)
                    Y.append(yb*4+1)
                else:
                    X.append(xb*4+1)
                    Y.append(yb*4+3)

                locs[qubit.qID] = i
                i += 1

            color = [self.cc for _ in range(len(X))]
            sizes = [self.scatter_size for _ in range(len(X))]

            self.scatter[z] = {
                "plot"  : None,
                "locs"  : locs,
                "size"  : sizes,
                "X"     : X,
                "Y"     : Y,
                "Z"     : z*self.z_distance
            }
            self.plot_scatter(z, color, self.scatter_size)

        self.set_axes_equal()
        self.draw_plot("Lattice plotted.")


    def draw_line(self, X, Y, Z=0, color="w", lw=2, ls=2, alpha=1, **kwargs):
        return self.ax.plot(X, Y, zs=Z, c=color, lw=lw, ls=ls, alpha=alpha)[0]


    def plot_scatter(self, z, color, sizes=None):
        '''
        Axes3D.scatter objects do not update color using set_color() function after blitting.
        Workaround is to remove entire scatter object from the plot and plotting a new scatter object with correct colors.
        '''

        X = self.scatter[z]["X"]
        Y = self.scatter[z]["Y"]
        Z = self.scatter[z]['Z']

        if self.scatter[z]["plot"]:
            self.scatter[z]["plot"].remove()

        if sizes:
            self.scatter[z]["plot"] = self.ax.scatter(X, Y, Z, s=sizes, c=color)
        else:
            self.scatter[z]["plot"] = self.ax.scatter(X, Y, Z, c=color)


    def plot_errors(self, z, plot_qubits=False):
        '''
        param: z            z/t layer of 3D plot
        param: plot_qubits  replots all qubits
        Plots errors by setting colors of Axes3D.scatter objects and plotting using plot_qubits() function
        '''
        plt.sca(self.ax)
        qubits = self.graph.Q[z].values()
        plocs = self.scatter[z]["locs"]
        sizes = self.scatter[z]["size"]

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

        self.plot_scatter(z, color, sizes)


    def plot_erasures(self, z):
        """
        :param erasures         list of locations (TD, y, x) of the erased stab_qubits
        plots an additional blue cicle around the qubits which has been erased
        """
        plt.sca(self.ax)
        qubits = self.graph.Q[z].values()
        plocs = self.scatter[z]["locs"]
        sizes = self.scatter[z]["size"]
        color = [self.cc for _ in range(len(qubits))]

        for qubit in qubits:
            X_error = qubit.E[0].state
            Z_error = qubit.E[1].state

            if qubit.erasure:
                sizes[plocs[qubit.qID]] = self.scatter_size/3

            if X_error or Z_error:
                if X_error and not Z_error:
                    color[plocs[qubit.qID]] = self.cx
                elif Z_error and not X_error:
                    color[plocs[qubit.qID]] = self.cz
                elif X_error and Z_error:
                    color[plocs[qubit.qID]] = self.cy

        self.scatter[z]["size"] = sizes
        self.plot_scatter(z, color, sizes)


    def plot_syndrome(self, z):
        """
        param: z            z/t layer of 3D plot
        Plots the syndrome by redrawing Axes3D.line plots of the stabilizer.
        Additionally plots scatter object of anyons, that are now in between stabilizers of different z layers
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
                X, Y, Z = xb * 4 + 2*ertype, yb * 4 + 2*ertype, (z - 1/2) * self.z_distance
                stab.ap = self.ax.scatter(X, Y, Z, s=self.scatter_size, c=[C[ertype]], alpha=1, marker="*")


    def plot_lines(self, matchings):
        """
        :param mathings      list of matchings of anyon
        plots strings between the two anyons of each match
        """

        plt.sca(self.ax)
        P = [0, 2]

        for _, _, v0, v1 in matchings:

            color = [random.random() * 0.8 + 0.2 for _ in range(3)]

            (type, topy, topx), topz = v0.sID, v0.z
            (type, boty, botx), botz = v1.sID, v1.z

            p, ls = P[type], self.LS2[type]

            self.ax.plot(
                [topx * 4 + p, botx * 4 + p],
                [topy * 4 + p, boty * 4 + p],
                [(topz - .5)*self.z_distance, (botz - .5)*self.z_distance],
                c=color,
                lw=self.slw,
                ls=ls,
                alpha=self.alpha2
            )

        self.draw_plot("Matchings plotted.")

    def plot_final(self):
        '''
        Plots a plot_graph 2D figure of the final z layer.
        '''
        z = self.graph.size - 1

        fp = plot_2D(self.graph, z=z)
        fp.plot_errors(z=z)
