import toric_lat as tl
import planar_lat as pl
import sys

# sys.path.insert(0, '../fault_tolerance_simulations/')
# # sys.path.insert(0, '../Code_Eduardo/')
# #
# # import Eduardo
# import st

printval = 100


def toric_2D_MWPM(size, pX, pZ, iters, savefile=False, time_stamp=None, load_plot=False):

    TL0 = tl.lattice(size, False)
    (edge_data, stab_data, log_data) = TL0.init_data()

    N_succes = 0
    for i in range(iters):
        if i % printval == 0:
            print("Iteration " + str(i))
        TL = tl.lattice(size, load_plot)
        TL.load_data(edge_data, stab_data, log_data)
        TL.init_plots()
        TL.init_pauli(pX, pZ, savefile, time_stamp)
        TL.measure_stab()
        TL.get_matching_MWPM()
        logical_error = TL.logical_error()
        if logical_error == [False, False, False, False]:
            N_succes += 1
    return N_succes


def toric_2D_peeling(size, pE, pX, pZ, iters, savefile=False, time_stamp=None, load_plot=False):

    TL0 = tl.lattice(size, False)
    (edge_data, stab_data, log_data) = TL0.init_data()

    N_succes = 0
    for i in range(iters):
        if i % printval == 0:
            print("Iteration " + str(i))
        TL = tl.lattice(size, load_plot)
        TL.load_data(edge_data, stab_data, log_data)
        TL.init_plots()
        TL.init_pauli(pX, pZ, savefile, time_stamp)
        TL.init_erasure(pE, savefile, time_stamp)
        TL.measure_stab()
        TL.get_matching_peeling()
        logical_error = TL.logical_error()
        if logical_error == [False, False, False, False]:
            N_succes += 1
    return N_succes


def planar_2D_MWPM(size, pX, pZ, iters, savefile=False, time_stamp=None, load_plot=False):

    PL0 = pl.lattice(size, False)
    (edge_data, stab_data, log_data) = PL0.init_data()

    N_succes = 0
    for i in range(iters):
        if i % printval == 0:
            print("Iteration " + str(i))
        PL = pl.lattice(size, load_plot)
        PL.load_data(edge_data, stab_data, log_data)
        PL.init_plots()
        PL.init_pauli(pX, pZ, savefile, time_stamp)
        PL.measure_stab()
        PL.get_matching_MWPM()
        logical_error = PL.logical_error()
        if logical_error == [False, False]:
            N_succes += 1
    return N_succes

a = [1, 2]
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
