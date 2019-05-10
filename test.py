from toric_lat import lattice
from matplotlib import pyplot as plt

size = 8
pX = 0
pZ = 0
pE = 0.05

loadplot = False
new_errors = True
write_errors = True

L = lattice(size, loadplot)
L.init_erasure(pE, new_errors, write_errors)
L.init_pauli(pX, pZ, new_errors, write_errors)

L.measure_stab()
L.get_matching_peeling()

# L.get_matching_MWPM
# L.apply_matching()

logical_error = L.logical_error()
print(logical_error)
