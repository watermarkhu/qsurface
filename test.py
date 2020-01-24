import run_toric_2D_uf as rt2
import unionfind_evengrow2 as uf
import time

t0 = time.time()
size = 12
pX = 0.05
pZ = 0
pE = 0.0
iters = 10000

plot_load = 1
output = rt2.single(size, pE, pX, pZ, plot_load=plot_load, uf=uf)
# output = rt2.multiple(size, iters, pE, pX, pZ, plot_load=plot_load, uf=uf)
# output = rt2.multiprocess(size, iters, pE, pX, pZ, uf=uf)

print("time taken =", time.time() - t0)
print("p = " + str(output / iters * 100) + "%")
