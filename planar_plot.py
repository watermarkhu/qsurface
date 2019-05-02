from matplotlib import pyplot as plt
from PIL import Image,ImageDraw,ImageFont
import os
import copy
import numpy as np
import cv2


class plotlattice:

    def __init__(self,size = 10):


        self.base_image_size = 17
        self.plot_lattice = False
        self.plot_error = False
        self.plot_syndrome = False
        self.plot_matching = True
        self.size = size
        self.makebaseimage()

        self.latticeL = self.baseL*size
        self.l1 = int(((self.baseL-2)/2 - self.erL)/2 + 1)
        self.l2 = int(self.baseL/2 + self.l1)

        if os.name == "windows":
            self.fnt = ImageFont.truetype("arial.ttf", 10, encoding="unic")
        elif os.name == "posix":
            self.fnt = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf")
        else:
            print("Error: unknown os")
            return


        if self.plot_lattice:
            plt.imshow(self.lattice/255)
            plt.show()


    def makebaseimage(self, input_size=13):

        qubit_size = (input_size - input_size % 4) + 1
        self.baseL = 2 * qubit_size + 2
        self.vecL = int((qubit_size - 1) / 2 + 1)
        self.erL = self.vecL - 2
        mid = qubit_size + self.vecL + 1
        gray = 150
        w = 1

        # Normal tile 0
        im0 = np.ones((self.baseL, self.baseL, 3), np.uint8) * 255
        im0 = cv2.line(im0, (self.vecL, 0), (self.vecL, qubit_size + 1), (gray, gray, gray), w)       # vertical line
        im0 = cv2.line(im0, (0, self.vecL), (qubit_size + 1, self.vecL), (gray, gray, gray), w)       # horizontal line
        im0 = cv2.circle(im0, (qubit_size + self.vecL + 1, self.vecL), self.vecL - 1, (0, 0, 0), w)   # T qubit
        im0 = cv2.circle(im0, (self.vecL, qubit_size + self.vecL + 1), self.vecL - 1, (0, 0, 0), w)   # D qubit
        p = qubit_size + 2
        while p < self.baseL:
            im0[p, mid, :] = gray    # vertical dashed line
            im0[mid, p, :] = gray    # horizontal dashed
            p += 2

        # Left bottom tile 1
        im1 = np.ones((self.baseL, self.baseL, 3), np.uint8) * 255
        im1 = cv2.circle(im1, (qubit_size + self.vecL + 1, self.vecL), self.vecL - 1, (0, 0, 0), w)   # T qubit

        # Left tile 2
        im2 = np.ones((self.baseL, self.baseL, 3), np.uint8) * 255
        im2 = cv2.circle(im2, (qubit_size + self.vecL + 1, self.vecL), self.vecL - 1, (0, 0, 0), w)   # T qubit
        pv = qubit_size + 2
        ph = qubit_size + self.vecL + 3
        while pv < self.baseL:
            im2[pv, mid, :] = gray    # vertical dashed line
            pv += 2
        while ph < self.baseL:
            im2[mid, ph, :] = gray    # horizontal dashed
            ph += 2

        # Top tile 3
        im3 = np.ones((self.baseL, self.baseL, 3), np.uint8) * 255
        im3 = cv2.line(im3, (self.vecL, self.vecL), (self.vecL, qubit_size + 1), (gray, gray, gray), w)       # vertical line
        im3 = cv2.line(im3, (0, self.vecL), (qubit_size + 1, self.vecL), (gray, gray, gray), w)       # horizontal line
        im3 = cv2.circle(im3, (qubit_size + self.vecL + 1, self.vecL), self.vecL - 1, (0, 0, 0), w)   # T qubit
        im3 = cv2.circle(im3, (self.vecL, qubit_size + self.vecL + 1), self.vecL - 1, (0, 0, 0), w)   # D qubit
        p = qubit_size + 2
        while p < self.baseL:
            im3[p, mid, :] = gray    # vertical dashed line
            im3[mid, p, :] = gray    # horizontal dashed
            p += 2


        # Top right tile 4
        im4 = np.ones((self.baseL, self.baseL, 3), np.uint8) * 255
        im4 = cv2.line(im4, (self.vecL, self.vecL), (self.vecL, qubit_size + 1), (gray, gray, gray), w)       # vertical line
        im4 = cv2.line(im4, (0, self.vecL), (qubit_size + 1, self.vecL), (gray, gray, gray), w)       # horizontal line
        im4 = cv2.circle(im4, (qubit_size + self.vecL + 1, self.vecL), self.vecL - 1, (0, 0, 0), w)   # T qubit
        im4 = cv2.circle(im4, (self.vecL, qubit_size + self.vecL + 1), self.vecL - 1, (0, 0, 0), w)   # D qubit
        p = qubit_size + 2
        while p < self.baseL:
            im4[p, mid, :] = gray    # vertical dashed line
            p += 2
        p = qubit_size + 2
        while p < self.baseL - self.vecL:
            im4[mid, p, :] = gray    # vertical dashed line
            p += 2

        # Tight tile 5
        im5 = np.ones((self.baseL, self.baseL, 3), np.uint8) * 255
        im5 = cv2.line(im5, (self.vecL, 0), (self.vecL, qubit_size + 1), (gray, gray, gray), w)       # vertical line
        im5 = cv2.line(im5, (0, self.vecL), (qubit_size + 1, self.vecL), (gray, gray, gray), w)       # horizontal line
        im5 = cv2.circle(im5, (qubit_size + self.vecL + 1, self.vecL), self.vecL - 1, (0, 0, 0), w)   # T qubit
        im5 = cv2.circle(im5, (self.vecL, qubit_size + self.vecL + 1), self.vecL - 1, (0, 0, 0), w)   # D qubit
        p = qubit_size + 2
        while p < self.baseL:
            im5[p, mid, :] = gray    # vertical dashed line
            p += 2
        p = qubit_size + 2
        while p < self.baseL - self.vecL:
            im5[mid, p, :] = gray    # vertical dashed line
            p += 2

        # Bottom tile 6
        im6 = np.ones((self.baseL, self.baseL, 3), np.uint8) * 255
        im6 = cv2.line(im6, (self.vecL, 0), (self.vecL, self.vecL), (gray, gray, gray), w)       # vertical line
        im6 = cv2.line(im6, (0, self.vecL), (qubit_size + 1, self.vecL), (gray, gray, gray), w)       # horizontal line
        im6 = cv2.circle(im6, (qubit_size + self.vecL + 1, self.vecL), self.vecL - 1, (0, 0, 0), w)   # T qubit



        self.lattice = np.zeros([self.baseL*self.size, self.baseL*self.size, 3])

        for y in range(self.size):
            for x in range(self.size):
                left = True if x == 0 else False
                right = True if x == self.size - 1 else False
                top = True if y == 0 else False
                bot = True if y == self.size - 1 else False



                if not any([left, right, top, bot]):
                    self.lattice[y*self.baseL:(y+1)*self.baseL, x*self.baseL:(x+1)*self.baseL,:] = im0
                elif left and not bot:
                    self.lattice[y*self.baseL:(y+1)*self.baseL, x*self.baseL:(x+1)*self.baseL,:] = im2
                elif bot and not left:
                    self.lattice[y*self.baseL:(y+1)*self.baseL, x*self.baseL:(x+1)*self.baseL,:] = im6
                elif top and not any([left, right]):
                    self.lattice[y*self.baseL:(y+1)*self.baseL, x*self.baseL:(x+1)*self.baseL,:] = im3
                elif right and not any([top, bot]):
                    self.lattice[y*self.baseL:(y+1)*self.baseL, x*self.baseL:(x+1)*self.baseL,:] = im5
                elif top and right:
                    self.lattice[y*self.baseL:(y+1)*self.baseL, x*self.baseL:(x+1)*self.baseL,:] = im4
                else:
                    self.lattice[y*self.baseL:(y+1)*self.baseL, x*self.baseL:(x+1)*self.baseL,:] = im1


        half = int(self.erL / 2)
        end = self.erL - 1

        self.Xer = np.ones((self.erL, self.erL, 3), np.uint8) * 255
        self.Xer = cv2.line(self.Xer, (0, 0), (end, end), (0, 0, 0), w)
        self.Xer = cv2.line(self.Xer, (0, end), (end, 0), (0, 0, 0), w)

        self.Zer = np.ones((self.erL, self.erL, 3), np.uint8) * 255
        self.Zer = cv2.line(self.Zer, (0, 0), (end, 0), (0, 0, 0), w)
        self.Zer = cv2.line(self.Zer, (0, end), (end, 0), (0, 0, 0), w)
        self.Zer = cv2.line(self.Zer, (0, end), (end, end), (0, 0, 0), w)

        self.Yer = np.ones((self.erL, self.erL, 3), np.uint8) * 255
        self.Yer = cv2.line(self.Yer, (half, half), (half, end), (0, 0, 0), w)
        self.Yer = cv2.line(self.Yer, (half, half), (0, 0), (0, 0, 0), w)
        self.Yer = cv2.line(self.Yer, (half, half), (end, 0), (0, 0, 0), w)

        self.Xerr = np.ones((self.erL, self.erL, 3), np.uint8) * 255
        self.Xerr = cv2.line(self.Xerr, (0, 0), (end, end), (255, 0, 0), w)
        self.Xerr = cv2.line(self.Xerr, (0, end), (end, 0), (255, 0, 0), w)

        self.Zerr = np.ones((self.erL, self.erL, 3), np.uint8) * 255
        self.Zerr = cv2.line(self.Zerr, (0, 0), (end, 0), (255, 0, 0), w)
        self.Zerr = cv2.line(self.Zerr, (0, end), (end, 0), (255, 0, 0), w)
        self.Zerr = cv2.line(self.Zerr, (0, end), (end, end), (255, 0, 0), w)

        self.Yerr = np.ones((self.erL, self.erL, 3), np.uint8) * 255
        self.Yerr = cv2.line(self.Yerr, (half, half), (half, end), (255, 0, 0), w)
        self.Yerr = cv2.line(self.Yerr, (half, half), (0, 0), (255, 0, 0), w)
        self.Yerr = cv2.line(self.Yerr, (half, half), (end, 0), (255, 0, 0), w)




    def plot_errors(self, X_er_loc, Z_er_loc, Y_er_loc, plot = None):

        Xer = copy.copy(X_er_loc)
        Yer = copy.copy(Y_er_loc)
        Zer = copy.copy(Z_er_loc)

        for Y_er in Yer:
            del Xer[Xer.index(Y_er)]
            del Zer[Zer.index(Y_er)]

        if plot == "matching":
            Xlet = self.Xerr
            Zlet = self.Zerr
            Ylet = self.Yerr
            base = 1
        else:
            Xlet = self.Xer
            Zlet = self.Zer
            Ylet = self.Yer
            base = 0


        for (Y,X,HV) in Xer:
            if HV == 0:
                Yb = Y*self.baseL+self.l1 + base
                Xb = X*self.baseL+self.l2 + base
            else:
                Yb = Y*self.baseL+self.l2 + base
                Xb = X*self.baseL+self.l1 + base
            self.lattice[Yb:(Yb+self.erL),Xb:(Xb+self.erL),:] = Xlet
        for (Y,X,HV) in Zer:
            if HV == 0:
                Yb = Y*self.baseL+self.l1 + base
                Xb = X*self.baseL+self.l2 + base
            else:
                Yb = Y*self.baseL+self.l2 + base
                Xb = X*self.baseL+self.l1 + base
            self.lattice[Yb:(Yb+self.erL),Xb:(Xb+self.erL),:] = Zlet
        for Y,X,HV in Yer:
            if HV == 0:
                Yb = Y*self.baseL+self.l1 + base
                Xb = X*self.baseL+self.l2 + base
            else:
                Yb = Y*self.baseL+self.l2 + base
                Xb = X*self.baseL+self.l1 + base
            self.lattice[Yb:(Yb+self.erL),Xb:(Xb+self.erL),:] = Ylet


        if self.plot_error or plot:
            plt.imshow(self.lattice/255)
            plt.show()


    def plotXstrings(self,qua_loc,save = True):
        ##########################

        base = [self.baseL - 2 * self.vecL + 1, 0]
        vecl = [self.vecL - 1, self.vecL]
        linel = [self.vecL * 2 - 1, self.vecL * 2 + 1]
        linels = [self.vecL - 1, self.vecL + 1]




        #############################
        # Plot the vertices over the stings


        lattice = copy.copy(self.lattice)


        # Load vertice image
        line = np.zeros([linel[0],3])
        line[:,2] = 255
        lines = np.zeros([linels[0],3])
        lines[:,2] = 255


        # Loop over all vertices
        for i in range(len(qua_loc[0])):
            Y = qua_loc[0][i][0]
            X = qua_loc[0][i][1]
            Yb = Y*self.baseL + base[0]
            Xb = X*self.baseL + base[0]
            if X not in [0, self.size - 1]:
                lattice[Yb + vecl[0], Xb:Xb + linel[0], :] = line
            elif X == 0:
                lattice[Yb + vecl[0], Xb + vecl[0] + 1 :Xb + linel[0], :] = lines
            else:
                lattice[Yb + vecl[0], Xb : Xb + vecl[0], :] = lines
            lattice[Yb:Yb + linel[0], Xb + vecl[0], :] = line

        self.latticeX = copy.copy(lattice)

        #############################
        # Plot the vertices over the stings


        lattice = copy.copy(self.lattice)


        # Load vertice image
        line = np.zeros([linel[1],3])
        line[:,2] = 255
        lines = np.zeros([linels[1],3])
        lines[:,2] = 255


        # Loop over all vertices
        for i in range(len(qua_loc[1])):
            Y = qua_loc[1][i][0]
            X = qua_loc[1][i][1] + 1
            Yb = Y*self.baseL + base[1]
            Xb = X*self.baseL + base[1]
            lattice[Yb + vecl[1], Xb:Xb + linel[1], :] = line

            if Y not in [0, self.size - 1]:
                lattice[Yb:Yb + linel[1], Xb + vecl[1], :] = line
            elif Y == 0:
                lattice[Yb + vecl[1] :Yb + linel[1], Xb + vecl[1], :] = lines
            else:
                lattice[Yb:Yb + vecl[1]+1, Xb + vecl[1], :] = lines

        self.latticeZ = copy.copy(lattice)

        if self.plot_syndrome:
            f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
            ax1.imshow(self.latticeX/255)
            ax2.imshow(self.latticeZ/255)
            ax1.set_title("X errors")
            ax2.set_title("Z errors")
            plt.show()


    def drawlines(self, Results):

        base = [self.baseL - 2 * self.vecL + 1, 0]
        ex = [self.baseL - self.vecL, self.vecL]

        for type in range(2):

            im = Image.new("RGBA", (self.latticeL, self.latticeL), (255, 255, 255, 0))

            np.random.seed(1)
            color = np.array(np.round(np.random.random([len(Results[type]),3])*255),dtype = int)

            if type == 0:
                lattice = self.latticeX.round().astype('uint8')
            else:
                lattice = self.latticeZ.round().astype('uint8')

            for pairi in range(len(Results[type])):
                pair = Results[type][pairi]
                c = color[pairi,:]
                d = ImageDraw.Draw(im)
                thiscolor1 = (c[0],c[1],c[2],150)

                (topy, topx) = pair[0]
                (boty, botx) = pair[1]

                if type ==1:
                    topx += 1
                    botx += 1

                if all(x not in [topy, topx, boty, botx] for x in [-1, self.size]):
                    top = (topx*self.baseL+ex[type],topy*self.baseL+ex[type])
                    bot = (botx*self.baseL+ex[type],boty*self.baseL+ex[type])
                    d.line([top,bot],fill = thiscolor1, width = 1)

            imbase = Image.fromarray(lattice).convert("RGBA")
            im = Image.alpha_composite(imbase,im)

            er = int(round(self.vecL/4))
            for pairi in range(len(Results[type])):
                pair = Results[type][pairi]
                c = color[pairi,:]
                d = ImageDraw.Draw(im)
                thiscolor1 = (c[0],c[1],c[2],150)
                (topy, topx) = pair[0]
                (boty, botx) = pair[1]
                if type ==1:
                    topx += 1
                    botx += 1
                top = [topx*self.baseL+ex[type],topy*self.baseL+ex[type]]
                bot = [botx*self.baseL+ex[type],boty*self.baseL+ex[type]]

                if all(x not in [topy, topx] for x in [-1, self.size]):
                    d.ellipse([top[0] - er, top[1] - er, top[0] + er, top[1] + er], fill=thiscolor1)
                if all(x not in [boty, botx] for x in [-1, self.size]):
                    d.ellipse([bot[0] - er, bot[1] - er, bot[0] + er, bot[1] + er], fill=thiscolor1)

            if type == 0:
                self.latticeX = copy.copy(im)
            else:
                self.latticeZ = copy.copy(im)

        if self.plot_matching:
            f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
            ax1.imshow(self.latticeX)
            ax2.imshow(self.latticeZ)
            ax1.set_title("X errors")
            ax2.set_title("Z errors")
            plt.show()
