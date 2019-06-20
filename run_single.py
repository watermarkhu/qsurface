import toric_lat as tl
import planar_lat as pl
import sys

sys.path.insert(0, '../fault_tolerance_simulations/')
# sys.path.insert(0, '../Code_Eduardo/')
#
# import Eduardo
import st



def toric_2D_MWPM(size, pX, pZ, savefile=False, time_stamp=None, load_plot=False):
    TL = tl.lattice(size, load_plot)
    TL.init_data()
    TL.init_plots()
    TL.init_pauli(pX, pZ, savefile, time_stamp)
    TL.measure_stab()
    TL.get_matching_MWPM()
    logical_error = TL.logical_error()
    correct = True if logical_error == [False, False, False, False] else False
    return correct


def toric_2D_peeling(size, pE, pX=0, pZ=0, savefile=False, time_stamp=None, load_plot=False):
    TL = tl.lattice(size, load_plot)
    TL.init_data()
    TL.init_plots()
    TL.init_erasure(pE, savefile, time_stamp)
    TL.init_pauli(pX, pZ, savefile, time_stamp)
    TL.measure_stab()
    TL.get_matching_peeling()
    logical_error = TL.logical_error()
    correct = True if logical_error == [False, False, False, False] else False
    return correct


def planar_2D_MWPM(size, pX, pZ, savefile=False, time_stamp=None, load_plot=False):
    PL = pl.lattice(size, load_plot)
    PL.init_data()
    PL.init_plots()
    PL.init_pauli(pX, pZ, savefile, time_stamp)
    PL.measure_stab()
    PL.get_matching_MWPM()
    logical_error = PL.logical_error()
    correct = True if logical_error == [False, False] else False
    return correct


def toric_2D_nickerson(size, pX=0, pZ=0):
    output = st.run2D(size, pX, pZ)
    correct = True if output == [[1, 1], [1, 1]] else False
    return correct


# def toric_2D_eduardo(size, pX=0, pZ=0):
#     output = Eduardo.thres_calc("toric", size, pX, pZ, 0, 1, 1, 0)
#     correct = True if output == 0 else False
#     return correct
