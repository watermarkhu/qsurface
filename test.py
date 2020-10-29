

#%%
import opensurfacesim 

#%%
benchmarker = opensurfacesim.main.BenchmarkDecoder({"decode":"duration"})
# benchmarker = None

output = opensurfacesim.main.run_multiprocess(10,Decoder="mwpm", processes=2,iterations=100, enabled_errors=["pauli"], error_rates={"p_bitflip": 0.1}, benchmark=benchmarker)

print(output)
# print(benchmarker.data)


# %%
from multiprocessing import Process, Manager

def f(d, b):
    d.dict["a"].append(b)
    d.dict["b"] += [b]
    d.b += b
    print(d.dict, d.b)


manager = Manager()

class Test():
    def __init__(self,):
        self.dict = manager.dict(a=[], b=[])
        self.b = 0

d = Test()

f(d, 3)
p1 = Process(target=f, args=(d,1))
p2 = Process(target=f, args=(d,2))
p1.start()
p2.start()
p1.join()
p2.join()


print(d.dict)

# %%
