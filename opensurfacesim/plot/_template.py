from abc import ABC, abstractmethod
from typing import Optional, Tuple
import matplotlib
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
from matplotlib.blocking_input import BlockingInput
from ..configuration import flatten_dict, write_config, read_config
from collections import defaultdict as ddict
from numpy import ndarray
import tkinter
import os


mpl.use("TkAgg")


class BlockingKeyInput(BlockingInput):
    """Blocking class to receive key presses.

    See Also
    --------
    matplotlib.blocking_input.BlockingInput : Inherited blocking class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, eventslist=("button_press_event", "key_press_event"), **kwargs)

    def __call__(self, timeout=30):
        """Blocking call to retrieve a single key press."""
        return super().__call__(n=1, timeout=timeout)[-1]


class Template2D(ABC):
    def __init__(self, init_plot: bool = True, **kwargs) -> None:
        """Template 2D plot object with history navigation.

        This template 2D plot object allows fast plotting by use of "blitting", redrawing past iterations of the figure by storing all changes in history, plot object information by picking, and keyboard navigation for iteration selection.

        Fast plotting is enabled by first drawing all recurring objects by `init_plot()`, and updating their properties by `matplotlib.pyplot.setp` and redrawing via `matplotlib.axes.Axes.draw_artist`. All changed properties are not shown until the canvas is blit in bbox.

        History navigation is achieved by storing every change in plot property in a `history_dict`. Moving to another iteration is simply applying the saved changes in plot properties. Again, all properties are not shown until the canvas is blit in bbox. A new iteration can be called by `new_iter()`, after which are new plot properties are saved to the new iteration.

        Keyboard navigation and picking is enabled by blocking the code via a custom `BlockingKeyInput` class. While the code is blocked, inputs are catched by the blocking class and processed for history navigation or picking navigation. Moving the iteration past the available history allows for the code to continue.

        Parameters
        ----------
        init_plot : bool, optional
            Enables drawing all base objects at class initialization.

        Attributes
        ----------
        figure : matplotlib.figure.Figure
            Main figure.
        main_ax : matplotlib.axes.Axes
            Main axis of the figure.
        history_dict : dict of dict of plot properties
            For each iteration, for every plot object with changed properties, the properties are stored as a nested dictionary. See the example below.
        history_iters : int
            Total number of iterations in history.
        history_iter : int
            The current plot iteration.
        history_iter_names : list of str
            List of length `history_iters` containing a title for each iteration.
        history_on_newest : bool
            Whether the current plot iteration is the latest or newest.
        history_event_iter : str
            String catching the keyboard input for the wanted plot iteration.
        future_dict : dict of dict of plot properties
            Same as `history_dict` but for changes for future iterations.

        See Also
        --------
        BlockingKeyInput : Blocking class to receive key presses.
        matplotlib.pyplot.setp : Set a property on an artist object.
        matplotlib.axes.Axes.draw_artist : Efficiently redrawing a artist.
        matplotlib.backend_bases.FigureCanvasBase.blit: Blit the canvas in bbox.

        Example
        -------
        The `history_dict` for a plot with a Line2D object and a Circle object. In the second iteration, the color of the Line2D object is updated from black to red, and the linestyle of the Circle object is changed from "-" to ":".

            >>> history_dict = {
                0: {
                    "<Line2D object>": {
                        "color": "k",
                    },
                    "<Circle object>": {
                        "linestyle": "-",
                    }
                }
                1: {
                    "<Line2D object>": {
                        "color": "r",
                    },
                    "<Circle object>": {
                        "linestyle": ":",
                    }
                }
            }
        """
        config = flatten_dict(self._init_config())
        for key, value in config.items():
            setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.figure = None
        self.main_ax = None
        self.history_dict = ddict(dict)
        self.history_iters = 0
        self.history_iter = 0
        self.history_iter_names = ["Initial"]
        self.history_on_newest = True
        self.history_event_iter = ""
        self.future_dict = ddict(dict)

        # Init figure object
        self.figure = plt.figure(figsize=(self.scale_figure_length, self.scale_figure_height))
        self.canvas = self.figure.canvas
        self.canvas.mpl_connect("pick_event", self._pick_handler)
        self.blocking_input = BlockingKeyInput(self.figure)

        # Init main axis
        self.main_ax = plt.axes(self.ax_coordinates_main)
        self.main_ax.set_aspect("equal")

        # Init buttons and boxes
        self.prev_button = Button(plt.axes(self.ax_coordinates_prev_button), "Previous")
        self.next_button = Button(plt.axes(self.ax_coordinates_next_button), "Next")
        self.prev_button.on_clicked(self._draw_prev)
        self.next_button.on_clicked(self._draw_next)
        self.text_box = plt.axes(self.ax_coordinates_text_box)
        self.text_box.axis("off")
        self.text = self.text_box.text(
            0.5, 0.5, "", fontsize=10, va="center", ha="center", transform=self.text_box.transAxes
        )
        self.canvas.draw()

        if init_plot:
            self.init_plot()

    def close(self):
        """Closes the class figure."""
        plt.close(self.figure)

    """
    -------------------------------------------------------------------------------
                                    Initialization
    -------------------------------------------------------------------------------
    """

    def _init_config(self, write: bool = False, **kwargs):
        """Reads the default and the user defined INI file.

        First, the INI file stored in `opensurfaceim.plot` is read and parsed. If there exists another INI file in the working directory, the attributes defined there are read, parsed and overwrites and default values.

        Parameters
        ----------
        write : bool
            Writes the default configuration to the working direction of the user.

        See Also
        --------
        opensurfacesim.configuration.write_config : Writes a INI file.
        opensurfacesim.configuration.read_config : Reads a INI file.
        """

        config_dict = read_config(os.path.dirname(os.path.abspath(__file__)) + "/plot.ini")
        config_path = "./plot.ini"
        if write:
            write_config(config_dict, config_path)
        if os.path.exists(config_path):
            read_config(config_path, config_dict)
        return config_dict

    @abstractmethod
    def init_plot(self, **kwargs):
        """Initilizes the figure by plotting al main and recurring objects"""
        pass

    def init_axis(
        self,
        limits: Optional[Tuple[float, float, float, float]] = None,
        title: str = "",
        invert: bool = True,
        ax: Optional[mpl.axes.Axes] = None,
    ) -> None:
        """(Main) Axis settings function.

        Parameters
        ----------
        limits : tuple of float of int
            Axis boundaries: `(xmin, ymin, xlength, ylength)`.
        title : str
            Axis title.
        invert : bool
            Invert axis.
        ax : mpl.axes.Axes
            Axis to change.
        """
        if ax is None:
            ax = self.main_ax
        ax.axis(False)
        if limits is not None:
            ax.set_xlim(limits[0], limits[0] + limits[2])
            ax.set_ylim(limits[1], limits[1] + limits[3])
        if title:
            ax.set_title(title)
        for bound in ["top", "right", "bottom", "left"]:
            ax.spines[bound].set_visible(False)
        if invert:
            ax.invert_yaxis()

    """
    -------------------------------------------------------------------------------
                                    Event Handlers
    -------------------------------------------------------------------------------
    """

    def _pick_handler(self, event):
        """Function on when an object in the figure is picked"""
        print(event)

    def _wait(self) -> None:
        """Enables the blocking object, catches input for history navigation.

        When the `_wait` function is called. The BlockingKeyInput object is called which blocks the execution of the code. During this block, the user input is received by the blocking object and return to `_wait`. From here, we can conditionally move through the plot history and call of `_wait` again when all changes in the history have been drawn and blit.

        See Also
        --------
        BlockingKeyInput : Matplotlib blocking object.
        """
        wait = True
        while wait:
            try:
                event = self.blocking_input(self.mpl_wait)
                if event.key in ["enter", "right"]:
                    if self.history_event_iter == "":
                        if self.history_on_newest:
                            wait = False
                        else:
                            self._draw_next()
                    else:
                        target_iter = int(self.history_event_iter)
                        self.history_event_iter = ""
                        if target_iter <= self.history_iters:
                            self._draw_iteration(target_iter)
                        else:
                            print("Input iter not in range.")
                elif event.key in ["backspace", "left"]:
                    self._draw_prev()
                elif event.key in [str(i) for i in range(10)]:
                    self.history_event_iter += event.key
                    print("Go to iteration {} (press enter).".format(self.history_event_iter))
                elif event.key == "n":
                    self._draw_iteration(self.history_iters)
                elif event.key == "i":
                    print("Iterations:")
                    for i, iter_name in enumerate(self.history_iter_names):
                        print(i, iter_name)
                    print()
                elif event.key == "h":
                    print(
                        "Usage:\nenter/right - next iteration\nbackspace/left - previous iteration\ni - show iterations\nn - go to newest iteration\n# - go to iteration #\n"
                    )
            except tkinter.TclError:
                print("Figure has been destroyed. Future plots will be ignored.")
                wait = False
                return True

    """
    -------------------------------------------------------------------------------
                                    Legend functions
    -------------------------------------------------------------------------------
    """

    def _legend_circle(self, label, marker="o", ms=10, color="w", mfc=None, mec="k", mew=2, ls="-", lw=0) -> Line2D:
        """Returns a Line2D object that is used on the plot legend."""
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

    """
    -------------------------------------------------------------------------------
                                        History
    -------------------------------------------------------------------------------
    """

    def draw_figure(self, output: bool = True, **kwargs):
        text = self.history_iter_names[self.history_iter]
        self.text.set_text(text)
        for obj, changes in self.future_dict.pop(text, {}):
            self.change_attributes(obj, changes)
        for obj, changes in self.future_dict.pop(self.history_iter, {}):
            self.change_attributes(obj, changes)
        if output:
            print("Drawing {}/{}: {}".format(self.history_iter, self.history_iters, text))
        self.canvas.blit(self.main_ax.bbox)
        return self._wait(**kwargs)

    def new_iter(self, name: str = ""):
        """Initiates new plot iteration"""
        self.history_iter_names.append(name)
        self.history_iters += 1
        self.history_iter += 1

    def _draw_from_history(self, condition: bool, direction: int, draw: bool = True, **kwargs) -> None:
        if condition:
            self.history_iter += direction
            for obj, changes in self.history_dict[self.history_iter].items():
                self.change_attributes(obj, changes)
            self.on_newest = True if self.history_iter == self.history_iters else False
            if draw:
                self.draw_figure(**kwargs)
        else:
            print("No history exists for this operation.")

    def _draw_next(self, *args, **kwargs) -> None:
        """Redraws all changes from next plot iteration onto the plot"""
        self._draw_from_history(self.history_iter < self.history_iters, 1, **kwargs)

    def _draw_prev(self, *args, **kwargs) -> None:
        """Redraws all changes from previous plot iteration onto the plot"""
        self._draw_from_history(self.history_iter > 0, -1, **kwargs)

    def _draw_iteration(self, target_iter: int, **kwargs) -> None:
        if target_iter == self.history_iter:
            print("Already on this plot iteration.")
        else:
            diff = target_iter - self.history_iter
            if diff > 0:
                for _ in range(diff):
                    self._draw_next(draw=False, output=False)
            else:
                for _ in range(-diff):
                    self._draw_prev(draw=False, output=False)
            self.draw_figure(**kwargs)

    """
    -------------------------------------------------------------------------------
                                    Object attributes
    -------------------------------------------------------------------------------
    """

    def _get_nested_attribute(self, attribute):
        """Get nested color and makes np.array, which is sometimes but not at all times used for color values, to a list."""

        def get_nested(value):
            if type(value) == list and type(value[0]) == list:
                return get_nested(value[0])
            else:
                return value

        if type(attribute) == ndarray:
            return get_nested(attribute.tolist())
        elif type(attribute) == list:
            return get_nested(attribute)
        else:
            return attribute

    def new_attributes(self, obj, attr_dict, overwrite=False):
        """
        Finds the differences of the plot attributes between this iteration and the previous iterations. All differences are stored as dictionaries in the history variable.
        Makes sure that all changes are stored correctly and plot attributes are not overwritten if not explicitly defined.
        """
        prev_changes = self.history_dict[self.history_iter - 1]
        next_changes = self.history_dict[self.history_iter]
        prev_dict, next_dict = {}, {}

        def find_attributes(attr_dict, old_dict=None):
            for key, new_value in attr_dict.items():
                if old_dict and key in old_dict:
                    current_value = old_dict[key]
                else:
                    current_value = self.get_nested_attribute(plt.getp(obj, key))
                new_value = self.get_nested_attribute(new_value)
                if current_value != new_value:
                    prev_dict[key], next_dict[key] = current_value, new_value

        # If record exists, find difference in object attributes
        if not overwrite or obj not in prev_changes:
            find_attributes(attr_dict)
        else:
            old_dict = prev_changes[obj]
            find_attributes(attr_dict, old_dict)

        if prev_dict:
            if overwrite or obj not in prev_changes:
                prev_changes[obj] = prev_dict
            else:
                prev_changes[obj].update(prev_dict)

        if next_dict:
            next_changes[obj] = next_dict
            self.change_attributes(obj, next_dict)

    def change_attributes(self, object, attr_dict):
        """
        Redraws the attributes from the dictionary onto the plot object
        """
        if attr_dict:
            plt.setp(object, **attr_dict)
        self.main_ax.draw_artist(object)

    def get_attributes(self, attribute_names: dict, name: str = "") -> dict:
        attributes = {}
        for key, attribute in attribute_names.items():
            if type(attribute) == str:
                if attribute[0] == "~":
                    attributes[key] = attribute[1:]
                else:
                    try:
                        attributes[key] = getattr(self, attribute)
                    except:
                        if name:
                            print("Parameter {} from {} is not defined in plot.ini.".format(attribute, name))
                        else:
                            print("Parameter {} is not defined in plot.ini.".format(attribute))
        return attributes
