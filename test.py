
#%%
 
from opensurfacesim.plot import PlotParams
params = PlotParams(color_x_primary=(0,0,1,1))


#%%
from opensurfacesim.main import *

code, decoder = initialize(
   6,
   "toric",
   "ufns",
   enabled_errors=["pauli"],
   plotting=True,
   plot_params = params,
   step_cluster=True,
   step_bucket=True,
   print_steps=0,
)
# benchmarker = BenchmarkDecoder({
#    "decode": ["duration"],
# })
benchmarker = BenchmarkDecoder(
   {
      "decode": ["duration", "value_to_list"],
      "correct_edge": "count_calls",
   }
)
output = run(code, decoder, iterations=500, error_rates={"p_bitflip": 0.1}, benchmark=benchmarker)

print(output)
# %%

# from opensurfacesim.threshold import *

# error_rates = [{"p_bitflip": p} for p in [0.09, 0.095, 0.1, 0.105, 0.11]]

# data = sim_thresholds(
#    "toric",
#    "ufns",
#    1000,
#    [8, 10, 12, 14],
#    ["pauli"],
#    error_rates,
#    methods_to_benchmark={"decode": ["duration", "value_to_list"], "correct_edge": "count_calls"},
# )
