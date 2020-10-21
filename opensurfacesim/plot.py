from abc import ABC, abstractmethod
from typing import Optional, Tuple
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.artist import Artist
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
from matplotlib.blocking_input import BlockingInput
from collections import defaultdict
from .configuration import flatten_dict, init_config
import tkinter
import numpy
from pathlib import Path


mpl.use("TkAgg")


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
        return super().__call__(n=1, timeout=timeout)[-1]


class Template2D(ABC):
    """Template 2D plot object with history navigation.

    This template plot object has the following features:

    - Fast plotting by use of "blitting".
    - Redrawing past iterations of the figure by storing all changes in history.
    - Keyboard navigation for iteration selection.
    - Plot object information by picking.

    To instance this class, one must inherit the current class and supply a :meth:`init_plot` method that draws the objects of the plot. The existing objects can then be altered by updating their plot properties by :meth:`new_properties`, where the changed properties must be a dictionary with keywords and values corresponding tho the respective matplotlib object. Every change in plot property is stored in `self.history_dict`. This allows to undo or redo changes by simply applying the saved changed properties in the dictionary.

    Fast plotting is enabled by not drawing the figure after every queued change. Instead, each object is draw in the canvas individually after a property change and a series of changes is drawn to the figure when a new plot iteration is requested via :meth:`new_iter`. This is performed by *blitting* the canvas.

    Keyboard navigation and picking is enabled by blocking the code via a custom `.BlockingKeyInput` class. While the code is blocked, inputs are caught by the blocking class and processed for history navigation or picking navigation. Moving the iteration past the available history allows for the code to continue. The keyboard input is parsed by :meth:`focus`.

    Default values for plot properties such as colors and linewidths are saved in a 'plot.ini` file. All parameters within the ini file are parsed by :meth:`~opensurfacesim.configuration.read_config` and saved to ``self.rc`` as a dictionary.

    Parameters
    ----------
    init_plot : bool, optional
        Enables drawing all base objects at class initialization.

    Attributes
    ----------
    figure : `matplotlib.figure.Figure`
        Main figure.
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
        List of length `history_iters` containing a title for each iteration.
    history_at_newest : bool
        Whether the current plot iteration is the latest or newest.
    history_event_iter : str
        String catching the keyboard input for the wanted plot iteration.
    future_dict : `.collections.defaultdict`
        Same as `history_dict` but for changes for future iterations.
    temporary_changes : `.collections.defaultdict`
        Temporary changes for plot properties, requested by :meth:`temporary_properties`, which are immediately drawn to the figure. These properties can be overwritten or undone before a new iteration is requested via :meth:`new_iter`. When a new iteration is requested, we need to find the difference in properties of the queued changes with the current iteration and save all differences to `self.history_dict`.
    temporary_saved : `.collections.defaultdict`
        Temporary changes are saved to the current iteration ``iter``. Thus when a new iteration ``iter + 1`` is requested, we need to recalculate the differences of the properties in ``iter -1`` and the current iteration with the temporary changes. The previous property values when temporary changes are requested by :meth:`temporary_properties` are saved to `self.temporary_saved` and used as the property changes for ``iter -``.
    interact_axes : dict of `matplotlib.axes.Axes'
        All iteractive elements should have their own axis saved in ``self.interact_axes``. The ``axis.active`` attribute must be added to define when the axis is shown. If the focus on the figure is lost, all axes in ``self.interact_axes`` are hidden by setting ``axis.active`` to ``False``. See :meth:`_set_figure_state`.
    interact_bodies : dict
        All interactive elements such as buttons, radiobuttons, sliders, should be saved to this dictionary with the same key as their axes in ``s`elf.interact_axes``

    Notes
    -----
    Note all backends support blitting. You can check if a given canvas does via the `matplotlib.backend_bases.FigureCanvasBase.supports_blit` property. It does not work with the OSX backend (but does work with other GUI backends on mac).

    Examples
    --------
    A `matplotlib.lines.Line2D` object is initiated with ``color="k"`` and ``ls="-"``. We request that the color of the object is red in a new plot iteration.

        >>> import matplotlib.pyplot as plt
        ... class Example(Template2D):
        ...     def init_plot(self):
        ...         self.line = plt.plot(0, 0, color="k", ls="-")[0]    # Line located at [0] after plot
        >>> fig = Example()
        >>> fig.new_properties(fig.line, {"color": "r})
        >>> fig.new_iter()
        >>> fig.history_dict
        {
            0: {"<Line2D>": {"color": "k"}},
            1: {"<Line2D>": {"color": "r"}},
        }

    The attribute ``self.history_dict`` thus only contain changes to plot properties. If we request another iteration but change the linestyle to ``":"``, the initial linestyle will be saved to iteration 1.

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

    The ``history_dict`` for a plot with a Line2D object and a Circle object. In the second iteration, the color of the Line2D object is updated from black to red, and the linestyle of the Circle object is changed from ``"-"`` to ``":"``.
    """
    def __init__(self, init_plot: bool = True, **kwargs):

        file = Path(__file__).resolve().parent / "plot.ini"
        self.rc = flatten_dict(init_config(file))
        self.rc.update(kwargs)

        self.figure = None
        self.main_ax = None
        self.history_dict = defaultdict(dict)
        self.history_iters = 0
        self.history_iter = 0
        self.history_iter_names = ["Initial"]
        self.history_event_iter = ""
        self.future_dict = defaultdict(dict)
        self.temporary_changes = defaultdict(dict)
        self.temporary_saved = defaultdict(dict)

        # Init figure object
        self.figure = plt.figure(
            figsize=(self.rc["scale_figure_length"], self.rc["scale_figure_height"])
        )
        self.canvas = self.figure.canvas
        self.canvas.mpl_connect("pick_event", self._pick_handler)
        self.blocking_input = BlockingKeyInput(self.figure)

        # Init buttons and boxes
        self.main_ax = plt.axes(self.rc["axis_main"])
        self.main_ax.set_aspect("equal")
        self.legend_ax = plt.axes(self.rc["axis_legend"])
        self.legend_ax.axis("off")

        self.interact_axes = {
            "prev_button": plt.axes(self.rc["axis_prevbutton"]),
            "next_button": plt.axes(self.rc["axis_nextbutton"]),
        }
        for body in self.interact_axes.values():
            body.active = True
        self.interact_bodies = {
            "prev_button": Button(self.interact_axes["prev_button"], "Previous"),
            "next_button": Button(self.interact_axes["next_button"], "Next"),
        }
        self.interact_bodies["prev_button"].on_clicked(self._draw_prev)
        self.interact_bodies["next_button"].on_clicked(self._draw_next)
        self.block_box = plt.axes(self.rc["axis_block"])
        self.block_box.axis("off")
        self.block_icon = self.block_box.scatter(0, 0, color="r")
        self.text_box = plt.axes(self.rc["axis_text"])
        self.text_box.axis("off")
        self.text = self.text_box.text(
            0.5,
            0.5,
            "",
            fontsize=self.rc["font_default_size"],
            va="center",
            ha="center",
            transform=self.text_box.transAxes,
        )
        self.canvas.draw()

        if init_plot:
            self.init_plot()

    def close(self):
        """Closes the figure."""
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
        """Initializes the figure by plotting al main and recurring objects"""
        pass

    def _init_axis(
        self,
        limits: Optional[Tuple[float, float, float, float]] = None,
        title: str = "",
        invert: bool = True,
        ax: Optional[mpl.axes.Axes] = None,
        **kwargs,
    ):
        """(Main) Axis settings function.

        Parameters
        ----------
        limits : tuple, (xmin, ymin, xlength, ylength)
            Axis boundaries
        title : str
            Axis title.
        invert : bool
            Invert axis.
        ax : `matplotlib.axes.Axes`
            Axis to change.
        """
        if ax is None:
            ax = self.main_ax
        ax.axis(False)
        if limits is not None:
            ax.set_xlim(limits[0], limits[0] + limits[2])
            ax.set_ylim(limits[1], limits[1] + limits[3])
        if title:
            ax.set_title(title, fontsize=self.rc["font_title_size"])
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

    def focus(self):
        """Enables the blocking object, catches input for history navigation.

        The BlockingKeyInput object is called which blocks the execution of the code. During this block, the user input is received by the blocking object and return to the current method. From here, we can manipulate the plot or move through the plot history and call :meth:`focus` again when all changes in the history have been drawn and blit.

        ==================  ==============================================
        key                 function
        ==================  ==============================================
        h                   show help
        i                   show all iterations
        enter or right      go to next iteration, enter iteration number
        backspace or left   go to previous iteration
        n                   go to newest iteration
        0-9                 input iteration number
        ==================  ==============================================

        When the method is active, the focus is on the figure. This will be indicated by a green circle in the bottom right of the figure. When the focus is lost, the code execution is continued and the icon is red. The change is icon color is performed by :meth:`_set_figure_state`, which also hides the interactive elements when the focus is lost.
        """
        wait = True
        while wait:
            self._set_figure_state("g")
            try:
                event = self.blocking_input(self.rc["mpl_wait"])
                if hasattr(event, "button"):  # Catch next button if on most recent
                    if (
                        event.button == 1
                        and event.inaxes == self.interact_axes["next_button"]
                        and self.history_iter == self.history_iters
                    ):
                        wait = False
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
        self._set_figure_state("r", False)  # Hide all interactive axes
        self.canvas.draw()  # Draw before focus is lost


    def _set_figure_state(self, color, override: Optional[bool] = None):
        """Set color of blocking icon and updates interactive axes visibility.

        Parameters
        ----------
        color : {"r","g", (1,0,0), (0,1,0), ...}
            Color of `self.block_icon`.
        override : bool, optional
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

    """
    -------------------------------------------------------------------------------
                                    Legend functions
    -------------------------------------------------------------------------------
    """
    # marker="o", ms=10, color="w", mfc=None, mec="k", ls="-"
    def _legend_circle(self, label: str, **kwargs) -> Line2D:
        """Returns a Line2D object that is used on the plot legend."""
        return Line2D(
            [0],
            [0],
            lw=self.rc["legend_line_width"],
            mew=self.rc["legend_line_width"],
            label=label,
            **kwargs,
        )

    """
    -------------------------------------------------------------------------------
                                        History
    -------------------------------------------------------------------------------
    """

    def draw_figure(self, new_iter_name: Optional[str] = None, output: bool = True, carriage_return: bool = False, **kwargs):
        """Draws the canvas and blocks code execution.

        Draws the queued plot changes onto the canvas and calls for :meth:`focus` which blocks the code execution and catches user input for history navigation. 
        
        If a new iteration is called by supplying a `new_iter_name`, we additionally check for future property changes in the `self.future_dict`, and add these changes to the queue. Finally, all queued property changes for the next iteration are applied by `change_properties`. 

        Parameters
        ----------
        new_iter_name : str, optional
            Name of the new iteration. If no name is supplied, no new iteration is called.
        output : bool, optional
            Prints information to the console.
        carriage_return : bool, optional
            Applies carriage return to remove last line printed.

        See Also
        --------
        focus
        change_properties
        """
        if new_iter_name:
            if self.history_at_newest:
                for artist, changes in self.future_dict.pop(new_iter_name, {}).items():
                    self.new_properties(artist, changes)
                for artist, changes in self.future_dict.pop(self.history_iter + 1, {}).items():
                    self.new_properties(artist, changes)
                for artist, changes in self.history_dict[self.history_iter+1].items():
                    self.change_properties(artist, changes)
                self.history_iter_names.append(new_iter_name)
                self.history_iters += 1
                self.history_iter += 1
            else:
                print(
                    f"Cannot add iteration {new_iter_name} to history, currently not on most recent iteration."
                )
        if not (new_iter_name and self.history_at_newest):
            new_iter_name = self.history_iter_names[self.history_iter]
        text = "{}/{}: {}".format(self.history_iter, self.history_iters, new_iter_name)
        self.text.set_text(text)
        if output:
            if carriage_return:
                print("\rDrawing", text)
            else:
                print("Drawing", text)
        self.canvas.blit(self.main_ax.bbox)
        self.focus()

    def _draw_from_history(
        self, condition: bool, direction: int, draw: bool = True, **kwargs
    ) -> bool:
        """Move a single plot iteration forward or backwards. 
        
        Draws all stored object properties of in either +1 or -1 `direction` in the history if the `condition` is met. If there are any properties stored in `self.temporary_changes`, these settings are first parsed and saved to the current and previous iterations. 

        Parameters
        ----------
        condition : bool
            Must be true for navigation.
        direction : int, {1, -1}
            Moves either a single iteration forward or backwards in time. 
        draw : bool, optional
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
        else:
            print("No history exists for this operation.")
            return True
        return False

    def _draw_next(self, *args, **kwargs) -> bool:
        """Redraws all changes from next plot iteration onto the plot."""
        return self._draw_from_history(self.history_iter < self.history_iters, 1, **kwargs)

    def _draw_prev(self, *args, **kwargs) -> bool:
        """Redraws all changes from previous plot iteration onto the plot."""
        return self._draw_from_history(self.history_iter > 0, -1, **kwargs)

    def _draw_iteration(self, target: int, draw: bool = True, **kwargs) -> bool:
        """Redraws all changes until the `target` iteration. 
        
        Loops over :meth:`_draw_next` or :meth:`_draw_prev` until the `target` plot iteration is reached. Note that this means that all the changes from the current iteration until the target iteration in `self.history_dict` are applied. 

        Parameters
        ----------
        target : int
            Target plot iteration. 
        draw : bool, optional
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
        '''Adds a new artist to the ``axis``. 

        Newly added artists must be hidden in the previous iteration. To make sure the history is properly logged, the visibility of the ``artist`` is set to ``False``, and a new property of shown visibility is added to the queue of the next iteration.

        Parameters
        ----------
        artist : `matplotlib.artist.Artist`
            New plot artist to add to the ``axis``.
        axis : `matplotlib.axes.Axes`, optional
            Axis to add the figure to.
        '''
        if axis is None:
            axis = self.main_ax
        axis.add_artist(artist)
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
        artist : `matplotlib.artist.Artist`
            Plot object whose properties are changed.
        properties : dict
            Plot properties to change.
        saved_properties : dict
            Override current properties and parse previous and current history. 
        """
        def get_nested(value):
            if type(value) == list and type(value[0]) == list:
                return get_nested(value[0])
            else:
                return value

        def get_nested_property(prop):
            if type(prop) == numpy.ndarray:
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
            current_value = get_nested_property(plt.getp(artist, key))
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
        artist : `matplotlib.artist.Artist`
            Plot object whose properties are changed.
        properties : dict
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


class Template3D(Template2D):
    """Template 2D plot object with history navigation."""
    pass