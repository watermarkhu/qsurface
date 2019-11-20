# import run_toric_2D_uf as rt2u
# import time
#
#
# t0 = time.time()
# size = 20
# pX = 0.09
# pZ = 0.0
# pE = 0.0
# iters = 5000
#
# plot_load = 1
# save_file = 0
# filename = None
# pauli_file = filename + "_pauli" if filename is not None else None
# erasure_file = filename + "_erasure" if filename is not None else None
# # pauli_file, erasure_file = "pauli", "erasure"
#
# # output = rt2u.single(
# #     size, pE, pX, pZ, save_file, erasure_file, pauli_file, plot_load
# # )
# # output = rt2u.multiple(size, iters, pE, pX, pZ, plot_load=plot_load)
# output = rt2u.multiprocess(size, iters, pE, pX, pZ, 4)
#
# print("time taken =", time.time() - t0)
# print("p = " + str(output / iters * 100) + "%")

from cposguf_run import multiprocess
from cposguf_plotcompare import plot_both
import graph_objects as go
from progiter import ProgIter as pi

l, p, num = 44, 0.09, 10000

results = multiprocess(num, l, p)

tree_wins, list_wins, treeval, listval = [], [], 0, 0
for trees, lists, seed in results:
    treeval += trees
    listval += lists
    if trees and not lists: tree_wins.append(int(seed))
    if lists and not trees: list_wins.append(int(seed))

print(treeval/num, listval/num, len(tree_wins), len(list_wins))



# graph0 = go.init_toric_graph(l)
# graph1 = go.init_toric_graph(l)

# for seed in tree_wins:
#     plot_both(graph0, graph1, seed, p)
