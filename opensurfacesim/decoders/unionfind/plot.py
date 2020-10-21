from opensurfacesim.codes.elements import AncillaQubit
from ...plot import Template2D, Template3D
from .._template import PlotCode
from .sim import Toric as SimToric, Planar as SimPlanar
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D
import sys


class Toric(SimToric, PlotCode):
    """Union-Find decoder for the toric lattice with union-find plot. 

    Has all class attributes and methods from `.unionfind.sim.Toric`, with additional parameters below. Default values for these parameters can be supplied via a *decoders.ini* file under the section of ``[unionfind]``.

    The plotting class initiates a `opensurfacesim.plot` object. For its usage, see :ref:`plot-usage`. 

    Parameters
    ----------
    step_bucket : bool, optional
        Waits for user after every occupied bucket. Default is false.
    step_cluster : bool, optional
        Waits for user after growth of every cluster. Default is false.
    step_cycle : bool, optional
        Waits for user after every edge removed due to cycle detection. Default is false.
    step_peel : bool, optional
        Waits for user after every edge removed during peeling. Default is false.
    """

    opposite_keys = dict(n="s", s="n", e="w", w="e")

    def _draw(self, text: str = "", returns: int = 1):
        if self.config["print_steps"]:
            self.figure.draw_figure(text, carriage_return=returns)
        else:
            self.figure.draw_figure(text)

    def decode(self, *args, **kwargs):
        # Inherited docstring
        if self.code.__class__.__name__ == "PerfectMeasurements":
            self.figure = self.Figure2D(self.code, self.name, **kwargs)
        elif self.code.__class__.__name__ == "FaultyMeasurements":
            self.figure = self.Figure3D(self.code, self.name, **kwargs)
        super().decode(*args, **kwargs)
        self._draw("Press (->/enter) to close decoder figure.")
        self.figure.close()

    def find_clusters(self, **kwargs):
        # Inherited docstring
        ret = super().find_clusters(**kwargs)
        self.figure.draw_figure()
        return ret

    def grow_clusters(self, *args, **kwargs):
        # Inherited docstring
        ret = super().grow_clusters(*args, **kwargs)
        self._draw("Clusters grown.")
        return ret

    def _grow_bucket(self, bucket, bucket_i, **kwargs):
        ret = super()._grow_bucket(bucket, bucket_i, **kwargs)
        if self.config["step_bucket"] and self.config["step_cycle"]:
            self._draw(f"Bucket {bucket_i} grown.")
        return ret

    def _grow_boundary(self, cluster, union_list, **kwargs):
        # Inherited docstring
        draw = True if self.config["step_cluster"] and cluster.new_bound else False
        ret = super()._grow_boundary(cluster, union_list, **kwargs)
        if draw:
            self._draw(f"Cluster {cluster} grown.")
        return ret

    def _place_bucket(self, place_list, bucket_i, **kwargs):
        # Inherited docstring
        ret = super()._place_bucket(place_list, bucket_i, **kwargs)
        if self.config["step_bucket"] and not self.config["step_cycle"]:
            self._draw(f"Bucket {bucket_i} grown.")
        return ret

    def peel_clusters(self, *args, **kwargs):
        # Inherited docstring
        ret = super().peel_clusters(*args, **kwargs)
        self._draw("Clusters peeled.")
        return ret

    def _flip_edge(self, ancilla, edge, new_ancilla, **kwargs):
        # Inherited docstring
        ret = super()._flip_edge(ancilla, edge, new_ancilla, **kwargs)
        self.figure._match_edge(edge)
        self.figure._flip_ancilla(ancilla)
        self.figure._flip_ancilla(new_ancilla)
        if self.config["step_peel"]:
            self._draw(f"Edge {edge} to matching.")
        return ret

    def cluster_find_ancillas(self, cluster, ancilla, **kwargs):
        # Inherited docstring
        if ancilla.measured_state:
            self.figure._plot_ancilla(ancilla, init=True)
        return super().cluster_find_ancillas(cluster, ancilla, **kwargs)

    def _edge_full(self, ancilla, edge, new_ancilla, **kwargs):
        # Inherited docstring
        self.support[edge] = 2
        if len(edge.uf_plot) == 1:
            if ancilla in edge.uf_plot:
                self.figure._plot_half_edge(edge, new_ancilla, full=True)
                self.figure._plot_full_edge(edge, ancilla)
            else:
                self.figure._plot_half_edge(edge, ancilla, full=True)
                self.figure._plot_full_edge(edge, new_ancilla)

    def _edge_grow(self, ancilla, edge, new_ancilla, **kwargs):
        # Inherited docsting
        if self.support[edge] == 1:
            self._edge_full(ancilla, edge, new_ancilla, **kwargs)
        else:
            self.support[edge] += 1
            self.figure._plot_half_edge(edge, ancilla)

    def _edge_peel(self, edge, variant="", **kwargs):
        # Inherited docstingS
        ret = super()._edge_peel(edge, variant=variant, **kwargs)
        self.figure._hide_edge(edge)
        if variant == "peel" and self.config["step_peel"]:
            self._draw(f"Edge {edge} removed by peel.")
        elif variant == "cycle" and self.config["step_cycle"]:
            self._draw(f"Edge {edge} removed by cycle.")
        return ret

    class Figure2D(Template2D):
        def __init__(self, code, name, *args, **kwargs) -> None:
            self.code = code
            self.decoder = name
            super().__init__(*args, **kwargs)
            self.colors1 = {"x": self.rc["color_x_primary"], "z": self.rc["color_z_primary"]}
            self.colors2 = {"x": self.rc["color_x_secondary"], "z": self.rc["color_z_secondary"]}

        def init_plot(self, **kwargs):
            # Inherited docstring
            size = [xy + 0.25 for xy in self.code.size]
            self._init_axis([-0.25, -0.25] + size, title=self.decoder)
            self.legend_ax.legend(
                handles=[
                    self._legend_circle(
                        "Vertex",
                        ls="-",
                        color=self.rc["color_x_secondary"],
                        mfc=self.rc["color_x_secondary"],
                        mec=self.rc["color_x_primary"],
                        marker="s",
                        ms=5,
                    ),
                    self._legend_circle(
                        "Star",
                        ls="-",
                        color=self.rc["color_z_secondary"],
                        mfc=self.rc["color_z_secondary"],
                        mec=self.rc["color_z_primary"],
                        marker="D",
                        ms=5,
                    ),
                    self._legend_circle(
                        "Half edge",
                        ls=self.rc["line_style_tertiary"],
                        color=self.rc["color_edge"],
                    ),
                    self._legend_circle(
                        "Full edge",
                        ls=self.rc["line_style_primary"],
                        color=self.rc["color_edge"],
                    ),
                    self._legend_circle(
                        "X matching",
                        ls=self.rc["line_style_primary"],
                        color=self.rc["color_x_primary"],
                    ),
                    self._legend_circle(
                        "Z matching",
                        ls=self.rc["line_style_primary"],
                        color=self.rc["color_z_primary"],
                    ),
                ]
            )

        def _plot_half_edge(self, edge, ancilla, full=False):
            line = Line2D(
                self.code._parse_boundary_coordinates(
                    self.code.size[0], edge.qubit.loc[0], ancilla.loc[0]
                ),
                self.code._parse_boundary_coordinates(
                    self.code.size[0], edge.qubit.loc[1], ancilla.loc[1]
                ),
                ls=self.rc["line_style_primary"] if full else self.rc["line_style_tertiary"],
                zorder=0,
                lw=self.rc["line_width_primary"],
                color=self.colors2[ancilla.state_type],
            )
            line.object = edge
            if hasattr(edge, "uf_plot"):
                edge.uf_plot[ancilla] = line
            else:
                edge.uf_plot = {ancilla: line}

            self.new_artist(line)

        def _plot_full_edge(self, edge, ancilla):
            self.new_properties(edge.uf_plot[ancilla], {"ls": self.rc["line_style_primary"]})

        def _hide_edge(self, edge):
            for artist in edge.uf_plot.values():
                self.new_properties(artist, {"visible": False})

        def _match_edge(self, edge):
            for artist in edge.uf_plot.values():
                self.new_properties(artist, {"color": self.colors1[edge.state_type]})

        def _plot_ancilla(self, ancilla, init=False):

            rotations = {"x": 0, "z": 45}

            loc_parse = {
                "x": lambda x, y: (
                    x - self.rc["patch_rectangle_2d"] / 2,
                    y - self.rc["patch_rectangle_2d"] / 2,
                ),
                "z": lambda x, y: (x, y - self.rc["patch_rectangle_2d"] * 2 ** (1 / 2) / 2),
            }
            # Plot ancilla object
            ancilla.uf_plot = Rectangle(
                loc_parse[ancilla.state_type](*ancilla.loc),
                self.rc["patch_rectangle_2d"],
                self.rc["patch_rectangle_2d"],
                rotations[ancilla.state_type],
                edgecolor=self.colors1[ancilla.state_type],
                facecolor=self.colors2[ancilla.state_type],
                picker=self.rc["interact_pick_radius"],
                zorder=1,
                lw=self.rc["line_width_primary"],
            )
            ancilla.uf_plot.object = ancilla
            if init:
                self.main_ax.add_artist(ancilla.uf_plot)
            else:
                self.new_artist(ancilla.uf_plot)

        def _flip_ancilla(self, ancilla):
            if ancilla.measured_state:
                if hasattr(ancilla, "uf_plot"):
                    self.new_properties(
                        ancilla.uf_plot,
                        {
                            "edgecolor": self.colors1[ancilla.state_type],
                            "facecolor": self.colors2[ancilla.state_type],
                        },
                    )
                else:
                    self._plot_ancilla(ancilla)
            else:
                self.new_properties(ancilla.uf_plot, {"visible": False})

    class Figure3D(Template3D, Figure2D):
        pass


class Planar(SimPlanar, Toric):
    """Union-Find decoder for the planar lattice with union-find plot. 

    Has all class attributes and methods from `.unionfind.sim.Planar`, with additional parameters below. Default values for these parameters can be supplied via a *decoders.ini* file under the section of ``[unionfind]``.

    The plotting class initiates a `opensurfacesim.plot` object. For its usage, see :ref:`plot-usage`. 

    Parameters
    ----------
    step_bucket : bool, optional
        Waits for user after every occupied bucket. Default is false.
    step_cluster : bool, optional
        Waits for user after growth of every cluster. Default is false.
    step_cycle : bool, optional
        Waits for user after every edge removed due to cycle detection. Default is false.
    step_peel : bool, optional
        Waits for user after every edge removed during peeling. Default is false.
    """
    def init_plot(self, **kwargs):
        size = [xy - 0.5 for xy in self.code.size]
        self._init_axis([-0.25, -0.25] + size, title=self.decoder)

    class Figure2D(Toric.Figure2D):
        def _plot_ancilla(self, ancilla, **kwargs):
            if type(ancilla) == AncillaQubit:
                super()._plot_ancilla(ancilla, **kwargs)