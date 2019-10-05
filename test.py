# import run_toric_2D_uf as rt2u
# # import run_toric_2D_mwpm as rt2m
# import time

#
# if __name__ == '__main__':
#
#     t0 = time.time()
#     size = 14
#     pX = 0.25
#     pZ = 0.0
#     pE = 0.0
#     iters = 20000
#
#     plot_load = 1
#     save_file = 0
#     filename = None
#     pauli_file = filename + "_pauli" if filename is not None else None
#     erasure_file = filename + "_erasure" if filename is not None else None
#     # pauli_file, erasure_file = "pauli", "erasure"
#
#     output = rt2u.single(size, pE, pX, pZ, save_file, erasure_file, pauli_file, plot_load)
#     # output = rt2u.multiple(size, iters, pE, pX, pZ, plot_load=plot_load)
#     # output = rt2u.multiprocess(size, iters, pE, pX, pZ, 4)
#
#
#     print("time taken =", time.time()-t0)
#     print("p = " + str(output/iters*100) + "%")

import graph_objects as go
import toric_code as tc
import unionfind_tree as uft
import unionfind_list as ufl
import toric_error as te
import toric_plot as tp
import uf_plot as up
import random
from cposguf_analyze import get_grown_from_graph
import cposguf_cluster_actions as cca

L, p = 12, 0.11

ubuck_win, lubuck_win, vcomb_win, lvcomb_win , d, k = 1, 1, 1, 1, [], []
for i in range(5000):
    graph = go.init_toric_graph(L)

    seed = te.init_random_seed()
    te.init_pauli(graph, pX=p)           # Simulate for unique bucket method
    tc.measure_stab(graph)
    uft.find_clusters(graph)
    uft.grow_clusters(graph)
    uft.peel_clusters(graph)
    ugs, ups = get_grown_from_graph(graph)
    tc.apply_matching_peeling(graph)
    logical_error = tc.logical_error(graph)
    graph.reset()
    ubuck_win = True if logical_error == [False, False, False, False] else False


    random.seed(seed)
    te.init_pauli(graph, pX=p)
    tc.measure_stab(graph)
    uft.find_clusters(graph, vcomb=1)
    uft.grow_clusters(graph, vcomb=1)
    uft.peel_clusters(graph)
    vgs, lvps = get_grown_from_graph(graph)
    tc.apply_matching_peeling(graph)
    logical_error = tc.logical_error(graph)
    graph.reset()
    vcomb_win = True if logical_error == [False, False, False, False] else False


    random.seed(seed)
    te.init_pauli(graph, pX=p)           # Simulate for unique bucket method
    tc.measure_stab(graph)
    ufl.find_clusters(graph)
    ufl.grow_clusters(graph)
    ufl.peel_clusters(graph)
    lugs, lups = get_grown_from_graph(graph)
    tc.apply_matching_peeling(graph)
    logical_error = tc.logical_error(graph)
    graph.reset()
    lubuck_win = True if logical_error == [False, False, False, False] else False


    random.seed(seed)
    te.init_pauli(graph, pX=p)
    tc.measure_stab(graph)
    ufl.find_clusters(graph, vcomb=1)
    ufl.grow_clusters(graph, vcomb=1)
    ufl.peel_clusters(graph)
    lvgs, lvps = get_grown_from_graph(graph)
    tc.apply_matching_peeling(graph)
    logical_error = tc.logical_error(graph)
    graph.reset()
    lvcomb_win = True if logical_error == [False, False, False, False] else False

    d.append([len(ugs), len(vgs), len(lugs), len(lvgs)])
    k.append([ubuck_win, vcomb_win, lubuck_win, lvcomb_win])


[sum(a)/len(a) for a in list(map(list, zip(*d)))]
k.count([1,1,1,1]) + k.count([0,0,0,0])
k.count([0,0,1,1])
k.count([1,1,0,0])
cca.plot_cluster(ugs, L-1, L-1)
cca.plot_cluster(vgs, L-1, L-1)
cca.plot_cluster(lugs, L-1, L-1)
cca.plot_cluster(lvgs, L-1, L-1)
