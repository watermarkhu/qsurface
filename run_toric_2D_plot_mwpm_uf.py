import graph_objects as go
import toric_code as tc
import toric_error as te
import toric_plot as tp
import uf_plot as up
import unionfind as uf


size = 8
pX = 0.1
pZ = 0.0
pE = 0.0




# seeds = []
#
# for i in range(100):
#     graph = go.init_toric_graph(size)
#
#     seed = te.init_random_seed()
#     te.init_pauli(graph, pX, pZ)
#     tc.measure_stab(graph)
#     matching = tc.get_matching_mwpm(graph)
#     tc.apply_matching_mwpm(graph, matching)
#     le1 = tc.logical_error(graph)
#
#     graph.reset()
#     te.apply_random_seed(seed)
#     te.init_pauli(graph, pX, pZ)
#     tc.measure_stab(graph)
#     ufg = uf.cluster_farmer(
#         graph,
#         plot_growth=0,
#         print_steps=0,
#         random_traverse=0,
#         intervention=0,
#         vcomb=0
#     )
#     ufg.find_clusters()
#     ufg.grow_clusters()
#     ufg.peel_clusters()
#     le2 = tc.logical_error(graph)
#
#     if le1 != le2:
#         seeds.append(seed)
#
#
# print(seeds)
outcome = ["complex","dg", "never", "nondg"]

seeds = ['1576086445105950800', '1576086445117989400', '1576086445170354400', '1576086445229467800', '1576086445253968800', '1576086445259885800', '1576086445269608200', '1576086445337262800', '1576086445356102800', '1576086445386285800', '1576086445394128800', '1576086445399560000', '1576086445415314000', '1576086445445901600', '1576086445449795400', '1576086445482731200', '1576086445495251200', '1576086445510983800', '1576086445539117400', '1576086445566503800', '1576086445579458800', '1576086445613256200', '1576086445653322000', '1576086445656154200', '1576086445671882000', '1576086445678052400', '1576086445687139200', '1576086445693976400']



def countmatching(graph):
    count = 0
    for edge in graph.E.values():
        if edge.matching:
            count += 1
    return count


seed = seeds[10]
graph0 = go.init_toric_graph(size)
toric_plot = tp.lattice_plot(graph0, plot_size=6, line_width=2)

te.apply_random_seed(seed)
te.init_pauli(graph0, pX, pZ, toric_plot=toric_plot)
tc.measure_stab(graph0, toric_plot)
matching = tc.get_matching_mwpm(graph0)
tc.apply_matching_mwpm(graph0, matching, toric_plot)
result0 = tc.logical_error(graph0)
count0 = countmatching(graph0)
print(result0)


graph = go.init_toric_graph(size)
toric_plot = tp.lattice_plot(graph, plot_size=6, line_width=2)
te.apply_random_seed(seed)
te.init_pauli(graph, pX, pZ, toric_plot=toric_plot)
tc.measure_stab(graph, toric_plot)
uf_plot = up.toric(graph, toric_plot.f, plot_size=6, line_width=1.5, plotstep_click=1)

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
print(result)

toric_plot.plot_final()

row = "{},{},{}, {:d}{:d}, {:d}{:d}, {}, {};".format(size, pX, seed, result0[0], result0[1], result[0], result[1], count0, count)
with open('document.csv','a') as fd:
    fd.write(row)


# Measure logical operator
# logical_error = tc.logical_error(graph)
