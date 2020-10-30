   # #%%
   # from opensurfacesim.main import *

   # code, decoder = initialize(
   #    12,
   #    "toric",
   #    "ufns",
   #    enabled_errors=["pauli"],
   #    plotting=False,
   #    step_cluster=True,
   #    step_bucket=True,
   #    print_steps=0,
   # )
   # # benchmarker = BenchmarkDecoder({
   # #    "decode": ["duration"],
   # # })
   # benchmarker = BenchmarkDecoder(
   #    {
   #       "decode": ["duration", "value_to_list"],
   #       "correct_edge": "count_calls",
   #    }
   # )
   # output = run(code, decoder, iterations=500, error_rates={"p_bitflip": 0.1}, benchmark=benchmarker)

   # print(output)
   # # %%

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

# %%

from opensurfacesim.threshold import *

data = read_csv("toric_toric-pauli.csv")


#%%
thres = ThresholdFit()


# %%
figure = thres.plot_data(data, "p_bitflip")
# %%



from dataclasses import dataclass

@dataclass
class Test:
   value = "temp"

class Inherited(Test):
   pass
# %%
