from .sim import Toric as ToricTemplate, Planar as PlanarTemplate
from .._template.plot import Code as PlotTemplate


class Toric(ToricTemplate, PlotTemplate):

    opposite_keys = dict(n="s", s="n", e="w", w="e")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.line_color_normal = {
            "x": dict(color = self.code.figure.color_edge),
            "z": dict(color = self.code.figure.color_edge)
        }
        self.line_color_match = {
            "x": dict(color = self.code.figure.color_x_secundary),
            "z": dict(color = self.code.figure.color_z_secundary)
        }

    def do_decode(self, *args, **kwargs):
        super().do_decode(*args, **kwargs)
        self.code.figure.draw_figure(new_iter_name="Matchings found")



    def walk_and_flip(self, flipnode, length, key):

        for _ in range(length):

            try: 
                (newnode, flipedge) = self.get_neighbor(flipnode, key)
            except:
                break
            flipedge.state = 1 - flipedge.state

            if hasattr(flipnode, "surface_lines"):
                self.plot_matching_edge(flipnode.surface_lines.get(key, None))
            if hasattr(newnode, "surface_lines"):
                self.plot_matching_edge(newnode.surface_lines.get(self.opposite_keys[key], None))
            flipnode = newnode

        return flipnode
    
    def plot_matching_edge(self, line):
        if line: 
            figure = self.code.figure
            next_iter = figure.history_iter + 2
            state_type = line.object.state_type
            figure.new_properties(line, self.line_color_match[state_type])
            figure.future_dict[next_iter][line] = self.line_color_normal[state_type]


class Planar(Toric, PlanarTemplate):
    pass