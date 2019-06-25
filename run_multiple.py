import toric_lat as tl
import planar_lat as pl
import sys

# sys.path.insert(0, '../fault_tolerance_simulations/')
# # sys.path.insert(0, '../Code_Eduardo/')
# #
# # import Eduardo
# import st

printval = 100


def toric_2D_MWPM(size, pX, pZ, iters, plot_load=False):

    N_succes = 0
    for i in range(iters):
        if i % printval == 0:
            print("Iteration " + str(i))
        if i == 0:
            TL = tl.lattice(size, None, None, plot_load)
        else:
            TL = tl.lattice(size, None, None, plot_load, graph=TL.G)

        TL.init_pauli_errors(pX, pZ, False)
        TL.measure_stab()
        TL.get_matching_MWPM()
        logical_error = TL.logical_error()
        TL.G.reset()
        if logical_error == [False, False, False, False]:
            N_succes += 1
    return N_succes


def toric_2D_peeling(size, pE, pX, pZ, iters, plot_load=False):


    N_succes = 0
    for i in range(iters):
        if i % printval == 0:
            print("Iteration " + str(i))
        if i == 0:
            TL = tl.lattice(size, None, None, plot_load)
        else:
            TL = tl.lattice(size, None, None, plot_load, graph=TL.G)

        TL.init_erasure_errors_region(pE, False)
        TL.init_pauli_errors(pX, pZ, False)
        TL.measure_stab()
        TL.get_matching_peeling()
        logical_error = TL.logical_error()
        TL.G.reset()
        if logical_error == [False, False, False, False]:
            N_succes += 1
    return N_succes


def planar_2D_MWPM(size, pX, pZ, iters, plot_load=False):

    N_succes = 0
    for i in range(iters):
        if i % printval == 0:
            print("Iteration " + str(i))
        if i == 0:
            PL = pl.lattice(size, None, None, plot_load)
        else:
            PL = pl.lattice(size, None, None, plot_load, graph=PL.G)

        PL.init_pauli_errors(pX, pZ, False)
        PL.measure_stab()
        PL.get_matching_MWPM()
        logical_error = PL.logical_error()
        PL.G.reset()
        if logical_error == [False, False]:
            N_succes += 1
    return N_succes

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
