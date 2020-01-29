import graph_objects as go
import dec_mwpm as dc
import toric_error2 as te
import surface_plot as tp
import uf_plot as up
import unionfind as uf



size = 10
pX = 0.1
pZ = 0.0
pE = 0.0


graph = go.init_toric_graph(size)
decoder = dc.toric(graph)

lplot = tp.lattice_plot(graph, plot_size=8, line_width=2)

seed = te.init_random_seed()
te.init_erasure(graph, pE)
lplot.plot_erasures()
te.init_pauli(graph, pX, pZ)
lplot.plot_errors()
graph.measure_stab()
lplot.plot_syndrome()
decoder.get_matching_blossom5()
if type == "planar":
    decoder.remove_virtual()
lplot.plot_lines(decoder.matching)


graph.reset()
toric_plot = tp.lattice_plot(graph, plot_size=8, line_width=2)
te.apply_random_seed(seed)
te.init_erasure(graph, pE)
te.init_pauli(graph, pX, pZ)
graph.measure_stab()
uf_plot = up.toric(graph, toric_plot.f, plot_size=8, line_width=1.5, plotstep_click=1)

ufg = uf.cluster_farmer(
    graph,
    uf_plot,
    plot_growth=0,
    print_steps=0,
    random_traverse=0,
    intervention=0,
    vcomb=0
)
ufg.find_clusters(plot_step=0)
ufg.grow_clusters()
ufg.peel_clusters(plot_step=0)

decoder.apply_matching()
lplot.plot_final()
