import graph_objects as go
import toric_code as tc
import toric_error as te
import toric_plot as tp
import uf_plot as up
import unionfind as uf


size = 10
pX = 0.1
pZ = 0.0
pE = 0.0


graph = go.init_toric_graph(size)

seed = te.init_random_seed()
if pE != 0:
    te.init_erasure_region(graph, pE)
te.init_pauli(graph, pX, pZ)
tc.measure_stab(graph)
matching = tc.get_matching_mwpm(graph)


graph.reset()
toric_plot = tp.lattice_plot(graph, plot_size=8, line_width=2)
te.apply_random_seed(seed)
if pE != 0:
    te.init_erasure_region(graph, pE, toric_plot=toric_plot)
te.init_pauli(graph, pX, pZ, toric_plot=toric_plot)
tc.measure_stab(graph, toric_plot)
uf_plot = up.toric(graph, toric_plot.f, plot_size=8, line_width=1.5, plotstep_click=1)

toric_plot.plot_lines(matching)

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

if toric_plot:
    toric_plot.plot_final()

# Measure logical operator
logical_error = tc.logical_error(graph)
