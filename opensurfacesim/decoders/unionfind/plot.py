from ...configuration import flatten_dict, get_attributes, init_config
from ...plot import Template2D, Template3D
from .._template import PlotCode
from .sim import Toric as SimToric
from pathlib import Path
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D


class Toric(SimToric, PlotCode):

    opposite_keys = dict(n="s", s="n", e="w", w="e")

    def do_decode(self, *args, **kwargs):
        if self.code.__class__.__name__ == "PerfectMeasurements":
            self.figure =  self.Figure2D(self.code, self.name, **kwargs)
        elif self.code.__class__.__name__ == "FaultyMeasurements":
            self.figure = self.Figure3D(self.code, self.name, **kwargs)
        super().do_decode(*args, **kwargs)
    

    def find_clusters(self, **kwargs):
        # Inherited docstring
        super().find_clusters(**kwargs)
        self.figure.draw_figure()

    def _cluster_find_vertices(self, cluster, vertex, **kwargs):
        # Inherited docstring
        if vertex.measured_state:
            self.figure._plot_vertex(vertex)
        super()._cluster_find_vertices(cluster, vertex, **kwargs)


    class Figure2D(Template2D):
        def __init__(self, code, name, *args, **kwargs) -> None:
            self.code = code
            self.decoder = name
            super().__init__(*args, **kwargs)
            self.rc.update(
                flatten_dict(
                    get_attributes(
                        self.rc,
                        init_config(
                            Path(__file__).resolve().parent / "plot_unionfind.ini"
                        )
                    )
                )
            )
        
        def init_plot(self, **kwargs):
            size = [xy + .25 for xy in self.code.size]
            self._init_axis([-.25, -.25] + size, title=self.decoder)

        def _plot_vertex(self, vertex):

            colors = {"x": self.rc["color_x_secondary"], "z": self.rc["color_z_secondary"]} 
            rotations = {"x": 0, "z": 45}

            loc_parse = {
                "x": lambda x, y: (x - self.rc["vertex_size_2d"] / 2, y - self.rc["vertex_size_2d"] / 2),
                "z": lambda x, y: (x, y - self.rc["vertex_size_2d"] * 2 ** (1 / 2) / 2),
            }
            # Plot ancilla object
            vertex.uf_plot = Rectangle(
                loc_parse[vertex.state_type](*vertex.loc),
                self.rc["vertex_size_2d"],
                self.rc["vertex_size_2d"],
                rotations[vertex.state_type],
                facecolor = colors[vertex.state_type],
                picker=self.rc["interact_pick_radius"],
                zorder=1,
                lw=self.rc["line_width_primary"],
            )
            self.main_ax.add_artist(vertex.uf_plot)

    class Figure3D(Template3D, Figure2D):
        pass