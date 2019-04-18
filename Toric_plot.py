from matplotlib import pyplot as plt
from PIL import Image,ImageDraw,ImageFont
import os
import copy
import numpy as np
import cv2






class plotlattice:

    def makebaseimage(self, input_size=13):

        qubit_size = (input_size - input_size % 4) + 1
        self.baseL = 2 * qubit_size + 2
        self.vecL = int((qubit_size - 1) / 2 + 1)
        self.erL = self.vecL - 2
        gray = 150
        w = 1

        im = np.ones((self.baseL, self.baseL, 3), np.uint8) * 255
        im = cv2.line(im, (self.vecL, 0), (self.vecL, qubit_size + 1), (gray, gray, gray), w)
        im = cv2.line(im, (0, self.vecL), (qubit_size + 1, self.vecL), (gray, gray, gray), w)
        im = cv2.circle(im, (self.vecL, qubit_size + self.vecL + 1), self.vecL - 1, (0, 0, 0), w)
        im = cv2.circle(im, (qubit_size + self.vecL + 1, self.vecL), self.vecL - 1, (0, 0, 0), w)
        
        self.base = im

        p = qubit_size + 2
        mid = qubit_size + self.vecL + 1
        while p < self.baseL:
            im[mid, p, :] = gray
            im[p, mid, :] = gray
            p += 2

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


    def __init__(self,size = 10):


        self.base_image_size = 17
        self.plot_indices = True
        self.plot_lattice = False
        self.plot_error = False
        self.plot_syndrome = False
        self.plot_matching = True

        self.size = size
        self.makebaseimage()
        
        self.latticeL = self.baseL*size
        self.lattice = np.tile(self.base,[size,size,1])
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
            plt.imshow(self.lattice)
            plt.show()


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
            plt.imshow(self.lattice)
            plt.show()


    def plotXstrings(self,Vplus,Vline,qua_loc,save = True):
        ##########################

        base = [self.baseL - 2 * self.vecL + 1, 0]
        vecl = [self.vecL - 1, self.vecL]
        linel = [self.vecL * 2 - 1, self.vecL * 2 + 1]


        for type in range(2):

            lattice = copy.copy(self.lattice)


            vertices = Vplus[type,:,:]
            strings = Vline[type,:,:]

            # Plot strings (green) first

            # Create horizontal and vertical lines
            line = np.zeros([vecl[type]+1,3])
            line[:,1] = 255

            # Loop over all stings
            Yloc,Xloc,Wloc = np.where(strings==0)
            for Y,X,W in zip(Yloc,Xloc,Wloc):
                Yb = Y*self.baseL + base[type]
                Xb = X*self.baseL + base[type]
                if W == 0:    #West
                    lattice[Yb+vecl[type], Xb:(Xb+vecl[type] + 1), :] = line
                elif W == 1:  #East
                    lattice[Yb+vecl[type], (Xb+vecl[type]):(Xb+2*vecl[type] + 1), :] = line
                elif W == 2:  #North
                    lattice[Yb:(Yb+vecl[type] + 1), Xb + vecl[type],:] = line
                else: #W == 3: South
                    lattice[(Yb+vecl[type]):(Yb+vecl[type]*2 + 1), Xb + vecl[type], :] = line

        #############################
        # Plot the vertices over the stings

            # Load vertice image
            line = np.zeros([linel[type],3])
            line[:,2] = 255

            im = Image.new("RGBA", (self.latticeL,self.latticeL),(255,255,255,0))
            d = ImageDraw.Draw(im)
            d.fontmode = "1"

            # Loop over all vertices
            for i in range(len(qua_loc[type])):
                Yb = qua_loc[type][i][0]*self.baseL + base[type]
                Xb = qua_loc[type][i][1]*self.baseL + base[type]
                lattice[Yb + vecl[type], Xb:Xb + linel[type], :] = line
                lattice[Yb:Yb + linel[type], Xb + vecl[type], :] = line
                if self.plot_indices:
                    d.text((Xb + 5,Yb+1),str(i), font=self.fnt, fill=(0, 0, 0, 255))

            imbase = Image.fromarray(lattice).convert("RGBA")
            lattice = Image.alpha_composite(imbase,im)

            if type == 0:
                self.latticeX = copy.copy(lattice)
            else:
                self.latticeZ = copy.copy(lattice)

        if self.plot_syndrome:
            f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
            ax1.imshow(self.latticeX)
            ax2.imshow(self.latticeZ)
            ax1.set_title("X errors")
            ax2.set_title("Z errors")
            plt.show()


    def drawlines(self,Results):

        base = [self.baseL - 2 * self.vecL + 1, 0]
        ex = [self.baseL - self.vecL, self.vecL]

        for type in range(2):

            im = Image.new("RGBA", (self.latticeL, self.latticeL), (255, 255, 255, 0))

            np.random.seed(1)
            color = np.array(np.round(np.random.random([len(Results[type]),3])*255),dtype = int)

            if type == 0:
                imbase = self.latticeX
            else:
                imbase = self.latticeZ

            for string in range(len(Results[type])):
                c = color[string,:]
                d = ImageDraw.Draw(im)
                thiscolor1 = (c[0],c[1],c[2],150)

                topx = Results[type][string][0][1]
                topy = Results[type][string][0][0]
                botx = Results[type][string][1][1]
                boty = Results[type][string][1][0]
                top = (topx*self.baseL+ex[type],topy*self.baseL+ex[type])
                bot = (botx*self.baseL+ex[type],boty*self.baseL+ex[type])
                d.line([top,bot],fill = thiscolor1, width = 1)

                if self.plot_indices:
                    d.fontmode = "1"
                    thiscolor2 = (c[0], c[1], c[2], 255)
                    midx = round((topx + botx)*self.baseL / 2 + base[type])
                    midy = round((topy + boty)*self.baseL / 2 + base[type])
                    d.text((midx,midy), str(string), font=self.fnt, fill=thiscolor2)

            im = Image.alpha_composite(imbase,im)

            er = int(round(self.vecL/4))
            for string in range(len(Results[type])):
                c = color[string,:]
                d = ImageDraw.Draw(im)
                thiscolor1 = (c[0],c[1],c[2],150)
                topx = Results[type][string][0][1]
                topy = Results[type][string][0][0]
                botx = Results[type][string][1][1]
                boty = Results[type][string][1][0]
                top = [topx*self.baseL+ex[type],topy*self.baseL+ex[type]]
                bot = [botx*self.baseL+ex[type],boty*self.baseL+ex[type]]
                d.ellipse([top[0] - er, top[1] - er, top[0] + er, top[1] + er], fill=thiscolor1)
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