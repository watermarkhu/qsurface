from ...codes.elements import AncillaQubit, DataQubit, Edge
from ...plot import Template2D, Template3D
from .._template import Plot
from .sim import Toric as SimToric, Planar as SimPlanar
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D


class Toric(SimToric, Plot):
    """Union-Find decoder for the toric lattice with union-find plot.

    Has all class attributes and methods from `.unionfind.sim.Toric`, with additional parameters below. Default values for these parameters can be supplied via a *decoders.ini* file under the section of ``[unionfind]`` (see `.decoders._template.read_config`).

    The plotting class initiates a `qsurface.plot` object. For its usage, see :ref:`plot-usage`.

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

    def decode(self, *args, **kwargs):
        # Inherited docstring
        params = self.code.figure.params if hasattr(self.code, "figure") else None
        if self.code.__class__.__name__ == "PerfectMeasurements":
            self.figure = self.Figure2D(self, self.name, plot_params=params, **kwargs)
        elif self.code.__class__.__name__ == "FaultyMeasurements":
            self.figure = self.Figure3D(self, self.name, plot_params=params, **kwargs)
        super().decode(*args, **kwargs)
        # self.figure.draw_figure("Press (->/enter) to close decoder figure.")
        self.figure.close()

    def find_clusters(self, **kwargs):
        # Inherited docstring
        ret = super().find_clusters(**kwargs)
        self.figure.draw_figure("Clusters found.")
        return ret

    def grow_clusters(self, *args, **kwargs):
        # Inherited docstring
        ret = super().grow_clusters(*args, **kwargs)
        self.figure.draw_figure("Clusters grown.")
        return ret

    def grow_bucket(self, bucket, bucket_i, **kwargs):
        ret = super().grow_bucket(bucket, bucket_i, **kwargs)
        if self.config["step_bucket"] and self.config["step_cycle"]:
            self.figure.draw_figure(f"Bucket {bucket_i} grown.")
        return ret

    def grow_boundary(self, cluster, union_list, **kwargs):
        # Inherited docstring
        draw = True if self.config["step_cluster"] and cluster.new_bound else False
        ret = super().grow_boundary(cluster, union_list, **kwargs)
        if draw:
            self.figure.draw_figure(f"Cluster {cluster} grown.")
        return ret

    def place_bucket(self, place_list, bucket_i, **kwargs):
        # Inherited docstring
        ret = super().place_bucket(place_list, bucket_i, **kwargs)
        if self.config["step_bucket"] and not self.config["step_cycle"] and bucket_i != -1:
            self.figure.draw_figure(f"Bucket {bucket_i} grown.")
        return ret

    def peel_clusters(self, *args, **kwargs):
        # Inherited docstring
        ret = super().peel_clusters(*args, **kwargs)
        self.figure.draw_figure("Clusters peeled.")
        return ret

    def flip_edge(self, ancilla, edge, new_ancilla, **kwargs):
        # Inherited docstring
        ret = super().flip_edge(ancilla, edge, new_ancilla, **kwargs)
        self.figure._match_edge(edge)
        self.figure._flip_ancilla(ancilla)
        self.figure._flip_ancilla(new_ancilla)
        if self.config["step_peel"]:
            self.figure.draw_figure(f"Edge {edge} to matching.")
        return ret

    def cluster_add_ancilla(self, cluster, ancilla, **kwargs):
        # Inherited docstring
        if ancilla.syndrome:
            self.figure._plot_ancilla(ancilla, init=True)
        return super().cluster_add_ancilla(cluster, ancilla, **kwargs)

    def _edge_full(self, ancilla, edge, new_ancilla, **kwargs):
        # Inherited docstring
        self.support[edge] = 2
        if hasattr(edge, "uf_plot_instance") and edge.uf_plot_instance == self.code.instance:
            if ancilla in edge.uf_plot and edge.uf_plot[ancilla].instance == self.code.instance:
                self.figure._plot_half_edge(edge, new_ancilla, self.code.instance, full=True)
                self.figure._plot_full_edge(edge, ancilla)
            else:
                self.figure._plot_half_edge(edge, ancilla, self.code.instance, full=True)
                self.figure._plot_full_edge(edge, new_ancilla)
        else:
            self.figure._plot_half_edge(edge, ancilla, self.code.instance, full=True)
            self.figure._plot_half_edge(edge, new_ancilla, self.code.instance, full=True)

    def _edge_grow(self, ancilla, edge, new_ancilla, **kwargs):
        # Inherited docsting
        if self.support[edge] == 1:
            self._edge_full(ancilla, edge, new_ancilla, **kwargs)
        else:
            self.support[edge] += 1
            self.figure._plot_half_edge(edge, ancilla, self.code.instance)

    def _edge_peel(self, edge, variant="", **kwargs):
        # Inherited docstingS
        ret = super()._edge_peel(edge, variant=variant, **kwargs)
        self.figure._hide_edge(edge)
        if variant == "peel" and self.config["step_peel"]:
            self.figure.draw_figure(f"Edge {edge} removed by peel.")
        elif variant == "cycle" and self.config["step_cycle"]:
            self.figure.draw_figure(f"Edge {edge} removed by cycle.")
        return ret

    class Figure2D(Template2D):
        """Visualizer for the Union-Find decoder and Union-Find based decoders with perfect measurements.

        Parameters
        ----------
        args, kwargs
            Positional and keyword arguments are forwarded to `.plot.Template2D`.
        """

        def __init__(self, decoder, name, *args, **kwargs) -> None:
            self.decoder = decoder
            self.code = decoder.code
            self.decoder = name
            super().__init__(*args, **kwargs)
            self.colors1 = {"x": self.params.color_x_primary, "z": self.params.color_z_primary}
            self.colors2 = {"x": self.params.color_x_secondary, "z": self.params.color_z_secondary}

            size = [xy + 0.25 for xy in self.code.size]
            self._init_axis([-0.25, -0.25] + size, title=self.decoder, aspect="equal")

            handles = [
                self._legend_scatter(
                    "Syndrome vertex",
                    facecolors=self.params.color_x_secondary,
                    edgecolors=self.params.color_x_primary,
                    marker="s",
                ),
                self._legend_scatter(
                    "Syndrome star",
                    facecolors=self.params.color_z_secondary,
                    edgecolors=self.params.color_z_primary,
                    marker="D",
                ),
                self._legend_circle(
                    "Half edge",
                    ls=self.params.line_style_tertiary,
                    color=self.params.color_edge,
                ),
                self._legend_circle(
                    "Full edge",
                    ls=self.params.line_style_primary,
                    color=self.params.color_edge,
                ),
                self._legend_circle(
                    "X matching",
                    ls=self.params.line_style_primary,
                    color=self.params.color_x_primary,
                ),
                self._legend_circle(
                    "Z matching",
                    ls=self.params.line_style_primary,
                    color=self.params.color_z_primary,
                ),
            ]
            labels = [artist.get_label() if hasattr(artist, "get_label") else artist[0].get_label() for artist in handles]
            self.legend_ax.legend(handles, labels, **kwargs.pop("uf_legend_kwargs", {}))

        def _plot_half_edge(
            self,
            edge: Edge,
            ancilla: AncillaQubit,
            instance: float,
            full: bool = False,
        ):
            """Adds a line corresponding to a half-edge to the figure."""
            line = self._draw_line(
                self.code._parse_boundary_coordinates(self.code.size[0], edge.qubit.loc[0], ancilla.loc[0]),
                self.code._parse_boundary_coordinates(self.code.size[0], edge.qubit.loc[1], ancilla.loc[1]),
                ls=self.params.line_style_primary if full else self.params.line_style_tertiary,
                zorder=0,
                lw=self.params.line_width_primary,
                color=self.colors2[ancilla.state_type],
            )
            line.object = edge
            line.instance = instance
            if hasattr(edge, "uf_plot"):
                edge.uf_plot[ancilla] = line
            else:
                edge.uf_plot = {ancilla: line}
                edge.uf_plot_instance = instance

            self.new_artist(line)

        def _plot_full_edge(self, edge: Edge, ancilla: AncillaQubit):
            """Updates the line styles of the plot of an edge with support 2."""
            self.new_properties(edge.uf_plot[ancilla], {"ls": self.params.line_style_primary})

        def _hide_edge(self, edge: Edge):
            """Hides the plot of an edge after a peel or detected cycle."""
            if hasattr(edge, "uf_plot"):
                for artist in edge.uf_plot.values():
                    self.new_properties(artist, {"visible": False})

        def _match_edge(self, edge: Edge):
            """Updates the color of an matched edge."""
            for artist in edge.uf_plot.values():
                self.new_properties(artist, {"color": self.colors1[edge.state_type]})

        def _plot_ancilla(self, ancilla: AncillaQubit, init: bool = False):
            """Adds a syndrome to the plot."""

            rotations = {"x": 0, "z": 45}

            loc_parse = {
                "x": lambda x, y: (
                    x - self.params.patch_rectangle_2d / 2,
                    y - self.params.patch_rectangle_2d / 2,
                ),
                "z": lambda x, y: (x, y - self.params.patch_rectangle_2d * 2 ** (1 / 2) / 2),
            }
            # Plot ancilla object
            ancilla.uf_plot = self._draw_rectangle(
                loc_parse[ancilla.state_type](*ancilla.loc),
                self.params.patch_rectangle_2d,
                self.params.patch_rectangle_2d,
                rotations[ancilla.state_type],
                edgecolor=self.colors1[ancilla.state_type],
                facecolor=self.colors2[ancilla.state_type],
                linewidth=self.params.line_width_primary,
                picker=self.params.blocking_pick_radius,
                zorder=1,
                z=ancilla.z,
            )
            ancilla.uf_plot.object = ancilla
            if not init:
                self.new_artist(ancilla.uf_plot)

        def _flip_ancilla(self, ancilla: AncillaQubit):
            """Flips the state of the ancilla on the figure."""
            if ancilla.syndrome:
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
                if hasattr(ancilla, "uf_plot"):
                    self.new_properties(ancilla.uf_plot, {"visible": False})

        def _pick_handler(self, event):
            """Function on when an object in the figure is picked"""
            obj = event.artist.object
            if type(obj) == Edge:
                print(f"{obj}L{self.decoder.support[obj]}")
            elif type(obj) == AncillaQubit:
                print(f"{obj}-{obj.cluster.find()}")
            elif type(obj) == DataQubit:
                print(obj)

    class Figure3D(Template3D, Figure2D):
        """Visualizer for the Union-Find decoder and Union-Find based decoders with faulty measurements.

        Parameters
        ----------
        args, kwargs
            Positional and keyword arguments are forwarded to `~.decoders.unionfind.plot.Toric.Figure2D` and `.plot.Template3D`.
        """

        def _plot_half_edge(
            self,
            edge: Edge,
            ancilla: AncillaQubit,
            instance: float,
            full: bool = False,
        ):
            """Adds a line corresponding to a half-edge to the figure."""

            if type(edge.qubit) is DataQubit:
                edge_z = edge.qubit.z
            else:
                edge_z = edge.qubit.z - 0.5
                if abs(edge_z - ancilla.z) > 1:
                    edge_z = self.code.layers - edge.z

            line = self._draw_line3D(
                self.code._parse_boundary_coordinates(self.code.size[0], edge.qubit.loc[0], ancilla.loc[0]),
                self.code._parse_boundary_coordinates(self.code.size[0], edge.qubit.loc[1], ancilla.loc[1]),
                (edge_z, ancilla.z),
                ls=self.params.line_style_primary if full else self.params.line_style_tertiary,
                zorder=0,
                lw=self.params.line_width_primary,
                color=self.colors2[ancilla.state_type],
            )
            line.object = edge
            line.instance = instance
            if hasattr(edge, "uf_plot"):
                edge.uf_plot[ancilla] = line
            else:
                edge.uf_plot = {ancilla: line}
                edge.uf_plot_instance = instance

            self.new_artist(line)


class Planar(Toric, SimPlanar):
    """Union-Find decoder for the planar lattice with union-find plot.

    Has all class attributes and methods from `.unionfind.sim.Planar`, with additional parameters below. Default values for these parameters can be supplied via a *decoders.ini* file under the section of ``[unionfind]`` (see `.decoders._template.read_config`).

    The plotting class initiates a `qsurface.plot` object. For its usage, see :ref:`plot-usage`.

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
    kwargs
        Keyword arguments are passed on to `.unionfind.sim.Planar`.
    """

    def init_plot(self, **kwargs):
        # Inherited docstring
        size = [xy - 0.5 for xy in self.code.size]
        self._init_axis([-0.25, -0.25] + size, title=self.decoder, aspect="equal")

    class Figure2D(Toric.Figure2D):
        """Visualizer for the Union-Find decoder and Union-Find based decoders with perfect measurements.

        Parameters
        ----------
        args, kwargs
            Positional and keyword arguments are forwarded to `.unionfind.plot.Toric.Figure2D`.
        """

        def _plot_ancilla(self, ancilla, **kwargs):
            if type(ancilla) == AncillaQubit:
                super()._plot_ancilla(ancilla, **kwargs)
