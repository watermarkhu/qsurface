import toric_lat as tl
import planar_lat as pl


import sys
sys.path.insert(0, '../fault_tolerance_simulations/')
sys.path.insert(0, '../Code_Eduardo/')
import st
import Eduardo

def toric_2D_MWPM(size, pX, pZ, new_errors = True, write_errors = False, load_plot = False):
    TL = tl.lattice(size, load_plot)
    TL.init_pauli(pX, pZ, new_errors, write_errors)
    TL.measure_stab()
    TL.get_matching_MWPM()
    TL.apply_matching()
    logical_error = TL.logical_error()
    correct = True if logical_error == [0,0,0,0] else False
    return correct

def toric_2D_peeling(size, pX, pZ, new_errors = True, write_errors = False, load_plot = False):
    TL = tl.lattice(size, load_plot)
    TL.init_pauli(pX, pZ, new_errors, write_errors)
    TL.measure_stab()
    TL.get_matching_peeling()
    logical_error = TL.logical_error()
    correct = True if logical_error == [0,0,0,0] else False
    return correct

def planar_2D_MWPM(size, pX, pZ, new_errors = True, write_errors = False, load_plot = False):
    PL = pl.lattice(size, load_plot)
    PL.init_pauli(pX, pZ, new_errors, write_errors)
    PL.measure_stab()
    PL.get_matching_MWPM()
    PL.apply_matching()
    logical_error = PL.logical_error()
    correct = True if logical_error == [0,0] else False
    return correct

def toric_2D_nickerson(size, pX = 0, pZ = 0, i = 0):
    output = st.run2D(i, size, pX, pZ)
    correct = True if output == [[1,1],[1,1]] else False
    return correct

def toric_2D_eduardo(size, pX = 0, pZ = 0):
    output = Eduardo.thres_calc("toric", size, pX, pZ, 0, 1, 1, 0)
    correct = True if output == 0 else False
    return correct
