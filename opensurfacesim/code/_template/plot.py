from abc import abstractmethod
from typing import List, Tuple, Union
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from ...plot._template import Template2D
from .sim import PerfectMeasurements as TemplateSimPM, FaultyMeasurements as TemplateSimFM


numtype = Union[str, float]
loctype = Tuple[numtype, numtype]


class PerfectMeasurements(TemplateSimPM):
    def __init__(self, *args, **kwargs) -> None:
        self.figures = {}
        self.figures_destroyed = {}
        super().__init__(*args, **kwargs)

    def init_figures(self, **kwargs) -> None:
        for figure in self.figures.values():
            figure.init_figure(**kwargs)


class CodePlot2D(Template2D):
    def __init__(self, code: PerfectMeasurements, *args, **kwargs) -> None:
        self.code = code
        self.main_boundary = None
        self.legend_loc = (1, 1)
        super().__init__(*args, **kwargs)

    def init_legend(self, legend_loc: Tuple[numtype, numtype], items: List[Line2D] = [], **kwargs):
        """
        Initilizes the legend of the plot.
        The qubits, errors and stabilizers are added.
        Aditional legend items can be inputted through the items paramter
        """

        le_qubit = self._legend_circle("Qubit", mfc=self.color_qubit_face, mec=self.color_qubit_edge)
        le_ver = self._legend_circle(
            "Vertex",
            ls="-",
            lw=self.line_width_primary,
            color=self.color_x_secundary,
            mfc=self.color_x_secundary,
            mec=self.color_x_secundary,
            marker="|",
        )
        le_pla = self._legend_circle(
            "Plaquette",
            ls="--",
            lw=self.line_width_primary,
            color=self.color_z_secundary,
            mfc=self.color_z_secundary,
            mec=self.color_z_secundary,
            marker="|",
        )

        self.lh = [le_qubit, le_ver, le_pla]
        for error in self.code.errors.values():
            for name, attributes in error.legend_attributes.items():
                for key, attribute in attributes.items():
                    if type(attribute) == str:
                        if attribute[0] == "~":
                            attributes[key] = attribute[1:]
                        else:
                            attributes[key] = getattr(self, attribute)
                self.lh.append(self._legend_circle(name, **attributes))
        self.lh += items

        self.main_ax.legend(handles=self.lh, bbox_to_anchor=legend_loc, **kwargs)

    def init_figure(self, z=0, **kwargs):

        title = "{} lattice".format(str(self.code.__class__.__module__).split(".")[-2])
        self.init_axis(self.main_boundary, title=title)
        self.init_legend(self.legend_loc, loc="upper right", ncol=1)

        for item in self.code.data_qubits[z].values():
            self.plot_data(item)
        for item in self.code.ancilla_qubits[z].values():
            self.plot_ancilla(item)
        if self.code.pseudo_qubits:
            for item in self.code.pseudo_qubits[z].values():
                self.plot_ancilla(item)

        self.draw_figure()

    @abstractmethod
    def parse_line_locs(self):
        pass

    def plot_ancilla(self, item):
        linestyles = {"x": self.line_style_primary, "z": self.line_style_secundary}
        item.surface_plot = {}
        for key, data in item.parity_qubits.items():
            line = Line2D(
                *self.parse_line_locs(item.loc, data.loc),
                color=self.color_edge,
                lw=self.line_width_primary,
                ls=linestyles[item.ancilla_type],
                zorder=0
            )
            item.surface_plot[key] = line
            self.main_ax.add_artist(line)
            line.object = item

    def plot_data(self, item):
        item.surface_plot = plt.Circle(
            item.loc,
            self.scatter_size_2d,
            edgecolor=self.color_qubit_edge,
            facecolor=self.color_qubit_face,
            lw=self.line_width_primary,
            picker=self.interact_pick_radius,
            zorder=1,
        )
        self.main_ax.add_artist(item.surface_plot)
        item.surface_plot.object = item
