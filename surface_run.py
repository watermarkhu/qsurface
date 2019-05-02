import toric_lattice as tl
import planar_lattice as pl

def toric_2D(size, pX, pZ, new_errors = True, write_errors = False, load_plot = False):
    TL = tl.lattice(size, load_plot)
    TL.init_errors(pX, pZ, new_errors, write_errors)
    TL.measure_stab()
    TL.get_matching()
    TL.apply_matching()
    logical_error = TL.logical_error()
    correct = True if logical_error == [0,0,0,0] else False
    return correct

def planar_2D(size, pX, pZ, new_errors = True, write_errors = False, load_plot = False):
    PL = pl.lattice(size, load_plot)
    PL.init_errors(pX, pZ, new_errors, write_errors)
    PL.measure_stab()
    PL.get_matching()
    PL.apply_matching()
    logical_error = PL.logical_error()

    correct = True if logical_error == [0,0] else False
    return correct
