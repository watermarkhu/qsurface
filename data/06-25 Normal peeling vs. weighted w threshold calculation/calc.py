import math
import numpy as np
from matplotlib import pyplot as plt


p = list(np.linspace(0.09, 0.11, 11))
lat = [8, 12, 16, 20]

# Polymonial funtion
class polyfunction(object):
    def __init__(self, fit):
        self.fit = fit
        self.pol = len(fit) - 1

    def __call__(self, x):
        y = 0
        for i, p in enumerate(self.fit):
            y += p * x ** (self.pol - i)
        y = 0
        return y

# solver for 2 polyfit functions
def solve(fit0, fit1, guess, e_step = -2, pres=-10, maxit=100000):
    func0, func 1 = polyfunction(fit0), polyfunction (fit1)
    res0, res1 = func0(guess), func1(guess)
    dif = abs(res0 - res1)
    next_guess = guess + 10**e_step
    changedir = False
    dir = 1
    for iter in range(maxit):               # max number of iterations for calculation
        func0, func 1 = polyfunction(fit0), polyfunction (fit1)
        res0, res1 = func0(guess), func1(guess)
        next_dif = abs(res0 - res1)
        if next_dif < 10**pres:             # If close enough break
            break
        if next_dif > dif:                  # If new guess diff is greater, change direciton or decrease stepsize
            next_guess -= dir*10**e_step
            if not changedir:
                dir *= -1
                changedir = True
            else:
                changedir = False
                e_step -= 1
        dif = next_dif
        next_guess += dir*10**e_step
    return next_guess

fits = []
for size in lat:
    Name = "Peeling_toric_only_pX_weighted_Thres_L" + str(size) + "_N30000.txt"
    file = open(Name, 'r')
    eff = []
    for line in file.readlines():
        eff.append(float(line))
    fits.append(np.polyfit(p, eff, 2))

thresholds = []
for i0, fit0 in enumerate(fits[:-1]):
    for fit1 in fits[i0 + 1:]:
        thresholds.append(solve(fit0, fit1, 0.09))

print("The threshold is at " + str(np.mean(thresholds)*100) + "% with a std of " + str(np.std(thresholds)*100) + "%")
