import graph_objects as go
import toric_code as tc
import toric_error as te
import toric_plot as tp
import uf_plot as up
import unionfind_dgvertices as uf


size = 16
pX = 0.09
pZ = 0.0
pE = 0.0


def countmatching(graph):
    count = 0
    for edge in graph.E.values():
        if edge.matching:
            count += 1
    return count


seed = '1576237986127575800'
graph0 = go.init_toric_graph(size)
toric_plot = tp.lattice_plot(graph0, plot_size=6, line_width=1)

te.apply_random_seed(seed)
te.init_pauli(graph0, pX, pZ, toric_plot=toric_plot)
tc.measure_stab(graph0, toric_plot)
matching = tc.get_matching_mwpm(graph0)
tc.apply_matching_mwpm(graph0, matching, toric_plot)
result0 = tc.logical_error(graph0)
count0 = countmatching(graph0)


graph = go.init_toric_graph(size)
toric_plot = tp.lattice_plot(graph, plot_size=6, line_width=1)
te.apply_random_seed(seed)
te.init_pauli(graph, pX, pZ, toric_plot=toric_plot)
tc.measure_stab(graph, toric_plot)
uf_plot = up.toric(graph, toric_plot.f, plot_size=6, line_width=1, plotstep_click=1)

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
result = tc.logical_error(graph)
count = countmatching(graph)

print("mwpm", result0, count0)
print("unfi", result, count)

toric_plot.plot_final()

# row = "{},{},{}, {:d}{:d}, {:d}{:d}, {}, {};".format(size, pX, seed, result0[0], result0[1], result[0], result[1], count0, count)
# with open('document.csv','a') as fd:
#     fd.write(row)


# Measure logical operator
# logical_error = tc.logical_error(graph)
