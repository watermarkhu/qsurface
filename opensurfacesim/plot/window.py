from typing import Optional, Tuple, Union
import matplotlib
from ..configuration import flatten_dict, write_config, read_config
from collections import defaultdict as ddict
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
from matplotlib.blocking_input import BlockingInput
from abc import ABC, abstractmethod
import os
from numpy import ndarray



numtype = Union[int, float]
mpl.rcParams['toolbar'] = 'None'


class Template_2D(ABC):
    def __init__(self, **kwargs) -> None:

        config = flatten_dict(self.init_config())
        for key, value in config.items():
            setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.history_dict = ddict(dict)
        self.history_iters = 0
        self.history_iter = 0
        self.history_iter_names = ["Initial"]
        self.history_on_newest = 0
        self.history_event_iter = ""

    """
    -------------------------------------------------------------------------------
                                    Initialization
    -------------------------------------------------------------------------------
    """
    @abstractmethod
    def init_figure(self):
        pass

    @abstractmethod
    def init_legend(self):
        pass

    def init_config(self, write: bool = False, **kwargs):

        config_dict = read_config(os.path.dirname(os.path.abspath(__file__)) + "/plot.ini")
        config_path = "./plot.ini"
        if write:
            write_config(config_dict, config_path)
        if os.path.exists(config_path):
            read_config(config_path, config_dict)
        return config_dict

    def init_window(self) -> matplotlib.figure.Figure:
        self.figure = plt.figure(figsize=(self.scale_figure_length, self.scale_figure_height))
        self.canvas = self.figure.canvas
        self.canvas.mpl_connect("pick_event", self._pick_handler)
        self.blocking_input = BlockingInput(self.figure)
        # plt.ion()

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
        self.text = self.text_box.text(0.5, 0.5, "", fontsize=10, va="center", ha="center", transform=self.text_box.transAxes)
    
    def init_axis(self, limits: Tuple[numtype, numtype, numtype, numtype], ax: Optional[mpl.Axes] = None, invert:bool = True) -> None:
        if ax is None:
            ax = self.main_ax
        ax.axis(False)
        ax.set_xlim(limits[0], limits[0] + limits[2])
        ax.set_ylim(limits[1], limits[1] + limits[3])
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
        print(event)

    def _wait(self) -> None:

        wait = True
        while wait:
            event = self.blocking_input(self.mpl_wait)
            print(event)
            if event.key in ["enter", "right"]:
                if self.history_event_iter == "":
                    if self.history_on_newest:
                        wait = False
                    else:
                        self._draw_next()
                else:
                    target_iter = int(self.history_event_iter)
                    self.history_event_iter = ""
                    if target_iter <= self.iters:
                        self._draw_iteration(target_iter)
                    else:
                        print("Input iter not in range.")
            elif event.key in ["backspace", "left"]:
                self._draw_prev()
            elif event.key in [str(i) for i in range(10)]:
                self.history_event_iter += event.key
            elif event.key == "n":
                self._draw_iteration(self.iters)
            elif event.key == "i":
                for i, iter_name in enumerate(self.history_iter_names):
                    print(i, iter_name)
            elif event.key == "h":
                print("enter/right - next iteration\nbackspace/left - previous iteration\nn - go to newest iteration\ni - show iterations")

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
    def draw_figure(self, output:bool=True, **kwargs):
        text = self.iter_names[self.iter]
        self.text.set_text(text)
        if output:
            print("Drawing {}/{}: {}".format(self.iter, self.iters, text))
        self.canvas.blit(self.main_ax.bbox)
        self._wait(**kwargs)

    def new_iter(self, name: str = ""):
        """Initiates new plot iteration"""
        self.history_iter_names.append(name)
        self.history_iters += 1
        self.history_iter += 1

    def _draw_from_history(self, condition: bool, direction: int, output: bool = True, **kwargs) -> None:
        if condition:
            self.iter += direction
            for object, changes in self.history_dict[self.iter].items():
                self.change_attributes(object, changes)
            self.on_newest = True if self.iter == self.iters else False

    def _draw_next(self, draw: bool = True, **kwargs) -> None:
        """Redraws all changes from next plot iteration onto the plot"""
        self._draw_from_history(self.iter < self.iters, 1, **kwargs)
        if draw:
            self.draw_figure(**kwargs)

    def _draw_prev(self, draw: bool = True, **kwargs) -> None:
        """Redraws all changes from previous plot iteration onto the plot"""
        self._draw_from_history(self.iter > 0, -1, **kwargs)
        if draw:
            self.draw_figure(**kwargs)

    def _draw_iteration(self, target_iter: int, **kwargs) -> None:
        if target_iter == self.iter:
            print("Already on this plot iteration.")
        else:
            diff = target_iter - self.iter
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
        '''
        Get nested color and makes np.array, which is sometimes but not at all times used for color values, to a list.
        '''
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
        '''
        Finds the differences of the plot attributes between this iteration and the previous iterations. All differences are stored as dictionaries in the history variable.
        Makes sure that all changes are stored correctly and plot attributes are not overwritten if not explicitly defined.
        '''
        prev_changes = self.history_dict[self.iter - 1]
        next_changes = self.history_dict[self.iter]
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
        '''
        Redraws the attributes from the dictionary onto the plot object
        '''
        if attr_dict:
            plt.setp(object, **attr_dict)
        self.main_ax.draw_artist(object)
