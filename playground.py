# import graph_objects as G
# import random
# import matplotlib.pyplot as plt
# import numpy as np
#
#
# class bidict(dict):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.inverse = {}
#         for key, value in self.items():
#             self.inverse.setdefault(value, []).append(key)
#
#     def __setitem__(self, key, value):
#         if key in self:
#             self.inverse[self[key]].remove(key)
#         super().__setitem__(key, value)
#         self.inverse.setdefault(value, []).append(key)
#
#     def __delitem__(self, key):
#         self.inverse.setdefault(self[key], []).remove(key)
#         if self[key] in self.inverse and not self.inverse[self[key]]:
#             del self.inverse[self[key]]
#         super().__delitem__(key)
#
#
#
# num = 100
# iter = 10000
# data = np.zeros((iter, num))
# l = [i for i in range(num)]
# k = [i for i in range(num)]
#
# for i in range(iter):
#     random.shuffle(k)
#     a = G.minbidict(zip(l, k))
#     data[i, :] = np.array(a.minlist)
#
# plt.errorbar(np.arange(num - 1, -1, -1), np.average(data, axis=0), np.std(data, axis=0))
# plt.plot(np.arange(num - 1, -1, -1), np.max(data, axis=0))
# plt.plot(np.arange(num - 1, -1, -1), np.min(data, axis=0))
# plt.xlabel("Index")
# plt.ylabel("Value")
# plt.title("Values in a list sorted with linear complexity")
# plt.show()
