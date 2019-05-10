import toric_lat as tl
import planar_lat as pl


import sys
sys.path.insert(0, '../fault_tolerance_simulations/')
import st

def toric_2D(size, pX, pZ, new_errors = True, write_errors = False, load_plot = False):
    TL = tl.lattice(size, load_plot)
    TL.init_pauli(pX, pZ, new_errors, write_errors)
    TL.measure_stab()
    TL.get_matching_MWPM()
    TL.apply_matching()
    logical_error = TL.logical_error()
    correct = True if logical_error == [0,0,0,0] else False
    return correct

def planar_2D(size, pX, pZ, new_errors = True, write_errors = False, load_plot = False):
    PL = pl.lattice(size, load_plot)
    PL.init_pauli(pX, pZ, new_errors, write_errors)
    PL.measure_stab()
    PL.get_matching_MWPM()
    PL.apply_matching()
    logical_error = PL.logical_error()

    correct = True if logical_error == [0,0] else False
    return correct

def nickerson_toric_2D(size, pX = 0, pZ = 0, i = 0):
    output = st.run2D(i, size, pX, pZ)
    correct = True if output == [[1,1],[1,1]] else False
    return correct
