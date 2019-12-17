
import pandas as pd
from collections import defaultdict as dd
from pprint import pprint

data = pd.read_csv("16.csv", names=["L", "p", "seed", "rm", "rp", "lm", "lp"])


def val(num):
    if num == 11:
        num = 2
    elif num == 10:
        num = 1
    return num

data

values = dd(lambda: [0,0])


for i in range(len(data)):

    resm = val(data.loc[i, "rm"])
    resp = val(data.loc[i, "rp"])

    if resm != resp:

        res = "m" if resm < resp else "p"

        lm = data.loc[i, "lm"]
        lp = data.loc[i, "lp"]
        if lm == lp:
            wei = "eq"
        else:
            wei = "pl"

        values[(res, wei)][0] += 1
        num = values[(res, wei)][0]
        values[(res, wei)][1] = (values[(res, wei)][1]*(num-1) + (lp-lm))/num

pprint(values)
