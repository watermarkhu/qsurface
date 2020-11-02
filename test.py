from os import truncate
from opensurfacesim.main import *
import random
import timeit


seed = 13385.775813716
# Initialize lattice
if not seed:
    seed = timeit.default_timer()
random.seed(seed)
print(seed)

plotting = False
iters = 500
error_keys = ["p_bitflip", "p_erasure"]

code, decoder = initialize(12, "planar", "ufns", ["pauli", "erasure"], plotting=plotting, step_bucket=True, step_peel=True, print_steps=True)
trivial = 0
for iter in range(iters):
    error_rates = {key: random.random() * 0.3 for key in error_keys}
    code.random_errors(**error_rates)
    code.state_icons(measure=True)
    decoder.decode()
    trivial += code.trivial_ancillas
    if plotting:
        code.show_corrected()

print(trivial)

