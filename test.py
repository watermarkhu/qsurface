
#%%
from opensurfacesim.main import *

code, decoder = initialize(20, "toric", "ufns", enabled_errors=["pauli"], plotting=False, step_cluster=True, step_bucket=True, print_steps=0)
# benchmarker = BenchmarkDecoder({
#    "decode": ["duration"], 
# })
benchmarker = BenchmarkDecoder({
   "decode": ["duration", "value_to_list"], 
   "correct_edge": "count_calls",
})
output = run(code, decoder, iterations=500, error_rates = {"p_bitflip": 0.1}, benchmark=benchmarker)

print(output)
# %%

