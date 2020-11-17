from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union
from dataclasses import dataclass
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.artist import Artist
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
from matplotlib.blocking_input import BlockingInput
from matplotlib.patches import Circle, Rectangle
from collections import defaultdict
import tkinter
import numpy as np
import os


color_type = Union[str, Tuple[float, float, float, float]]
axis_type = Tuple[float, float, float, float]


@dataclass
class PlotParams:
    """Parameters for the plotting template classes.

    Contains all parameters used in inherited objects of `.Template2D` and `.Template3D`. The dataclass is initialized with many default values for an optimal plotting experience. But if any parameters should be changed, the user can call the class to create its own instance of plotting paramters, where the altered paramters are supplied as keyword arguments. The instance can be supplied to the plotting class via the ``plot_params`` keyword argument.

    Examples
    --------
    See the below example where the background color of the figure is changed to black. Note that we have to inherit from the `.Template2D` class.

        >>> class Plotting(Template2D):
        ...     pass
        >>> custom_params = PlotParams(color_background = (0,0,0,1))
        >>> plot_with_custom_params = Plotting(plot_params=custom_params)
    """

    blocking_wait: float = -1
    blocking_pick_radius: float = 10

    scale_figure_length: float = 10
    scale_figure_height: float = 10
    scale_font_primary: float = 12
    scale_font_secondary: float = 10
    scale_3d_layer: float = 8

    color_background: color_type = (1, 1, 1, 0)
    color_edge: color_type = (0.8, 0.8, 0.8, 1)
    color_qubit_edge: color_type = (0.7, 0.7, 0.7, 1)
    color_qubit_face: color_type = (0.95, 0.95, 0.95, 1)
    color_x_primary: color_type = (0.9, 0.3, 0.3, 1)
    color_z_primary: color_type = (0.5, 0.5, 0.9, 1)
    color_y_primary: color_type = (0.9, 0.9, 0.5, 1)
    color_x_secondary: color_type = (0.9, 0.7, 0.3, 1)
    color_z_secondary: color_type = (0.3, 0.9, 0.3, 1)
    color_y_secondary: color_type = (0.9, 0.9, 0.5, 1)
    color_x_tertiary: color_type = (0.5, 0.1, 0.1, 1)
    color_z_tertiary: color_type = (0.1, 0.1, 0.5, 1)
    color_y_tertiary: color_type = (0.9, 0.9, 0.5, 1)

    alpha_primary: float = 0.35
    alpha_secondary: float = 0.5

    line_width_primary: float = 1.5
    line_width_secondary: float = 3
    line_style_primary: str = "solid"
    line_style_secondary: str = "dashed"
    line_style_tertiary: str = "dotted"

    patch_circle_2d: float = 0.1
    patch_rectangle_2d: float = 0.1
    patch_circle_3d: float = 30
    patch_rectangle_3d: float = 30

    legend_line_width = 1
    legend_marker_size = 10

    axis_main: axis_type = (0.075, 0.1, 0.7, 0.85)
    axis_main_non_interact: axis_type = (0.0, 0.05, 0.8, 0.9)
    axis_block: axis_type = (0.96, 0.01, 0.03, 0.03)
    axis_nextbutton: axis_type = (0.85, 0.05, 0.125, 0.05)
    axis_prevbutton: axis_type = (0.85, 0.12, 0.125, 0.05)
    axis_legend: axis_type = (0.85, 0.5, 0.125, 0.3)
    axis_text: axis_type = (0.05, 0.025, 0.7, 0.05)
    axis_radio: axis_type = (0.85, 0.19, 0.125, 0.125)

    font_default_size: float = 12
    font_title_size: float = 16
    font_button_size: float = 12

    axis3d_pane_color: color_type = (1, 1, 1, 0)
    axis3d_line_color: color_type = (0, 0, 0, 0.1)
    axis3d_grid_line_style: str = "dotted"
    axis3d_grid_line_alpha: float = 0.2

    def load_params(self, param_dict):
        """Loads extra plotting parameters.

        Additional parameters can be loaded to the dataclass via this method. The additional parameters must be a dictionary where values are stored to the dataclass with the key as attribute name. If the value is a string that equals to any already defined dataclass attribute, the value at the existing attribute is used for the new parameter. See examples.

        Parameters
        ----------
        params_dict
            Dictionary or dictionary of dictionaries of additional parameters.

        Examples
        --------
        New parameters can be added to the dataclass. Values of dataclass attributes are used if present.

            >>> params = PlotParams()
            >>> params.alpha_primary
            0.35
            >>> params.load_params({
            ...     "new_attr" : "some_value",
            ...     "use_existing" : "alpha_primary",
            ... })
            >>> params.new_attr
            some_value
            >>> params.use_existing
            0.35

        Nested dictionaries will also load existing attribute values.

            >>> params.load_params({
            ...     "category": {
            ...         "new_attr" : "some_value",
            ...         "use_existing" : "alpha_primary",
            ...     }
            ... })
            >>> params.category
            {"new_attr" : "some_value", "use_existing" : 0.35}
        """
        for attribute, value in param_dict.items():
            if hasattr(self, attribute):
                print(f"Warning, attribute {attribute} already defined.")
            if isinstance(value, dict):
                for sub_attribute, sub_value in value.items():
                    if isinstance(sub_value, str):
                        value[sub_attribute] = getattr(self, sub_value, sub_value)
                    else:
                        value[sub_attribute] = sub_value
                setattr(self, attribute, value)
            else:
                setattr(self, attribute, getattr(self, value, value))


class BlockingKeyInput(BlockingInput):
    """Blocking class to receive key presses.

    See Also
    --------
    `matplotlib.blocking_input.BlockingInput` : Inherited blocking class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, eventslist=("button_press_event", "key_press_event"), **kwargs)

    def __call__(self, timeout=30):
        """Blocking call to retrieve a single key press."""
        return super().__call__(n=1, timeout=timeout)


class Template2D(ABC):
    """Template 2D plot object with history navigation.

    This template plot object which can either be an interactive figure using the Tkinter backend, or shows each plotting iteration as a separate figure for the IPython ``inline`` backend. The interactive figure has the following features.

    - Fast plotting by use of "blitting".
    - Redrawing past iterations of the figure by storing all changes in history.
    - Keyboard navigation for iteration selection.
    - Plot object information by picking.

    To instance this class, one must inherit the current class. The existing objects can then be altered by updating their plot properties by :meth:`new_properties`, where the changed properties must be a dictionary with keywords and values corresponding tho the respective matplotlib object. Every change in plot property is stored in ``self.history_dict``. This allows to undo or redo changes by simply applying the saved changed properties in the dictionary. Fast plotting is enabled by not drawing the figure after every queued change. Instead, each object is draw in the canvas individually after a property change and a series of changes is drawn to the figure when a new plot iteration is requested via :meth:`new_iter`. This is performed by *blitting* the canvas.

    Keyboard navigation and picking is enabled by blocking the code via a custom `.BlockingKeyInput` class. While the code is blocked, inputs are caught by the blocking class and processed for history navigation or picking navigation. Moving the iteration past the available history allows for the code to continue. The keyboard input is parsed by :meth:`focus`.

    Default values for plot properties such as colors and linewidths loaded from `.PlotParams`. A custom parameter dataclass can be supplied via the ``plot_params`` keyword argument.

    Parameters
    ----------
    plot_params
        Plotting parameters dataclass containing colors, styles and others.

    Attributes
    ----------
    figure : `matplotlib.figure.Figure`
        Main figure.
    interactive : bool
       Enables GUI elements and interactive plotting.
    main_ax : `matplotlib.axes.Axes`
        Main axis of the figure.
    history_dict : `.collections.defaultdict`
        For each iteration, for every plot object with changed properties, the properties are stored as a nested dictionary. See the example below.

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

    history_iters : int
        Total number of iterations in history.
    history_iter : int
        The current plot iteration.
    history_iter_names : list of str
        List of length ``history_iters`` containing a title for each iteration.
    history_at_newest : bool
        Whether the current plot iteration is the latest or newest.
    history_event_iter : str
        String catching the keyboard input for the wanted plot iteration.
    future_dict : `.collections.defaultdict`
        Same as ``history_dict`` but for changes for future iterations.
    temporary_changes : `.collections.defaultdict`
        Temporary changes for plot properties, requested by :meth:`temporary_properties`, which are immediately drawn to the figure. These properties can be overwritten or undone before a new iteration is requested via :meth:`new_iter`. When a new iteration is requested, we need to find the difference in properties of the queued changes with the current iteration and save all differences to ``self.history_dict``.
    temporary_saved : `.collections.defaultdict`
        Temporary changes are saved to the current iteration ``iter``. Thus when a new iteration ``iter + 1`` is requested, we need to recalculate the differences of the properties in ``iter-1`` and the current iteration with the temporary changes. The previous property values when temporary changes are requested by :meth:`temporary_properties` are saved to ``self.temporary_saved`` and used as the property changes for ``iter-1``.
    interact_axes : dict of `matplotlib.axes.Axes`
        All iteractive elements should have their own axis saved in ``self.interact_axes``. The ``axis.active`` attribute must be added to define when the axis is shown. If the focus on the figure is lost, all axes in ``self.interact_axes`` are hidden by setting ``axis.active=False``.
    interact_bodies : dict
        All interactive elements such as buttons, radiobuttons, sliders, should be saved to this dictionary with the same key as their axes in ``self.interact_axes``.

    Notes
    -----
    Note all backends support blitting. It does not work with the OSX backend (but does work with other GUI backends on mac).

    Examples
    --------
    A `matplotlib.lines.Line2D` object is initiated with ``color="k"`` and ``ls="-"``. We request that the color of the object is red in a new plot iteration.

        >>> import matplotlib.pyplot as plt
        ... class Example(Template2D):
        ...     def __init__(self, *args, **kwargs):
        ...         super().__init__(*args, **kwargs)
        ...         self.line = plt.plot(0, 0, color="k", ls="-")[0]    # Line located at [0] after plot
        >>> fig = Example()
        >>> fig.new_properties(fig.line, {"color": "r})
        >>> fig.new_iter()
        >>> fig.history_dict
        {
            0: {"<Line2D>": {"color": "k"}},
            1: {"<Line2D>": {"color": "r"}},
        }

    The attribute ``self.history_dict`` thus only contain changes to plot properties. If we request another iteration but change the linestyle to ":", the initial linestyle will be saved to iteration 1.

        >>> fig.new_properties(fig.line, {"ls": ":"})
        >>> fig.new_iter()
        >>> fig.history_dict
        {
            0: {"<Line2D>": {"color": "k"}},
            1: {"<Line2D>": {"color": "r", "ls: "-"}},
            2: {"<Line2D>": {ls: ":"}},
        }

    We temporarily alter the linewidth to 2, and then to 1.5. After we are satisfied with the temporary changes. we request a new iteration with the final change of color to green.

        >>> fig.temporary_properties(fig.line, {"lw": 2})
        >>> fig.temporary_properties(fig.line, {"lw": 1.5})
        >>> fig.temporary_changes
        {"<Line2D>": {"lw": 1.5}}
        >>> fig.temporary_saved
        {"<Line2D>": {"lw": 1}}      # default value
        >>> fig.new_properties(fig.line, {"color": "g"})
        >>> fig.new_iter()
        >>> fig.history_dict
        {
            0: {"<Line2D>": {"color": "k"}},
            1: {"<Line2D>": {"color": "r", "ls: "-", "lw": 1}},
            2: {"<Line2D>": {"lw": 1.5, color": "r"},
            3: {"<Line2D>": {"color": "g"}},
        }

    Properties in ``self.temporary_saved`` are saved to ``self.history_dict`` in the previous iteration, properties in ``self.temporary_changes`` are saved to the current iteration, and new properties are saved to the new iteration.

    The ``history_dict`` for a plot with a Line2D object and a Circle object. In the second iteration, the color of the Line2D object is updated from black to red, and the linestyle of the Circle object is changed from "-" to ":".
    """

    def __init__(
        self,
        plot_params: Optional[PlotParams] = None,
        projection: Optional[str] = None,
        **kwargs,
    ):
        self.interactive = self.load_interactive_backend()
        self.projection = projection
        self.params = plot_params if plot_params else PlotParams()
        self.figure = None
        self.main_ax = None
        self.history_dict = defaultdict(dict)
        self.history_iters = 0
        self.history_iter = 0
        self.history_iter_names = []
        self.history_event_iter = ""
        self.future_dict = defaultdict(dict)
        self.temporary_changes = defaultdict(dict)
        self.temporary_saved = defaultdict(dict)
        self.shown_confirm_close = False

        self.figure = plt.figure(figsize=(self.params.scale_figure_length, self.params.scale_figure_height))
        self.canvas = self.figure.canvas
        # Init buttons and boxes
        self.legend_ax = plt.axes(self.params.axis_legend)
        self.legend_ax.axis("off")

        if self.interactive:
            self.main_ax = plt.axes(self.params.axis_main, projection=self.projection)
            self.canvas.mpl_connect("pick_event", self._pick_handler)
            self.blocking_input = BlockingKeyInput(self.figure)
            self.interact_axes = {
                "prev_button": plt.axes(self.params.axis_prevbutton),
                "next_button": plt.axes(self.params.axis_nextbutton),
            }
            for body in self.interact_axes.values():
                body.active = True
            self.interact_bodies = {
                "prev_button": Button(self.interact_axes["prev_button"], "Previous"),
                "next_button": Button(self.interact_axes["next_button"], "Next"),
            }
            self.interact_bodies["prev_button"].on_clicked(self._draw_prev)
            self.interact_bodies["next_button"].on_clicked(self._draw_next)
            self.block_box = plt.axes(self.params.axis_block)
            self.block_box.axis("off")
            self.block_icon = self.block_box.scatter(0, 0, color="r")
        else:
            self.main_ax = plt.axes(self.params.axis_main_non_interact, projection=self.projection)

        self.text_box = plt.axes(self.params.axis_text)
        self.text_box.axis("off")
        self.text = self.text_box.text(
            0.5,
            0.5,
            "",
            fontsize=self.params.font_default_size,
            va="center",
            ha="center",
            transform=self.text_box.transAxes,
        )
        if self.interactive:
            self.canvas.draw()

    def load_interactive_backend(self) -> bool:
        """Configures the plotting backend.

        If the Tkinter backend is enabled or can be enabled, the function returns True. For other backends False is returned.
        """
        backend = mpl.get_backend().lower()
        if backend in ["tkagg", "qt5agg"]:
            return True
        elif "inline" in backend:
            from IPython.display import display

            self.display = display
        else:
            DISPLAY = os.environ.get("DISPLAY", None)
            if DISPLAY:
                try:
                    mpl.use("TkAgg")
                    return True
                except ImportError:
                    pass
                try:
                    mpl.use("Qt5Agg")
                    return True
                except ImportError:
                    pass

                print(f"Matplotlib is using {backend} backend, which is not supported.")
            else:
                print(f"Display {DISPLAY} not available. Interactive plotting is disabled.")
        return False

    def close(self):
        """Closes the figure."""
        if self.interactive:
            self.draw_figure("Press (->/enter) to close figure.")
            plt.close(self.figure)

    @property
    def history_at_newest(self):
        return self.history_iter == self.history_iters

    """
    -------------------------------------------------------------------------------
                                    Initialization
    -------------------------------------------------------------------------------
    """

    def _init_axis(
        self,
        limits: Optional[Tuple[float, float, float, float]] = None,
        title: str = "",
        invert: bool = True,
        aspect: str = "",
        ax: Optional[mpl.axes.Axes] = None,
        **kwargs,
    ):
        """(Main) Axis settings function.

        Parameters
        ----------
        limits
            Axis boundaries
        title
            Axis title.
        invert
            Invert axis.
        ax
            Axis to change.
        """
        if ax is None:
            ax = self.main_ax
        ax.axis(False)
        if limits is not None:
            ax.set_xlim(limits[0], limits[0] + limits[2])
            ax.set_ylim(limits[1], limits[1] + limits[3])
        if title:
            ax.set_title(title, fontsize=self.params.font_title_size)
        for bound in ["top", "right", "bottom", "left"]:
            ax.spines[bound].set_visible(False)
        if invert:
            ax.invert_yaxis()
        if aspect:
            self.main_ax.set_aspect(aspect)

    """
    -------------------------------------------------------------------------------
                                    Event Handlers
    -------------------------------------------------------------------------------
    """

    def _pick_handler(self, event):
        """Function on when an object in the figure is picked"""
        print(event)

    def focus(self):
        """Enables the blocking object, catches input for history navigation.

        The BlockingKeyInput object is called which blocks the execution of the code. During this block, the user input is received by the blocking object and return to the current method. From here, we can manipulate the plot or move through the plot history and call :meth:`focus` again when all changes in the history have been drawn and blit.

        ==================  ==============================================
        key                 function
        ==================  ==============================================
        h                   show help
        i                   show all iterations
        d                   redraw current iteration
        enter or right      go to next iteration, enter iteration number
        backspace or left   go to previous iteration
        n                   go to newest iteration
        0-9                 input iteration number
        ==================  ==============================================

        When the method is active, the focus is on the figure. This will be indicated by a green circle in the bottom right of the figure. When the focus is lost, the code execution is continued and the icon is red. The change is icon color is performed by :meth:`_set_figure_state`, which also hides the interactive elements when the focus is lost.
        """
        self.canvas.draw()
        wait = True
        while wait:
            self._set_figure_state("g")
            try:
                output = self.blocking_input(self.params.blocking_wait)

                if output == []:
                    if self.history_at_newest:
                        wait = False
                    else:
                        wait = self._draw_next()
                    continue
                else:
                    event = output[-1]

                if hasattr(event, "button"):  # Catch next button if on most recent
                    if (
                        event.button == 1
                        and event.inaxes == self.interact_axes["next_button"]
                        and self.history_iter == self.history_iters
                    ):
                        wait = False
                elif event.key in ["return", "right"]:
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
                    print("Go to iteration {} (press return).".format(self.history_event_iter))
                elif event.key == "n":
                    wait = self._draw_iteration(self.history_iters)
                elif event.key == "i":
                    print("Iterations:")
                    for i, iter_name in enumerate(self.history_iter_names):
                        print(i, iter_name)
                    print()
                elif event.key == "h":
                    print(self.focus.__doc__)
                elif event.key == "d":
                    self.draw_figure()
            except tkinter.TclError:
                print("Figure has been destroyed. Future plots will be ignored.")
                wait = False
        self._set_figure_state("r", False)  # Hide all interactive axes

    def _set_figure_state(self, color, override: Optional[bool] = None):
        """Set color of blocking icon and updates interactive axes visibility.

        Parameters
        ----------
        color
            Color of `self.block_icon`.
        override
            Overrides the visibility of axes in `self.interact_axes`.
        """
        for ax in self.interact_axes.values():
            if override is None:
                ax.set_visible(ax.active)
            else:
                ax.set_visible(override)
        self.block_icon.set_color(color)
        self.block_box.draw_artist(self.block_icon)
        self.canvas.blit(self.block_box.bbox)
        self.canvas.draw()

    """
    -------------------------------------------------------------------------------
                                    Legend functions
    -------------------------------------------------------------------------------
    """
    # marker="o", ms=10, color="w", mfc=None, mec="k", ls="-"

    def _legend_circle(self, label: str, **kwargs) -> Line2D:
        """Returns a Line2D object that is used on the plot legend."""
        return Line2D(
            [],
            [],
            lw=self.params.legend_line_width,
            mew=self.params.legend_line_width,
            label=label,
            **kwargs,
        )

    def _legend_scatter(self, label: str, **kwargs):
        line = Line2D(
            [],
            [],
            label=label,
            lw=self.params.legend_line_width,
            mew=self.params.legend_line_width,
            color=self.params.color_edge,
        )
        scatter = plt.scatter([], [], s=8 ** 2, **kwargs)
        return (line, scatter)

    def _draw_line(self, X: list, Y: list, *args, z: float = 0, **kwargs):
        artist = Line2D(X, Y, *args, **kwargs)
        self.main_ax.add_line(artist)
        return artist

    def _draw_circle(self, xy: tuple, size: float, *args, z: float = 0, **kwargs):
        artist = Circle(xy, size, *args, **kwargs)
        self.main_ax.add_patch(artist)
        return artist

    def _draw_rectangle(self, xy: tuple, size_x: float, size_y: float, *args, z: float = 0, **kwargs):
        artist = Rectangle(xy, size_x, size_y, *args, **kwargs)
        self.main_ax.add_patch(artist)
        return artist

    """
    -------------------------------------------------------------------------------
                                        History
    -------------------------------------------------------------------------------
    """

    def draw_figure(
        self,
        new_iter_name: Optional[str] = None,
        output: bool = True,
        carriage_return: bool = False,
        **kwargs,
    ):
        """Draws the canvas and blocks code execution.

        Draws the queued plot changes onto the canvas and calls for :meth:`focus` which blocks the code execution and catches user input for history navigation.

        If a new iteration is called by supplying a `new_iter_name`, we additionally check for future property changes in the `self.future_dict`, and add these changes to the queue. Finally, all queued property changes for the next iteration are applied by `change_properties`.

        Parameters
        ----------
        new_iter_name
            Name of the new iteration. If no name is supplied, no new iteration is called.
        output
            Prints information to the console.
        carriage_return
            Applies carriage return to remove last line printed.

        See Also
        --------
        focus
        change_properties
        """
        # if self.interactive:
        if new_iter_name:
            if self.history_at_newest:
                for artist, changes in self.future_dict.pop(new_iter_name, {}).items():
                    self.new_properties(artist, changes)
                for artist, changes in self.future_dict.pop(self.history_iter + 1, {}).items():
                    self.new_properties(artist, changes)
                for artist, changes in self.history_dict[self.history_iter + 1].items():
                    self.change_properties(artist, changes)
                self.history_iter_names.append(new_iter_name)
                self.history_iters += 1
                self.history_iter += 1
            else:
                print(f"Cannot add iteration {new_iter_name} to history, currently not on most recent iteration.")
        if not (new_iter_name and self.history_at_newest):
            new_iter_name = self.history_iter_names[self.history_iter - 1]
        text = "{}/{}: {}".format(self.history_iter, self.history_iters, new_iter_name)
        self.text.set_text(text)

        if output:
            if carriage_return:
                print("\rDrawing", text)
            else:
                print("Drawing", text)

        if self.interactive:
            self.canvas.blit(self.main_ax.bbox)
            self.focus()
        else:
            self.display(self.figure)

    def _draw_from_history(self, condition: bool, direction: int, draw: bool = True, **kwargs) -> bool:
        """Move a single plot iteration forward or backwards.

        Draws all stored object properties of in either +1 or -1 `direction` in the history if the `condition` is met. If there are any properties stored in `self.temporary_changes`, these settings are first parsed and saved to the current and previous iterations.

        Parameters
        ----------
        condition
            Must be true for navigation.
        direction
            Moves either a single iteration forward or backwards in time.
        draw
            Draws the figure and blocks the code immediately with :meth:`draw_figure`.

        Returns
        -------
        bool
            True if focus is kept, False if lost.
        """
        if condition:
            # Save temporary changes
            if self.history_at_newest and self.temporary_changes:
                for artist, properties in self.temporary_changes.items():
                    self.new_properties(artist, properties, self.temporary_saved.pop(artist))
                self.temporary_changes = {}

            self.history_iter += direction
            for artist, changes in self.history_dict[self.history_iter].items():
                self.change_properties(artist, changes)
            if draw:
                self.draw_figure(**kwargs)
            return False
        else:
            print("Nothing to plot.")
            return True

    def _draw_next(self, *args, **kwargs) -> bool:
        """Redraws all changes from next plot iteration onto the plot."""
        return self._draw_from_history(self.history_iter < self.history_iters, 1, **kwargs)

    def _draw_prev(self, *args, **kwargs) -> bool:
        """Redraws all changes from previous plot iteration onto the plot."""
        self.shown_confirm_close = False
        return self._draw_from_history(self.history_iter > 1, -1, **kwargs)

    def _draw_iteration(self, target: int, draw: bool = True, **kwargs) -> bool:
        """Redraws all changes until the `target` iteration.

        Loops over :meth:`_draw_next` or :meth:`_draw_prev` until the `target` plot iteration is reached. Note that this means that all the changes from the current iteration until the target iteration in `self.history_dict` are applied.

        Parameters
        ----------
        target
            Target plot iteration.
        draw
            Draws the figure and blocks the code immediately with :meth:`draw_figure`.

        Returns
        -------
        bool
            True if focus is kept, False if lost.
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

    def new_artist(self, artist: mpl.artist.Artist, axis: Optional[mpl.axes.Axes] = None) -> None:
        """Adds a new artist to the ``axis``.

        Newly added artists must be hidden in the previous iteration. To make sure the history is properly logged, the visibility of the ``artist`` is set to ``False``, and a new property of shown visibility is added to the queue of the next iteration.

        Parameters
        ----------
        artist
            New plot artist to add to the ``axis``.
        axis
            Axis to add the figure to.
        """
        if axis is None:
            axis = self.main_ax
        self.change_properties(artist, {"visible": False})
        self.new_properties(artist, {"visible": True})

    @staticmethod
    def change_properties(artist, prop_dict):
        """Changes the plot properties and draw the plot object or artist."""
        if prop_dict:
            plt.setp(artist, **prop_dict)

    def new_properties(self, artist: Artist, properties: dict, saved_properties: dict = {}, **kwargs):
        """Parses a dictionary of property changes of a *matplotlib* artist.

        New properties are supplied via ``properties``. If any of the new properties is different from its current value, this is seen as a property change. The old property value is stored in ``self.history_dict[self.history_iteration]``, and the new property value is stored at ``self.history_dict[self.history_iteration+1]``. These new properties are *queued* for the next interation. The queue is emptied by applying all changes when `draw_figure` is called. If the same property changes 2+ times within the same iteration, the previous property change is removed with ``next_prop.pop(key, None)``.

        The ``saved_properties`` parameter is used when temporary property changes have been applied by `temporary_changes`, in which the original properties are saved to ``self.temporary_saved`` as the saved properties. Before a new iteration is drawn, the temporary changes, which can be overwritten, are compared with the saved changes and the differences in properties are saved to ``[self.history_dict[self.history_iter-1]]`` and ``self.history_dict[self.history_iteration]``.

        Some color values from different *matplotlib* objects are nested, some are list or tuple, and others may be a `.numpy.ndarray`. The nested methods `get_nested()` and `get_nested_property()` make sure that the return type is always a list.

        Parameters
        ----------
        artist
            Plot object whose properties are changed.
        properties
            Plot properties to change.
        saved_properties
            Override current properties and parse previous and current history.
        """

        def get_nested(value):
            if type(value) == list and type(value[0]) == list:
                return get_nested(value[0])
            else:
                return value

        def get_nested_property(prop):
            if type(prop) == np.ndarray:
                return get_nested(prop.tolist())[:3]
            elif type(prop) == list:
                return get_nested(prop)[:3]
            else:
                return prop

        if saved_properties:
            prev_properties = self.history_dict[self.history_iter - 1]
            next_properties = self.history_dict[self.history_iter]
        else:
            prev_properties = self.history_dict[self.history_iter]
            next_properties = self.history_dict[self.history_iter + 1]

        prev_prop = prev_properties.pop(artist, {})
        prev_prop.update(saved_properties)
        next_prop = next_properties.pop(artist, {})

        # If record exists, find difference in object properties
        for key, new_value in properties.items():
            current_value = prev_prop.get(key, get_nested_property(plt.getp(artist, key)))
            next_prop.pop(key, None)
            if current_value != new_value:
                prev_prop[key], next_prop[key] = current_value, new_value

        if prev_prop:
            prev_properties[artist] = prev_prop
        if next_prop:
            next_properties[artist] = next_prop

    def temporary_properties(self, artist: Artist, properties: dict, **kwargs):
        """Applies temporary property changes to a *matplotlib* artist.

        Only available on the newest iteration, as we cannot change what is already in the past. All values in ``properties`` are immediately applied to `artist`. Since temporary changes can be overwritten within the same iteration, the first time a temporary property change is requested, the previous value is saved to ``self.temporary_saved``. When the iteration changes, the property differences of the previous and current iteration are recomputed and saved to ``self.history_dict`` in :meth:`_draw_from_history`.

        Parameters
        ----------
        artist
            Plot object whose properties are changed.
        properties
            Plot properties to change.
        """
        if self.history_at_newest:
            self.temporary_changes[artist].update(properties)
            for prop_name in properties:
                if prop_name not in self.temporary_saved[artist]:
                    self.temporary_saved[artist][prop_name] = plt.getp(artist, prop_name)
            self.change_properties(artist, properties)
        else:
            print("Must be at newest iteration to apply changes.")


from mpl_toolkits.mplot3d import art3d


class Template3D(Template2D):
    """Template 3D plot object with history navigation."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, projection="3d", **kwargs)

    def _init_axis(
        self,
        limits: Optional[Tuple[float, float, float, float]] = None,
        title: str = "",
        invert: bool = True,
        ax: Optional[mpl.axes.Axes] = None,
        z_limits: Optional[Tuple[float, float]] = None,
        **kwargs,
    ):
        """
        Initializes the 3D axis by removing the background panes, changing the grid tics, alpha and linestyle, setting the labels and title.
        """
        if ax is None:
            ax = self.main_ax
        ax.axis(False)
        if title:
            ax.set_title(title, fontsize=self.params.font_title_size)

        ax.set_xlabel("z")
        ax.set_ylabel("y")
        ax.set_zlabel("t")
        ax.xaxis.set_pane_color(self.params.axis3d_pane_color)
        ax.yaxis.set_pane_color(self.params.axis3d_pane_color)
        ax.zaxis.set_pane_color(self.params.axis3d_pane_color)
        ax.xaxis.line.set_color(self.params.axis3d_line_color)
        ax.yaxis.line.set_color(self.params.axis3d_line_color)
        ax.zaxis.line.set_color(self.params.axis3d_line_color)
        ax.xaxis._axinfo["grid"]["linestyle"] = self.params.axis3d_grid_line_style
        ax.yaxis._axinfo["grid"]["linestyle"] = self.params.axis3d_grid_line_style
        ax.zaxis._axinfo["grid"]["linestyle"] = self.params.axis3d_grid_line_style
        ax.xaxis._axinfo["grid"]["alpha"] = self.params.axis3d_grid_line_alpha
        ax.yaxis._axinfo["grid"]["alpha"] = self.params.axis3d_grid_line_alpha
        ax.zaxis._axinfo["grid"]["alpha"] = self.params.axis3d_grid_line_alpha

        if limits is not None:
            ax.set_xlim(limits[0], limits[0] + limits[2])
            ax.set_ylim(limits[1], limits[1] + limits[3])
        if z_limits is not None:
            ax.set_zlim(z_limits[0], z_limits[0] + z_limits[1])
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()
        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = sum(x_limits) / len(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = sum(y_limits) / len(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = sum(z_limits) / len(z_limits)
        plot_radius = 0.5 * max([x_range, y_range, z_range])
        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
        if invert:
            ax.invert_yaxis()

    def _draw_line(self, X, Y, *args, z: float = 0, **kwargs):
        artist = super()._draw_line(np.array(X), np.array(Y), *args, **kwargs)
        art3d.line_2d_to_3d(artist, zs=z)
        return artist

    def _draw_line3D(self, X, Y, Z, *args, **kwargs):
        artist = art3d.Line3D(X, Y, Z, *args, **kwargs)
        self.main_ax.add_line(artist)
        return artist

    def _draw_circle(self, *args, z: float = 0, **kwargs):
        artist = super()._draw_circle(*args, **kwargs)
        art3d.patch_2d_to_3d(artist, z=z)
        return artist

    def _draw_rectangle(self, *args, z: float = 0, **kwargs):
        artist = super()._draw_rectangle(*args, **kwargs)
        art3d.patch_2d_to_3d(artist, z=z)
        return artist
