import toric_lat as tl
import sys
from tqdm import tqdm
from run_single import toric_2D_peeling
import multiprocessing as mp
import copy
# sys.path.insert(0, '../fault_tolerance_simulations/')
# # sys.path.insert(0, '../Code_Eduardo/')
# #
# # import Eduardo
# import st


# def toric_2D_MWPM(size, pX, pZ, iters, plot_load=False):
#
#     N_succes = 0
#     for i in range(iters):
#         if i % printval == 0:
#             print("Iteration " + str(i))
#         if i == 0:
#             TL = tl.lattice(size, None, None, plot_load)
#         else:
#             TL = tl.lattice(size, None, None, plot_load, graph=TL.G)
#
#         TL.init_pauli_errors(pX, pZ, False)
#         TL.measure_stab()
#         TL.get_matching_MWPM()
#         logical_error = TL.logical_error()
#         TL.G.reset()
#         if logical_error == [False, False, False, False]:
#             N_succes += 1
#     return N_succes


def m_toric_2D_peeling(size, pE, pX, pZ, iters, processes=1, plot_load=False):

    TL = tl.lattice(size)
    graphs = [TL.G]

    for i in range(processes):
        graphs.append(copy.deepcopy(graphs[0]))

    print(graphs)




    # pool = mp.Pool(processes=4)
    # results = [pool.apply_async(toric_2D_peeling, args=(size, pE, pX, pZ,)) for _ in tqdm(range(iters))]
    # output = [p.get() for p in results]
    # return sum(output)



    # N_succes = 0

    # for i in tqdm(range(iters)):
    #     if i == 0:
    #         TL = tl.lattice(size, None, None, plot_load)
    #     else:
    #         TL = tl.lattice(size, None, None, plot_load, graph=TL.G)
    #
    #     TL.init_erasure_errors_region(pE, False)
    #     TL.init_pauli_errors(pX, pZ, False)
    #     TL.measure_stab()
    #     TL.get_matching_peeling()
    #     logical_error = TL.logical_error()
    #     TL.G.reset()
    #     if logical_error == [False, False, False, False]:
    #         N_succes += 1
    # return N_succes


# def toric_2D_nickerson(size, pX, pZ, iters):
#
#     N_succes = 0
#     for i in range(iters):
#         if i % printval == 0:
#             print("Iteration " + str(i))
#         output = st.run2D(size, pX, pZ)
#         if output == [[1, 1], [1, 1]]:
#             N_succes += 1
#     return N_succes

#
# def toric_2D_eduardo(size, pX, pZ, iters):
#
#     N_succes = 0
#     for i in range(iters):
#         output = Eduardo.thres_calc("toric", size, pX, pZ, 0, 1, 1, 0)
#         if output == 0:
#             N_succes += 1
#     return N_succes
