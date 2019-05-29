import toric_lat as tl
import planar_lat as pl
import peeling as pel
import sys

sys.path.insert(0, '../fault_tolerance_simulations/')
sys.path.insert(0, '../Code_Eduardo/')

import Eduardo
import st


def toric_2D_MWPM(size, pX, pZ, iters, tsavefile=False, time_stamp=None, load_plot=False):

    TL0 = tl.lattice(size, False)
    stab_data = TL0.init_stab_data()

    N_succes = 0
    for i in range(iters):
        TL = tl.lattice(size, load_plot)
        TL.init_pauli(pX, pZ, tsavefile, time_stamp)
        TL.measure_stab(stab_data)
        TL.get_matching_MWPM()
        logical_error = TL.logical_error()
        if logical_error == [False, False, False, False]:
            N_succes += 1
    return N_succes


def toric_2D_peeling(size, pE, pX, pZ, iters, tsavefile=False, time_stamp=None, load_plot=False):

    TL0 = tl.lattice(size, False)
    stab_data = TL0.init_stab_data()

    peel = pel.toric(size, [], [], loadplot=False)
    edge_data = peel.init_edge_data()

    N_succes = 0
    for i in range(iters):
        TL = tl.lattice(size, load_plot)
        TL.init_pauli(pX, pZ, tsavefile, time_stamp)
        TL.init_erasure(pE, tsavefile, time_stamp)
        TL.measure_stab(stab_data)
        TL.get_matching_peeling(edge_data)
        logical_error = TL.logical_error()
        if logical_error == [False, False, False, False]:
            N_succes += 1
    return N_succes


def planar_2D_MWPM(size, pX, pZ, iters, tsavefile=False, time_stamp=None, load_plot=False):

    PL0 = pl.lattice(size, False)
    (plaq_data, star_data) = PL0.init_stab_data()

    N_succes = 0
    for i in range(iters):
        PL = pl.lattice(size, load_plot)
        PL.init_pauli(pX, pZ, tsavefile, time_stamp)
        PL.measure_stab(plaq_data, star_data)
        PL.get_matching_MWPM()
        logical_error = PL.logical_error()
        if logical_error == [False, False]:
            N_succes += 1
    return N_succes


### Other code

def toric_2D_nickerson(size, pX, pZ, iters):

    N_succes = 0
    for i in range(iters):
        output = st.run2D(size, pX, pZ)
        if output == [[1, 1], [1, 1]]:
            N_succes += 1
    return N_succes


def toric_2D_eduardo(size, pX, pZ, iters):

    N_succes = 0
    for i in range(iters):
        output = Eduardo.thres_calc("toric", size, pX, pZ, 0, 1, 1, 0)
        if output == 0:
            N_succes += 1
    return N_succes
