import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import printing as pr

class unionfind_plot:
    def __init__(
        self, graph, axn=2, plot_size=10, line_width=0.5, plotstep_click=False
    ):

        self.size = graph.size
        self.graph = graph
        self.plot_size = plot_size

        self.cl = [0.2, 0.2, 0.2]  # Line color
        self.cx = [0.9, 0.3, 0.3]  # X error color
        self.cz = [0.5, 0.5, 0.9]  # Z error color
        self.Cx = [0.5, 0.1, 0.1]
        self.Cz = [0.1, 0.1, 0.5]
        self.cX = [0.9, 0.7, 0.3]
        self.cZ = [0.3, 0.9, 0.3]

        self.C1 = [self.cx, self.cz]
        self.C2 = [self.cX, self.cZ]
        self.LS = ["-", "--"]

        self.alpha = 0.3

        self.qsize = 0.1
        self.lw = line_width
        self.plotstep_click = plotstep_click

        self.f = plt.figure(figsize=(self.plot_size, self.plot_size))

        self.init_plot()

    def init_plot(self):


        plt.figure(self.f.number)
        plt.ion()
        plt.show()
        plt.axis("off")
        self.ax = self.f.gca()
        self.ax.invert_yaxis()
        self.ax.set_aspect("equal")

        self.canvas = self.f.canvas
        self.text = self.ax.text(0.5, 0, "", fontsize=10, va ="top", ha="center", transform=self.ax.transAxes)

        self.edges = {}
        self.vertices = {}

        # Initate legend
        le_xv = Line2D(
            [0],
            [0],
            lw=0,
            marker="o",
            color="w",
            mew=0,
            mfc=self.cx,
            ms=10,
            label="X-vertex",
        )
        le_zv = Line2D(
            [0],
            [0],
            lw=0,
            marker="o",
            color="w",
            mew=0,
            mfc=self.cz,
            ms=10,
            label="Z-vertex",
        )
        le_xe = Line2D([0], [0], ls="-", lw=self.lw, color=self.cx, label="X-edge")
        le_ze = Line2D([0], [0], ls="--", lw=self.lw, color=self.cz, label="Z-edge")
        self.ax.legend(
            handles=[le_xv, le_zv, le_xe, le_ze],
            bbox_to_anchor=(1.25, 0.95),
            loc="upper right",
            ncol=1,
        )

        # Initate plot
        plt.sca(self.ax)

        for qubit in self.graph.Q[0].values():
            self.draw_edge0(qubit)
            self.draw_edge1(qubit)

        for stab in self.graph.S[0].values():
            self.draw_vertex(stab)

        self.canvas.draw()
        pr.printlog("Peeling lattice initiated.")
        self.waitforkeypress()


    def draw_edge0(self, qubit):

        (type, y0, x0) = qubit.qID[:3]

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

        color, alpha = (self.C1[0], 1) if qubit.erasure else (self.cl, self.alpha)

        up1 = self.ax.plot([x0,  pxm], [y0,  pym], c=color, lw=self.lw, ls=self.LS[0], alpha=alpha)
        up2 = self.ax.plot([pxm, px1], [pym, py1], c=color, lw=self.lw, ls=self.LS[0], alpha=alpha)
        qubit.E[0].pu = [up1[0], up2[0]]


    def draw_edge1(self, qubit):

        (type, y0, x0) = qubit.qID[:3]

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

        color, alpha = (self.C1[1], 1) if qubit.erasure else (self.cl, self.alpha)

        up1 = self.ax.plot([x0,  sxm], [y0,  sym], c=color, lw=self.lw, ls=self.LS[1], alpha=alpha)
        up2 = self.ax.plot([sxm, sx1], [sym, sy1], c=color, lw=self.lw, ls=self.LS[1], alpha=alpha)

        qubit.E[1].pu = [up1[0], up2[0]]

    def draw_vertex(self, stab):

        (ertype, y, x) = stab.sID[:3]
        if ertype == 1:
            y += 0.5
            x += 0.5

        if stab.state:
            fill = True
            lw = self.lw
        else:
            fill = False
            lw = 0

        stab.pu = plt.Circle(
            (x, y),
            self.qsize,
            facecolor=self.C2[ertype],
            linewidth=lw,
            edgecolor=self.C1[ertype],
            fill=fill,
            zorder=10
        )
        self.ax.add_artist(stab.pu)


    def draw_plot(self, txt=None):
        if txt is not None:
            self.text.set_text(txt)
            pr.printlog(txt)
        self.canvas.draw()
        if self.plotstep_click: self.waitforkeypress()

    def waitforkeypress(self):
        keyboardClick = False
        while not keyboardClick:
            keyboardClick = plt.waitforbuttonpress(120)

    """
    ________________________________________________________________________________

    main plot functions

    """

    def plot_edge(self, edge, num, color, alpha):

        p_edge = edge.pu[num]
        p_edge.set_color(color)
        p_edge.set_alpha(alpha)
        self.ax.draw_artist(p_edge)


    def plot_removed(self):
        """
        :param rem_list         list of edges
        plots the normal edge color over the edges that have been removed during the formation of the tree structure

        """
        plt.sca(self.ax)

        for qubit in self.graph.Q[0].values():
            for edge in [qubit.E[0], qubit.E[1]]:
                if edge.peeled and not edge.matching:
                    self.plot_edge(edge, 0, self.cl ,self.alpha)
                    self.plot_edge(edge, 1, self.cl ,self.alpha)


    def add_edge(self, edge, vertex):

        plt.figure(self.f.number)

        if edge.support == 1:

            (ye, xe) = edge.qubit.qID[1:3]
            (yv, xv) = vertex.sID[1:3]
            id = 0 if (ye == yv and xe == xv) else 1
            color = self.Cx if edge.ertype ==0 else self.Cz
            self.plot_edge(edge, id, color, 0.5)
            self.plot_edge(edge, 1-id, self.cl ,self.alpha)

        else:
            color = self.cx if edge.ertype == 0 else self.cz

            self.plot_edge(edge, 0, color, 1)
            self.plot_edge(edge, 1, color, 1)

    """
    ________________________________________________________________________________

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

        self.plot_edge(edge, 0, "k", 1)
        self.plot_edge(edge, 1, "k", 1)
        self.canvas.draw()

        line = text + " edge " + str(edge)
        pr.printlog(line)
        if self.plotstep_click: self.waitforkeypress()

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

        self.canvas.draw()
