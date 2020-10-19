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
        self.figure.draw_figure("Press (->/enter) to close decoder figure.")
        self.figure.close()
    

    def find_clusters(self, **kwargs):
        # Inherited docstring
        ret = super().find_clusters(**kwargs)
        self.figure.draw_figure()
        return ret

    def grow_clusters(self, *args, **kwargs):
        # Inherited docstring
        ret = super().grow_clusters(*args, **kwargs)
        self.figure.draw_figure("Clusters grown.")
        return ret

    def _grow_bucket(self, bucket, bucket_i, **kwargs):
        ret = super()._grow_bucket(bucket, bucket_i, **kwargs)
        if self.config["step_bucket"] and self.config["step_cycle"]:
            self.figure.draw_figure(f"Bucket {bucket_i} grown.")
        return ret

    def _grow_boundary(self, cluster, union_list, **kwargs):
        # Inherited docstring
        draw = True if self.config["step_cluster"] and cluster.new_bound else False
        ret = super()._grow_boundary(cluster, union_list, **kwargs)
        if draw:
            self.figure.draw_figure(f"Cluster {cluster} grown.")
        return ret

    def _place_bucket(self, place_list, bucket_i, **kwargs):
        # Inherited docstring
        ret = super()._place_bucket(place_list, bucket_i, **kwargs)
        if self.config["step_bucket"] and not self.config["step_cycle"]:
            self.figure.draw_figure(f"Bucket {bucket_i} grown.")
        return ret

    def peel_clusters(self, *args, **kwargs):
        # Inherited docstring
        ret = super().peel_clusters(*args, **kwargs)
        self.figure.draw_figure("Clusters peeled.")
        return ret
    
    def _flip_edge(self, vertex, edge, new_vertex, **kwargs):
        ret = super()._flip_edge(vertex, edge, new_vertex, **kwargs)
        self.figure._match_edge(edge)
        self.figure._flip_vertex(vertex)
        self.figure._flip_vertex(new_vertex)
        if self.config["step_peel"]:
            self.figure.draw_figure(f"Edge {edge} to matching.")
        return ret

    def _cluster_find_vertices(self, cluster, vertex, **kwargs):
        # Inherited docstring
        if vertex.measured_state:
            self.figure._plot_vertex(vertex, init=True)
        return super()._cluster_find_vertices(cluster, vertex, **kwargs)

    def _edge_full(self, vertex, edge, new_vertex, **kwargs):
        # Inherited docstring
        self.support[edge] = 2
        if len(edge.uf_plot) == 1:
            if vertex in edge.uf_plot:
                self.figure._plot_half_edge(edge, new_vertex, full=True)
                self.figure._plot_full_edge(edge, vertex)
            else:
                self.figure._plot_half_edge(edge, vertex, full=True)
                self.figure._plot_full_edge(edge, new_vertex)
        
    def _edge_grow(self, vertex, edge, new_vertex, **kwargs):
        # Inherited docsting
        if self.support[edge] == 1:
            self._edge_full(vertex, edge, new_vertex, **kwargs)
        else:
            self.support[edge] += 1
            self.figure._plot_half_edge(edge, vertex)
    
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
            self.colors1 = {"x": self.rc["color_x_primary"], "z": self.rc["color_z_primary"]} 
            self.colors2 = {"x": self.rc["color_x_secondary"], "z": self.rc["color_z_secondary"]}
        
        def init_plot(self, **kwargs):
            size = [xy + .25 for xy in self.code.size]
            self._init_axis([-.25, -.25] + size, title=self.decoder)

        def _plot_half_edge(self, edge, vertex, full=False):
            
            linestyle = self.rc["line_style_primary"] if full else self.rc["line_style_tertiary"]

            line = Line2D(
                self.code._parse_boundary_coordinates(self.code.size[0], edge.qubit.loc[0], vertex.loc[0]),
                self.code._parse_boundary_coordinates(self.code.size[0], edge.qubit.loc[1], vertex.loc[1]),
                ls=linestyle,
                zorder=0,
                lw=self.rc["line_width_primary"],
                color=self.colors2[vertex.state_type],
            )
            if hasattr(edge, "uf_plot"):
                edge.uf_plot[vertex] = line
            else:
                edge.uf_plot = {vertex: line} 
            self.main_ax.add_artist(line)
            self.history_dict[self.history_iter][line] = {"visible": False}
            self.history_dict[self.history_iter+1][line] = {"visible": True}
        
        def _plot_full_edge(self, edge, vertex):
            self.new_properties(edge.uf_plot[vertex], {"ls": self.rc["line_style_primary"]})


        def _hide_edge(self, edge):
            if hasattr(edge, "uf_plot"):
                for artist in edge.uf_plot.values():
                    self.new_properties(artist, {"visible": False})

        def _match_edge(self, edge):
            for artist in edge.uf_plot.values():
                self.new_properties(artist, {"color": self.colors1[edge.state_type]})

        def _plot_vertex(self, vertex, init=False):

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
                edgecolor = self.colors1[vertex.state_type],
                facecolor = self.colors2[vertex.state_type],
                picker=self.rc["interact_pick_radius"],
                zorder=1,
                lw=self.rc["line_width_primary"],
            )
            self.main_ax.add_artist(vertex.uf_plot)
            if not init:
                self.history_dict[self.history_iter][vertex.uf_plot] = {"visible": False}
                self.history_dict[self.history_iter+1][vertex.uf_plot] = {"visible": True}
        
        def _flip_vertex(self, vertex):
            if vertex.measured_state:
                if hasattr(vertex, "uf_plot"):
                    self.new_properties(
                        vertex.uf_plot,
                        {
                            "edgecolor": self.colors1[vertex.state_type],
                            "facecolor": self.colors2[vertex.state_type] 
                        }
                    )
                else:
                    self._plot_vertex(vertex)
            else:
                self.new_properties(vertex.uf_plot, {"visible": False})

    class Figure3D(Template3D, Figure2D):
        pass