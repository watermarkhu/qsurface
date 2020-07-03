'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________


Plotting function for the surface/planar lattice.
A plot_2D object is initialized for a graph_2D graph, which plots onto a 2D axis
A plot_3D object is initialized for a graph_3D graph, which plots onto a 3D axis

Plot_2D object is inherited by Plot_3D object. All colors on the plot are defined in the plot_2D oject.
The plot_unionfind.plot_2D and plot_3D objects are also child objects that uses the same colors and some methods

'''
from collections import defaultdict as dd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button, RadioButtons
import matplotlib as mpl
from time import time
import random
import os
from simulator.info import printing as pr
from simulator.configuration import readconfig, writeconfig


mpl.rcParams['toolbar'] = 'None'
    

class plot_2D:
    '''
    2D axis plot for both toric/planar lattices.

    Plots the qubits as cirlces, including the errors that occur on these qubits.
    Plots the stabilizers, their measurement state and the matching between the stabilizers.

    Many plot parameters, including colors of the plot, linewidths, scatter sizes are defined here.

    '''

    def __init__(self, graph, z=0, from3D=0, **kwargs):

        self.size = graph.size
        self.graph = graph
        self.from3D = from3D

        self.config = {'Scale':  {'plot_size': '10',
                                  'linewidth': '1.5',
                                  'scatter_size': '30',
                                  'qubitsize': '0.1',
                                  'z_distance': '8',
                                  'picksize': '5'},
              'Colors': {'cw': '[1, 1, 1]',
                         'cl': '[0.8, 0.8, 0.8]',
                         'cq': '[0.7, 0.7, 0.7]',
                         'cx': '[0.9, 0.3, 0.3]',
                         'cz': '[0.5, 0.5, 0.9]',
                         'cy': '[0.9, 0.9, 0.5]',
                         'cx2': '[0.9, 0.7, 0.3]',
                         'cz2': '[0.3, 0.9, 0.3]',
                         'cx3': '[0.5, 0.1, 0.1]',
                         'cz3': '[0.1, 0.1, 0.5]',
                         'alpha': '0.35'},
              'Linestyles': {'lsx': '":"',
                             'lsy': '"--"',
                             'uflsx': '"-"',
                             'uflsy': '"--"'}}
        
        configpath = 'simulator/plot/plot.ini'
        if not os.path.exists(configpath):
            writeconfig(configpath, self.config)
        data = readconfig(configpath)
        for key, value in data.items():
            setattr(self, key, value)
        
        self.C1 = [self.cx, self.cz]
        self.C2 = [self.cx2, self.cz2]
        self.LS = [self.lsx, self.lsy]
        self.UFLS = [self.uflsx, self.uflsy]

        # History attributes
        self.history = dd(dict)
        self.iter = 0
        self.iter_names = ["Initial"]
        self.iter_plot = 0
        self.recent = 0

        # Initiate figure and axes
        self.f = plt.figure(figsize=(self.plot_size, self.plot_size))
        plt.ion()
        plt.cla()
        plt.show()
        plt.axis("off")
        self.ax = plt.axes([0.075, 0.1, 0.7, 0.85])
        self.ax.set_aspect("equal")
        self.canvas = self.f.canvas
        self.canvas.callbacks.connect('pick_event', self.on_pick)

        # Initiate buttons and elements
        self.prev_button = Button(plt.axes([0.75, 0.025, 0.125, 0.05]), "Previous")
        self.next_button = Button(plt.axes([0.9, 0.025, 0.075, 0.05]), "Next")
        self.prev_button.on_clicked(self.draw_prev)
        self.next_button.on_clicked(self.draw_next)
        self.rax = plt.axes([0.9, 0.1, 0.075, 0.125])
        self.radio_button = RadioButtons(self.rax, ("info", "X", "Z", "E"))

        # Initiate text box
        self.ax_text = plt.axes([0.025, 0.025, 0.7, 0.05])
        plt.axis("off")
        self.text = self.ax_text.text(0.5, 0.5, "", fontsize=10, va ="center", ha="center", transform=self.ax_text.transAxes)

        self.init_plot(z)

        # Turn off radio button
        self.radio_button.set_active(0)
        plt.setp(self.rax, visible=0)


    def on_pick(self, event):
        '''
        Pick event handler for the plots
        Normally prints some info about the nodes on the plot.
        In the initial round, the user can opt to manually add extra errors onto the lattice.
        '''
        artist = event.artist
        radiovalue = self.radio_button.value_selected

        if radiovalue == "info":
            print("picked", artist.object.picker())
        else:
            qubit = artist.object

            '''
            Need to calculate time between pick events due to 3d_scatter workaround. When switching between plot objects in the workaround, we swap the visibility and also the picker attribute from None to True. However, the pick event is somehow stored for some period, such that after the swap of the picker attribute, a second pick event is registered. We therefore wait 0.1 seconds between pick events.
            '''
            prev_time = getattr(qubit, "pick_time", None)
            qubit.pick_time = time()
            if prev_time and qubit.pick_time - prev_time < 0.1:
                return

            if radiovalue == "X":
                qubit.E[0].state = not qubit.E[0].state
            elif radiovalue == "Z":
                qubit.E[1].state = not qubit.E[1].state
            elif radiovalue == "E":
                qubit.erasure = not qubit.erasure

            attr_dict = self.get_error_attr(qubit)

            if not attr_dict:
                attr_dict = dict(fill=0, facecolor=self.cw)

            if qubit.erasure:
                attr_dict.update(dict(linestyle=":"))
            else:
                attr_dict.update(dict(linestyle="-"))

            if attr_dict:
                self.new_attributes(qubit.pg, attr_dict)

    '''
    #########################################################################
                            Waiting funtions
    '''
    def draw_plot(self):
        '''
        Blits all changed plotting object onto the figure.
        Optional text is printed, added to the log and shown on the figure
        '''
        txt = self.iter_names[self.iter]
        self.text.set_text(txt)
        pr.printlog(f"{txt} plotted.")
        self.canvas.blit(self.ax.bbox)
        self.waitforkeypress()


    def waitforkeypress(self):
        '''
        Pauses the script until user interaction on the plot.
        Waits for a maximum of 120 seconds.
        '''
        wait = True
        while wait:
            wait = not plt.waitforbuttonpress(-1) or self.recent

    '''
    #########################################################################
                            Playback funtions
    '''
    def new_iter(self, name):
        '''
        Initiates new plot iteration
        '''
        self.iter_names.append(name)
        self.iter += 1
        self.iter_plot += 1


    def draw_next(self, event=None):
        '''
        Redraws all changes from next plot iteration onto the plot
        '''
        if self.iter_plot < self.iter:
            self.iter_plot += 1
            text = self.iter_names[self.iter_plot]
            self.text.set_text(text)
            for object, changes in self.history[self.iter_plot].items():
                self.change_attributes(object, changes)
            self.canvas.blit(self.ax.bbox)
            print("Drawing next: {}".format(text))
            if self.iter_plot == self.iter:
                self.recent = 0
        elif self.iter_plot == self.iter:
            print("Can't go further!")


    def draw_prev(self, event=None):
        '''
        Redraws all changes from previous plot iteration onto the plot
        '''
        if self.iter_plot >= 1:
            self.recent = 1
            self.iter_plot -= 1
            text = self.iter_names[self.iter_plot]
            self.text.set_text(text)
            for object, changes in self.history[self.iter_plot].items():
                self.change_attributes(object, changes)
            self.canvas.blit(self.ax.bbox)

            print("Drawing previous: {}".format(text))
        else:
            print("Can't go back further!")


    '''
    #########################################################################
                            Change attribute functions
    '''
    def get_nested_np_color(self, array):
        '''
        Get nested color and makes np.array, which is sometimes but not at all times used for color values, to a list.
        '''
        def get_nested(value):
            if type(value) == list and type(value[0]) == list:
                return get_nested(value[0])
            else:
                return value
        if type(array).__name__ == "ndarray":
            return get_nested(array.tolist())
        elif type(array) == list:
            return get_nested(array)
        else:
            return array


    def new_attributes(self, obj, attr_dict, overwrite=False):
        '''
        Finds the differences of the plot attributes between this iteration and the previous iterations. All differences are stored as dictionaries in the history variable.
        Makes sure that all changes are stored correctly and plot attributes are not overwritten if not explicitly defined.
        '''
        prev_changes = self.history[self.iter - 1]
        next_changes = self.history[self.iter]

        prev, next = {}, {}

        if not overwrite or obj not in prev_changes:
            for key, value in attr_dict.items():

                value = self.get_nested_np_color(value)
                old_value = self.get_nested_np_color(plt.getp(obj, key))

                if old_value != value:
                    prev[key] = old_value
                    next[key] = value
        else:
            old_dict = prev_changes[obj]
            for key, value in attr_dict.items():
                value = self.get_nested_np_color(value)
                old_value = old_dict[key] if key in old_dict else self.get_nested_np_color(plt.getp(obj, key))
                if old_value != value:
                    prev[key] = old_value
                    next[key] = value
        if prev:
            if overwrite or obj not in prev_changes:
                prev_changes[obj] = prev
            else:
                prev_changes[obj].update(prev)

        if next:
            next_changes[obj] = next
            self.change_attributes(obj, next)


    def change_attributes(self, object, attr_dict):
        '''
        Redraws the attributes from the dictionary onto the plot object
        '''
        if attr_dict:
            plt.setp(object, **attr_dict)
        self.ax.draw_artist(object)

    '''
    #########################################################################
                            Initilize axes
    '''
    def legend_circle(self, label, mfc=None, marker="o", mec="k", ms=10, color="w", lw=0, mew=2, ls="-"):
        '''
        Returns a Line2D, cirlle object that is used on the plot legend.
        '''
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


    def init_legend(self, x, y, items=[], loc="upper right"):
        '''
        Initilizes the legend of the plot.
        The qubits, errors and stabilizers are added.
        Aditional legend items can be inputted through the items paramter
        '''

        self.ax.set_title("{} lattice".format(self.graph.__class__.__name__))

        le_qubit    = self.legend_circle("Qubit", mfc=self.cq, mec=self.cq)
        le_xer      = self.legend_circle("X-error", mfc=self.cx, mec=self.cx)
        le_zer      = self.legend_circle("Y-error", mfc=self.cz, mec=self.cz)
        le_yer      = self.legend_circle("Z-error", mfc=self.cy, mec=self.cy)
        le_ver      = self.legend_circle("Vertex", ls="-", lw=self.linewidth, color=self.cx2, mfc=self.cx2, mec=self.cx2, marker="|")
        le_pla      = self.legend_circle("Plaquette", ls="--", lw=self.linewidth, color=self.cz2, mfc=self.cz2, mec=self.cz2, marker="|")

        self.lh = [le_qubit, le_xer, le_zer, le_yer, le_ver, le_pla] + items

        self.ax.legend(handles=self.lh, bbox_to_anchor=(x, y), loc=loc, ncol=1)


    def init_axis(self, min, max):
        '''
        Initilizes the 2D axis by settings axis limits, flipping y axis and removing the axis border
        '''
        # plt.grid(alpha = self.alpha, ls=":", lw=self.linewidth)
        self.ax.set_xlim(min, max)
        self.ax.set_ylim(min, max)
        self.ax.invert_yaxis()
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        plt.axis("off")
    '''
    #########################################################################
                            Initilize plot
    '''

    def init_plot(self, z=0):
        '''
        param: z        z layer to plot, defaults to 0
        Initializes 2D plot of toric/planar lattice
        Stabilizers are plotted with line objects
        Qubits are plotted with Circle objects
        '''
        plt.sca(self.ax)
        self.init_axis(-.25, self.size-.25)

        # Plot stabilizers
        for stab in self.graph.S[z].values():
            self.plot_stab(stab, alpha=self.alpha)

        # Plot open boundaries if exists
        if hasattr(self.graph, 'B'):
            for bound in self.graph.B[z].values():
                self.plot_stab(bound, alpha=self.alpha)

        # Plot qubits
        for qubit in self.graph.Q[z].values():
            self.plot_qubit(qubit)

        le_err = self.legend_circle("Erasure", mfc="w", marker="$\u25CC$", mec=self.cq, mew=1, ms=12)
        self.init_legend(1.3, 0.95, items=[le_err])
        
        self.canvas.draw()
        if not self.from3D:
            self.draw_plot()
    '''
    #########################################################################
                            Helper plot funtions
    '''

    def draw_line(self, X, Y, color="w", lw=2, ls=2, alpha=1, **kwargs):
        '''
        Plots a line onto the plot. Exist for default parameters.
        '''
        return self.ax.plot(X, Y, c=color, lw=lw, ls=ls, alpha=alpha)[0]


    def plot_stab(self, stab, alpha=1):
        '''
        param: stab         graph.stab object
        param: alpha        alpha for all line objects of this stab
        Plots stabilizers as line objects.
        Loop over layer neighbor keys to ensure compatibility with planar/toric lattices
        '''
        (type, y, x), zb = stab.sID, stab.z
        y += .5*type
        x += .5*type
        ls = "-" if type == 0 else "--"

        stab.pg = {}
        for dir in [dir for dir in self.graph.dirs if dir in stab.neighbors]:
            if dir == "w":
                X, Y = [x -.25, x + 0], [y + 0, y + 0]
            elif dir == "e":
                X, Y = [x + 0, x + .25], [y + 0, y + 0]
            elif dir == "n":
                X, Y = [x + 0, x + 0], [y -.25, y + 0]
            elif dir == "s":
                X, Y = [x + 0, x + 0], [y + 0, y + .25]

            line = self.draw_line(X, Y, Z=zb * self.z_distance, color=self.cl, lw=self.linewidth, ls=ls, alpha=alpha)
            stab.pg[dir] = line
            line.object = stab


    def plot_qubit(self, qubit):
        '''
        param: qubit        graph.qubit object
        Patch.Circle object for each qubit on the lattice
        '''
        (td, yb, xb) = qubit.qID
        X, Y = (xb+.5, yb) if td == 0 else (xb, yb+.5)
        qubit.pg = plt.Circle(
            (X, Y),
            self.qubitsize,
            edgecolor=self.cq,
            fill=False,
            lw=self.linewidth,
            picker=self.picksize,
        )
        self.ax.add_artist(qubit.pg)
        qubit.pg.object = qubit


    '''
    #########################################################################
                            Plotting functions
    '''
    def get_error_attr(self, qubit):
        '''
        returns plot attributes of a qubit plot if there is an pauli error
        '''
        X_error = qubit.E[0].state
        Z_error = qubit.E[1].state

        attr_dict = {}
        if X_error or Z_error:
            if X_error and not Z_error:
                color = self.cx
            elif Z_error and not X_error:
                color = self.cz
            else:
                color = self.cy
            attr_dict.update(dict(fill=1, facecolor=color, edgecolor=self.cq))
        return attr_dict



    def plot_erasures(self, z=0, draw=True):
        """
        :param erasures         list of locations (TD, y, x) of the erased stab_qubits
        plots an additional blue cicle around the qubits which has been erased
        """
        if z == 0: self.new_iter("Erasure")

        for qubit in self.graph.Q[0].values():
            qplot = qubit.pg

            attr_dict = self.get_error_attr(qubit)

            if qubit.erasure:
                attr_dict.update(dict(linestyle=":"))

            if attr_dict:
                self.new_attributes(qplot, attr_dict)

        if draw: self.draw_plot()


    def plot_errors(self, z=0, plot_qubits=False, draw=True):
        """
        :param arrays       array of qubit states
        plots colored circles within the qubits if there is an error
        """

        if z==0:
            round = "Result" if plot_qubits else "Errors"
            self.new_iter(round)

        for qubit in self.graph.Q[z].values():
            qplot = qubit.pg

            attr_dict = self.get_error_attr(qubit)

            if not attr_dict and plot_qubits:
                attr_dict = dict(fill=0, facecolor=self.cw)

            if attr_dict:
                self.new_attributes(qplot, attr_dict)

        if draw: self.draw_plot()


    def plot_syndrome(self, z=0, draw=True):
        """
        :param qua_loc      list of quasiparticle/anyon positions (y,x)
        plots the vertices of the anyons on the lattice
        """
        if z == 0: self.new_iter("Syndrome")

        for stab in self.graph.S[z].values():
            (ertype, yb, xb) = stab.sID
            if stab.parity:
                for dir in self.graph.dirs:
                    if dir in stab.neighbors:
                        gplot = stab.pg[dir]
                        self.new_attributes(gplot, dict(color=self.C2[ertype]))
        if draw: self.draw_plot()


    def plot_lines(self, matchings):
        """
        :param results      list of matchings of anyon
        plots strings between the two anyons of each match
        """
        P = [0, .5]
        self.new_iter("Matching")

        for _, _, v0, v1 in matchings:

            color = [random.random() * 0.8 + 0.2 for _ in range(3)]

            (type, topy, topx), topz = v0.sID, v0.z
            (type, boty, botx), botz = v1.sID, v1.z
            p, ls = P[type], self.LS[type]

            X = [topx + p, botx + p]
            Y = [topy + p, boty + p]
            Z = [(topz - .5)*self.z_distance, (botz - .5)*self.z_distance]
            lplot = self.draw_line(X, Y, Z=Z, color=color, lw=self.linewidth, ls=ls, alpha=self.alpha)

            self.history[self.iter - 1][lplot] = dict(visible=0)
            self.history[self.iter][lplot] = dict(visible=1)

        self.draw_plot()


    def plot_final(self):
        """
        param: flips        qubits that have flipped in value (y,x)
        param: arrays       data array of the (corrected) qubit states
        plots the applied stabilizer measurements over the lattices
        also, in the qubits that have flipped in value a smaller white circle is plotted

        optionally, the axis is clear and the final state of the lattice is plotted
        """

        plt.sca(self.ax)
        self.new_iter("Final")

        for qubit in self.graph.Q[0].values():
            qplot = qubit.pg
            X_error = qubit.E[0].matching
            Z_error = qubit.E[1].matching

            if X_error or Z_error:
                if X_error and not Z_error:
                    color = self.cx
                elif Z_error and not X_error:
                    color = self.cz
                else:
                    color = self.cy
                self.new_attributes(qplot, dict(edgecolor=color))

        self.draw_plot()
        self.plot_errors(plot_qubits=True)


from mpl_toolkits.mplot3d import Axes3D


class plot_3D(plot_2D):
    '''
    3D axis plot for both toric/planar lattices.

    Plots the qubits as cirlces, including the errors that occur on these qubits.
    Plots the stabilizers, their measurement state and the matching between the stabilizers.
    '''

    '''
    #########################################################################
                            Helper functions
    '''
    def __init__(self, *args, **kwargs):
        self.patch3d_dict = dd(dict)
        super().__init__(*args, **kwargs)

    '''
    #########################################################################
                            Change attribute functions
    '''
    def new_attributes(self, object, attr_dict, overwrite=False):
        '''
        Change plot object attributes

        The 3D plot currently implements a workaround for issue in set_color for Patch3DCollection (scatter) in matplotlib
        https://github.com/matplotlib/matplotlib/issues/13035
        https://github.com/matplotlib/matplotlib/pull/10489
        https://github.com/matplotlib/matplotlib/pull/10797

        Now upon a color change in a 3D scatter object, we apply visible = 0 on the old object and draw a new scatter in the same location.
        These scatter objects are stored as a dictionary of objects. which can be recognized by its type.
        scatter = dict(
            loc = coordindates_of_object,
            key = current_plot_object_key,
            object1_key = object1,
            object2_key = object2,
            .
            .
        )
        Now when iterating through the plot iterations, we find whether the desired version of the plot exists (object_key). If it exists, we swap the visibility. If not, we make a new plot object and add it to the dictionary.
        '''

        if type(object) == dict:

            prev_changes = self.history[self.iter - 1]
            next_changes = self.history[self.iter]

            if "key" in object:
                old_plot = object[object["key"]]

                current_dict = {
                    "facecolor": self.get_nested_np_color(plt.getp(old_plot, "facecolor")),
                    "edgecolor": self.get_nested_np_color(plt.getp(old_plot, "edgecolor")),
                    "linestyle": plt.getp(old_plot, "linestyle"),
                }

                for key, value in current_dict.items():
                    if key not in attr_dict:
                        attr_dict[key] = value

                prev_changes[old_plot] = dict(visible=1, picker=self.picksize)
                next_changes[old_plot] = dict(visible=0, picker=None)
                plt.setp(old_plot, visible=0)
                plt.setp(old_plot, picker=None)

            pdict, new_plot = self.plot_scatter(*object["pos"], pdict=object, **attr_dict)

            prev_changes[new_plot] = dict(visible=0, picker=None)
            next_changes[new_plot] = dict(visible=1, picker=True)

        else:
            super().new_attributes(object, attr_dict, overwrite)

    '''
    #########################################################################
                            Initilize axis
    '''
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


    def init_axis(self, min, max, zl):
        '''
        Initilizes the 3D axis by removing the background panes, changing the grid tics, alpha and linestyle, setting the labels and title.
        '''
        plt.sca(self.ax)

        self.ax = plt.axes(projection='3d', label="main")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("T")

        self.ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        self.ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        self.ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        self.ax.w_xaxis.line.set_color((0, 0, 0, 0.1))
        self.ax.w_yaxis.line.set_color((0, 0, 0, 0.1))
        self.ax.w_zaxis.line.set_color((0, 0, 0, 0.1))

        ticks = [str(i) for i in range(self.size)]

        self.ax.set_xlim(min, max)
        self.ax.set_ylim(min, max)
        self.ax.set_zlim(0, self.size*zl)
        self.ax.set_xticks([i for i in range(self.size)])
        self.ax.set_yticks([i for i in range(self.size)])
        self.ax.set_zticks([i*zl for i in range(self.size)])
        self.ax.set_xticklabels(ticks)
        self.ax.set_yticklabels(ticks)
        self.ax.set_zticklabels(ticks)

        self.ax.xaxis._axinfo["grid"]['linestyle'] = ":"
        self.ax.yaxis._axinfo["grid"]['linestyle'] = ":"
        self.ax.zaxis._axinfo["grid"]['linestyle'] = ":"
        self.ax.xaxis._axinfo["grid"]['alpha'] = 0.2
        self.ax.yaxis._axinfo["grid"]['alpha'] = 0.2
        self.ax.zaxis._axinfo["grid"]['alpha'] = 0.2

    '''
    #########################################################################
                            Initilize plot
    '''
    def init_plot(self, *args, **kwargs):
        '''
        Initializes 3D plot of toric/planar lattice
        Stabilizers are plotted with Axes3D.line objects
        Qubits are plotted with Axes3D.scatter objects
        '''
        self.init_axis(-.25, self.size-.25, self.z_distance)

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
        for layer in self.graph.Q.values():
            for qubit in layer.values():
                (td, yb, xb) = qubit.qID
                X, Y = (xb+.5, yb) if td == 0 else (xb, yb+.5)
                Z = qubit.z * self.z_distance
                pdict, plot = self.plot_scatter(X, Y, Z, object=qubit, facecolor=self.cw, edgecolor=self.cq)
                qubit.pg = pdict

        le_err = self.legend_circle(
            "Erasure", mfc="w", marker="$\u25CC$", mec=self.cq, mew=1, ms=12)
        le_xan = self.legend_circle("X-anyon", marker="*", mfc=self.cx2, mec=self.cx2)
        le_zan = self.legend_circle("Z-anyon", marker="*", mfc=self.cz2, mec=self.cz2)
        self.init_legend(1.05, 0.95, items=[le_err, le_xan, le_zan])
        self.set_axes_equal()
        self.canvas.draw()
        self.draw_plot()

    '''
    #########################################################################
                            Helper plot funtions
    '''
    def scatter_attr(self, facecolor=(0,0,0,0), edgecolor=(0,0,0,0), **kwargs):
        '''
        Part of workarond of Patch3DCollection set_color issue
        Returns attribute dict of new plot and a key identifier for these attributes
        '''

        attr = {
            "facecolor" : facecolor,
            "edgecolor" : edgecolor,
            "s"         : self.scatter_size,
        }
        kwargs.pop("fill", None)
        attr.update(**kwargs)
        name = f"{facecolor[:3]}-{edgecolor[:3]}"
        return attr, name


    def plot_scatter(self, X, Y, Z, object=None, pdict=None, **kwargs):
        '''
        param: qubit        graph.qubit object
        Patch.Circle object for each qubit on the lattice
        '''
        sattr, key = self.scatter_attr(**kwargs)

        if object:
            plot = self.ax.scatter(X, Y, Z, **sattr, picker=True)
            plot.object = object
            pdict = {
                key     : plot,
                "key"   : key,
                "pos"   : (X, Y, Z),
                "object": object,
            }
        else:
            if key in pdict:
                plot = pdict[key]
                plt.setp(plot, visible=1)
                plt.setp(plot, picker=True)
            else:
                plot = self.ax.scatter(X, Y, Z, **sattr, picker=True)
                plot.object = pdict["object"]
                pdict[key] = plot
            pdict["key"] = key

        return pdict, plot


    def draw_line(self, X, Y, Z=0, color="w", lw=2, ls=2, alpha=1, **kwargs):
        '''
        Plots a line onto the plot. Exist for default parameters.
        '''
        return self.ax.plot(X, Y, zs=Z, c=color, lw=lw, ls=ls, alpha=alpha)[0]

    '''
    #########################################################################
                            Plotting functions
    '''

    def plot_syndrome(self, z):
        """
        param: z            z/t layer of 3D plot
        Plots the syndrome by redrawing Axes3D.line plots of the stabilizer.
        Additionally plots scatter object of anyons, that are now in between stabilizers of different z layers
        """

        super().plot_syndrome(z, draw=False)

        for stab in self.graph.S[z].values():
            (ertype, yb, xb) = stab.sID

            if stab.mstate:
                for dir in self.graph.dirs:
                    if dir in stab.neighbors:
                        gplot = stab.pg[dir]
                        self.new_attributes(gplot, dict(linewidth=2*self.linewidth))

            if stab.state:
                X, Y, Z = xb + .5*ertype,  yb + .5*ertype, (z - 1/2) * self.z_distance

                color = self.C2[ertype]
                stab.ap = self.ax.scatter(X, Y, Z, facecolor=color, edgecolor=color, marker="*")

                self.history[self.iter - 1][stab.ap] = dict(visible=0)
                self.history[self.iter][stab.ap] = dict(visible=1)

    def plot_final(self):
        return
