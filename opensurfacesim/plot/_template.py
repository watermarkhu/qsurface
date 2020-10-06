from abc import ABC, abstractmethod
import os
from typing import Optional, Tuple
import matplotlib
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
from matplotlib.blocking_input import BlockingInput
from ..configuration import flatten_dict, get_attributes, init_config
from collections import defaultdict as ddict
from numpy import ndarray
import tkinter


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
        history_at_newest : bool
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
        file = os.path.dirname(os.path.abspath(__file__)) + "/plot.ini"
        config = flatten_dict(init_config(file))
        for key, value in config.items():
            setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.plot_properties = ddict(dict)

        self.figure = None
        self.figure_destroyed = False
        self.main_ax = None
        self.history_dict = ddict(dict)
        self.history_iters = 0
        self.history_iter = 0
        self.history_iter_names = ["Initial"]
        self.history_event_iter = ""
        self.future_dict = ddict(dict)

        # Init figure object
        self.figure = plt.figure(figsize=(self.scale_figure_length, self.scale_figure_height))
        self.canvas = self.figure.canvas
        self.canvas.mpl_connect("pick_event", self._pick_handler)
        self.blocking_input = BlockingKeyInput(self.figure)


        # Init buttons and boxes
        self.main_ax = plt.axes(self.ax_coordinates_main)
        self.main_ax.set_aspect("equal")

        self.interact_axes = {
            "prev_button": plt.axes(self.ax_coordinates_prev_button), 
            "next_button": plt.axes(self.ax_coordinates_next_button)
        }

        self.interact_bodies = {
            "prev_button": Button(self.interact_axes["prev_button"], "Previous"), 
            "next_button": Button(self.interact_axes["next_button"], "Next")
        }
        self.interact_bodies["prev_button"].on_clicked(self._draw_prev)
        self.interact_bodies["next_button"].on_clicked(self._draw_next)

        self.block_box = plt.axes(self.ax_coordinates_block_box)
        self.block_box.axis("off")
        self.block_icon = self.block_box.scatter(0,0, color='r')
        self.text_box = plt.axes(self.ax_coordinates_text_box)
        self.text_box.axis("off")
        self.text = self.text_box.text(
            0.5,
            0.5,
            "",
            fontsize=self.font_default_size,
            va="center",
            ha="center",
            transform=self.text_box.transAxes,
        )
        self.canvas.draw()

        if init_plot:
            self.init_plot()

    def close(self):
        """Closes the class figure."""
        plt.close(self.figure)

    @property
    def history_at_newest(self):
        return self.history_iter == self.history_iters

    """
    -------------------------------------------------------------------------------
                                    Initialization
    -------------------------------------------------------------------------------
    """

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
            ax.set_title(title, fontsize=self.font_title_size)
        for bound in ["top", "right", "bottom", "left"]:
            ax.spines[bound].set_visible(False)
        if invert:
            ax.invert_yaxis()

    def init_properties(self, property_dict: dict):
        """Saves the plot properties from the class attributes into categories."""
        for key, properties in property_dict.items():
            self.plot_properties[key] = get_attributes(self, properties)

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
            self._set_state('g', True)
            try:
                event = self.blocking_input(self.mpl_wait)
                if event.key in ["enter", "right"]:
                    if self.history_event_iter == "":
                        if self.history_at_newest:
                            wait = False
                        else:
                            wait = self._draw_next()
                    else:
                        target_iter = int(self.history_event_iter)
                        self.history_event_iter = ""
                        if target_iter <= self.history_iters:
                            wait = self._draw_iteration(target_iter)
                        else:
                            print("Input iter not in range.")
                elif event.key in ["backspace", "left"]:
                    wait = self._draw_prev()
                elif event.key in [str(i) for i in range(10)]:
                    self.history_event_iter += event.key
                    print("Go to iteration {} (press enter).".format(self.history_event_iter))
                elif event.key == "n":
                    wait = self._draw_iteration(self.history_iters)
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
        self._set_state("r", False)
        return False

    def _set_state(self, color, axis_visibility):
        "Set color of blocking icon."
        for axis in self.interact_axes.values():
            axis.set_visible(axis_visibility)
            self.canvas.blit(axis.bbox)
        self.block_icon.set_color(color)
        self.block_box.draw_artist(self.block_icon)
        self.canvas.blit(self.block_box.bbox)

    """
    -------------------------------------------------------------------------------
                                    Legend functions
    -------------------------------------------------------------------------------
    """

    def _legend_circle(
        self, label, marker="o", ms=10, color="w", mfc=None, mec="k", ls="-", **kwargs
    ) -> Line2D:
        """Returns a Line2D object that is used on the plot legend."""
        return Line2D(
            [0],
            [0],
            lw=self.line_width_primary,
            ls=ls,
            marker=marker,
            color=color,
            mec=mec,
            mew=self.line_width_primary,
            mfc=mfc,
            ms=ms,
            label=label,
            **kwargs,
        )

    """
    -------------------------------------------------------------------------------
                                        History
    -------------------------------------------------------------------------------
    """

    def draw_figure(self, new_iter_name: Optional[str] = None, output: bool = True, **kwargs):
        """Blit the canvas and block code execution.

        Blits all changes to the plot objects drawn by `draw_artist()` onto the canvas and calls for `_wait()` which blocks the code execution and catches user input for history navigation. If a new iteration is called by supplying a `new_iter_name`, we additionally check for future property changes in the `history_dict`, and draw all these planned changes before the canvas is blit.

        Parameters
        ----------
        new_iter_name : str, optional
            Name of the new iteration. If no name is supplied, no new iteration is called.
        output : bool, optional
            Prints information to the console.

        See Also
        --------
        _wait
        change_properties
        """
        if new_iter_name:
            if self.history_at_newest:
                for obj, changes in self.future_dict.pop(new_iter_name, {}).items():
                    self.new_properties(obj, changes)
                for obj, changes in self.future_dict.pop(self.history_iter + 1, {}).items():
                    self.new_properties(obj, changes)
                self.history_iter_names.append(new_iter_name)
                self.history_iters += 1
                self.history_iter += 1
            else:
                print(
                    f"Cannot add iteration {new_iter_name} to history, currently not on most recent iteration."
                )
        if not (new_iter_name and self.history_at_newest):
            new_iter_name = self.history_iter_names[self.history_iter]
        self.text.set_text(new_iter_name)
        if output:
            print("Drawing {}/{}: {}".format(self.history_iter, self.history_iters, new_iter_name))
        self.canvas.blit(self.main_ax.bbox)
        self.figure_destroyed = self._wait(**kwargs)

    def _draw_from_history(
        self, condition: bool, direction: int, draw: bool = True, **kwargs
    ) -> bool:
        """Draws all stored object properties of in either +1 or -1 `direction` in the history if the `condition` is met.

        See Also
        --------
        change_properties
        draw_figure
        """
        if condition:
            self.history_iter += direction
            for obj, changes in self.history_dict[self.history_iter].items():
                self.change_properties(obj, changes)
            if draw:
                self.draw_figure(**kwargs)
        else:
            print("No history exists for this operation.")
            return True
        return False

    def _draw_next(self, *args, **kwargs) -> bool:
        """Redraws all changes from next plot iteration onto the plot

        See Also
        --------
        _draw_from_history
        """
        return self._draw_from_history(self.history_iter < self.history_iters, 1, **kwargs)

    def _draw_prev(self, *args, **kwargs) -> bool:
        """Redraws all changes from previous plot iteration onto the plot

        See Also
        --------
        _draw_from_history
        """
        return self._draw_from_history(self.history_iter > 0, -1, **kwargs)

    def _draw_iteration(self, target: int, draw: bool = True, **kwargs) -> bool:
        """Loops over `_draw_next()` or `_draw_prev()` until the `target` plot iteration is reached.

        See Also
        --------
        _draw_next
        _draw_prev
        """
        if target != self.history_iter:
            diff = target - self.history_iter
            if diff > 0:
                for _ in range(diff):
                    self._draw_next(draw=False, output=False)
            else:
                for _ in range(-diff):
                    self._draw_prev(draw=False, output=False)
            if draw:
                self.draw_figure(**kwargs)
        else:
            print("Already on this plot iteration.")
            return True
        return False

    """
    -------------------------------------------------------------------------------
                                    Object properties
    -------------------------------------------------------------------------------
    """

    def _get_nested_property(self, prop):
        """Get nested color and makes np.array, which is sometimes used for color values, to a list."""

        def get_nested(value):
            if type(value) == list and type(value[0]) == list:
                return get_nested(value[0])
            else:
                return value

        if type(prop) == ndarray:
            return get_nested(prop.tolist())[:3]
        elif type(prop) == list:
            return get_nested(prop)[:3]
        else:
            return prop

    def new_properties(self, obj, prop_dict, **kwargs):
        """Finds the differences of the plot properties between this iteration and the previous iteration and store in history.

        Changes to the plot objects in the figure can be requested via this function. New properties are supplied via the `prop_dict` that contains the properties stored at the appropiate keyword. If any of the new properties is different from its current value, this is seen as a property change. The old property value is stored in history in the previous iteration, and the new property value is stored at the new iteration. The group of new properties, stored in `next_dict`, are draw with `change_properties()`.

        Parameters
        ----------
        obj : matplotlib object
            Plot object whose properties are changed.
        prop_dict : dict
            Dictory with plot properties to change.

        See Also
        --------
        change_properties
        """
        prev_changes = self.history_dict[self.history_iter]
        next_changes = self.history_dict[self.history_iter + 1]
        prev_dict, next_dict = {}, {}

        def find_properties(prop_dict, old_dict=None):
            for key, new_value in prop_dict.items():
                if old_dict and key in old_dict:
                    current_value = old_dict[key]
                else:
                    current_value = self._get_nested_property(plt.getp(obj, key))
                new_value = self._get_nested_property(new_value)
                if current_value != new_value:
                    prev_dict[key], next_dict[key] = current_value, new_value

        # If record exists, find difference in object properties
        if obj not in prev_changes:
            find_properties(prop_dict)
        else:
            old_dict = prev_changes[obj]
            find_properties(prop_dict, old_dict)
        if prev_dict:
            if obj not in prev_changes:
                prev_changes[obj] = prev_dict
            else:
                prev_changes[obj].update(prev_dict)
        if next_dict:
            next_changes[obj] = next_dict
            self.change_properties(obj, next_dict)

    def change_properties(self, obj, prop_dict):
        """Changes the plot properties and draw the plot object or artist."""
        if prop_dict:
            plt.setp(obj, **prop_dict)
