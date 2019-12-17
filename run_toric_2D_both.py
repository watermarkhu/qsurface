import graph_objects as go
import toric_code as tc
import toric_error as te
import toric_plot as tp
import uf_plot as up
import unionfind_dgvertices as uf


size = 20
pX = 0.09
pZ = 0.0
pE = 0.0

def countmatching(graph):
    count = 0
    for edge in graph.E.values():
        if edge.matching:
            count += 1
    return count

graph0 = go.init_toric_graph(size)
graph = go.init_toric_graph(size)

counter = 0
total = 0
while counter < 100:

    print(total)
    total += 1

    seed = te.init_random_seed()

    te.apply_random_seed(seed)
    te.init_pauli(graph0, pX, pZ)
    tc.measure_stab(graph0)
    matching = tc.get_matching_mwpm(graph0)
    tc.apply_matching_mwpm(graph0, matching)
    result0 = tc.logical_error(graph0)
    count0 = countmatching(graph0)


    te.apply_random_seed(seed)
    te.init_pauli(graph, pX, pZ)
    tc.measure_stab(graph)

    ufg = uf.cluster_farmer(
        graph,
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

    graph0.reset()
    graph.reset()

    if result0 != result:
        print("got! ", counter)

        counter += 1

        row = "{},{},{}, {:d}{:d}, {:d}{:d}, {}, {}\n".format(size, pX, seed, result0[0], result0[1], result[0], result[1], count0, count)
        with open('16.csv','a') as fd:
            fd.write(row)


# Measure logical operator
# logical_error = tc.logical_error(graph)
