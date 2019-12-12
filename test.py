import run_toric_2D_uf as rt2
import time


t0 = time.time()
size = 16
pX = 0.09
pZ = 0.0
pE = 0.0
iters = 20000

plot_load = 0
# output = rt2.single(size, pE, pX, pZ, plot_load=plot_load)
# output = rt2.multiple(size, iters, pE, pX, pZ, plot_load=plot_load)
output = rt2.multiprocess(size, iters, pE, pX, pZ)

print("time taken =", time.time() - t0)
print("p = " + str(output / iters * 100) + "%")

# from cposguf_run import multiprocess
# from cposguf_plotcompare import plot_both
# import graph_objects as go
# from progiter import ProgIter as pi
#
# l, p, num = 44, 0.09, 10000
#
# results = multiprocess(num, l, p)
#
# tree_wins, list_wins, treeval, listval = [], [], 0, 0
# for trees, lists, seed in results:
#     treeval += trees
#     listval += lists
#     if trees and not lists: tree_wins.append(int(seed))
#     if lists and not trees: list_wins.append(int(seed))
#
# print(treeval/num, listval/num, len(tree_wins), len(list_wins))

# graph0 = go.init_toric_graph(l)
# graph1 = go.init_toric_graph(l)

# for seed in tree_wins:
#     plot_both(graph0, graph1, seed, p)
