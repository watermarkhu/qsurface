import matplotlib.pyplot as plt
import numpy as np
import time

class toric_peeling_plot:

    def __init__(self, size):

        self.size = size

        self.cl = [0.8, 0.8, 0.8]       # Line color
        self.cx = [0.9, 0.3, 0.3]       # X error color
        self.cz = [0.5, 0.5, 0.9]       # Z error color
        self.cX = [0.9, 0.7, 0.3]
        self.cZ = [0.3, 0.9, 0.3]


        self.qsize = 0.1
        self.lw = 2

        self.step = 0.01
        self.stepwait = False

        self.f = plt.figure(2)
        self.ax = plt.gca()
        self.ax.invert_yaxis()
        self.ax.set_aspect('equal')
        plt.ion()
        plt.show()

    def plot_lattice(self, qua_loc, erasures):

        plt.figure(self.f.number)

        for y in range(self.size):
            y1 = y - 1/2
            for x in range(self.size):
                x1 = x - 1/2

                if (0, y, x) in erasures:
                    self.ax.plot([x, x], [y, y-1], c = self.cx, lw = self.lw, ls = '-')
                    self.ax.plot([x1, x1+1], [y1, y1], c = self.cz, lw = self.lw, ls = '--')
                else:
                    self.ax.plot([x, x], [y, y-1], c = self.cl, lw = self.lw, ls = '-')
                    self.ax.plot([x1, x1+1], [y1, y1], c = self.cl, lw = self.lw, ls = '--')

                if (1, y, x) in erasures:
                    self.ax.plot([x, x-1], [y, y], c = self.cx, lw = self.lw, ls = '-')
                    self.ax.plot([x1, x1], [y1, y1+1], c = self.cz, lw = self.lw, ls = '--')
                else:
                    self.ax.plot([x, x-1], [y, y], c = self.cl, lw = self.lw, ls = '-')
                    self.ax.plot([x1, x1], [y1, y1+1], c = self.cl, lw = self.lw, ls = '--')


                if (y,x) in qua_loc[0]:
                    circle0 = plt.Circle((x, y), self.qsize, facecolor = self.cx, linewidth = 0)
                    self.ax.add_artist(circle0)

                if (y,x) in qua_loc[1]:
                    circle1 = plt.Circle((x1, y1), self.qsize, facecolor = self.cz, linewidth = 0)
                    self.ax.add_artist(circle1)
        plt.draw()
        plt.waitforbuttonpress()

    def plot_removed(self, rem_list):

        plt.figure(self.f.number)



        for (hv, y, x) in rem_list[0]:
            if hv == 0:
                self.ax.plot([x, x], [y, y-1], c = self.cl, lw = self.lw, ls = '-')
            else:
                self.ax.plot([x, x-1], [y, y], c = self.cl, lw = self.lw, ls = '-')

        for (hv, y, x) in rem_list[1]:
            y1 = y-1/2
            x1 = x-1/2
            if hv == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = self.cl, lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = self.cl, lw = self.lw, ls = '--')

        plt.draw()
        plt.waitforbuttonpress()



    def plot_removed_step(self, ertype, rem_v):

        plt.figure(self.f.number)

        hv = rem_v[0]
        y = rem_v[1]
        x = rem_v[2]

        if ertype == 0:
            if hv == 0:
                self.ax.plot([x, x], [y, y-1], c = 'k', lw = self.lw, ls = '-')
            else:
                self.ax.plot([x, x-1], [y, y], c = 'k', lw = self.lw, ls = '-')
        else:
            y1 = y-1/2
            x1 = x-1/2
            if hv == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = 'k', lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = 'k', lw = self.lw, ls = '--')

        plt.draw()
        if self.stepwait: plt.waitforbuttonpress()
        else: plt.pause(self.step)

        if ertype == 0:
            if hv == 0:
                self.ax.plot([x, x], [y, y-1], c = self.cl, lw = self.lw, ls = '-')
            else:
                self.ax.plot([x, x-1], [y, y], c = self.cl, lw = self.lw, ls = '-')
        else:
            y1 = y-1/2
            x1 = x-1/2
            if hv == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = self.cl, lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = self.cl, lw = self.lw, ls = '--')

    def plot_tree_step(self, ertype, v):

        plt.figure(self.f.number)

        hv = v[0]
        y = v[1]
        x = v[2]

        if ertype == 0:
            if hv == 0:
                self.ax.plot([x, x], [y, y-1], c = self.cX, lw = self.lw, ls = '-')
            else:
                self.ax.plot([x, x-1], [y, y], c = self.cX, lw = self.lw, ls = '-')
        else:
            y1 = y-1/2
            x1 = x-1/2
            if hv == 0:
                self.ax.plot([x1, x1+1], [y1, y1], c = self.cZ, lw = self.lw, ls = '--')
            else:
                self.ax.plot([x1, x1], [y1, y1+1], c = self.cZ, lw = self.lw, ls = '--')

        plt.draw()
        if self.stepwait: plt.waitforbuttonpress()
        else: plt.pause(self.step)
