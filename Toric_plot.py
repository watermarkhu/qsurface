from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from PIL import Image,ImageDraw,ImageFont
import math
import numpy as np
import random


class plotlattice:
    def __init__(self,size,plot):
        self.size = size
        self.fig = plt.figure()
        self.base = mpimg.imread('base.jpg')
        self.Xer = mpimg.imread('X_5.jpg')
        self.Yer = mpimg.imread('Y_5.jpg')
        self.Zer = mpimg.imread('Z_5.jpg')
        self.baseL = self.base.shape[0]
        self.erL = self.Xer.shape[0]
        self.latticeL = self.baseL*size
        self.lattice = np.tile(self.base,[size,size,1])
        self.l1 = 5
        self.l2 = 19
        self.fnt = ImageFont.truetype("arial.ttf", 10, encoding="unic")
        if plot:
            plt.imshow(self.lattice)
            plt.show()
    def plot_errors(self,errors,type,plot):
        Yloc,Xloc = np.where(errors==True)
        for Y2,X in zip(Yloc,Xloc):
            Y = math.floor(Y2/2)
            if Y2%2==0:
                Yb = Y*self.baseL+self.l1
                Xb = X*self.baseL+self.l2
            else:
                Yb = Y*self.baseL+self.l2
                Xb = X*self.baseL+self.l1
            if type == 'X':
                plot3 = self.Xer
            elif type == "Y":
                plot3 = self.Yer
            elif type == "Z":
                plot3 = self.Zer
            else:
                print("Unknown error type")
                plot3 = np.ones([self.erL,self.erL,3])
            self.lattice[Yb:(Yb+self.erL),Xb:(Xb+self.erL),:] = plot3
        if plot:
            plt.imshow(self.lattice)
            plt.show()
    def plotXstrings(self,vertices,strings,plot):
        ##########################
        # Plot strings (green) first

        # Create horizontal and vertical lines
        hline = np.zeros([8,3])
        hline[:,1] = 255
        vline = np.zeros([8,3])
        vline[:,1] = 255

        # Loop over all stings
        Yloc,Xloc = np.where(strings==True)
        for Y2,X2 in zip(Yloc,Xloc):
            Yb = math.floor(Y2/2)*self.baseL
            Xb = math.floor(X2/2)*self.baseL
            if Y2%2==0:
                if X2%2==0:     #top
                    self.lattice[Yb+7, Xb:(Xb+8), :] = hline
                else:           #bottom
                    self.lattice[Yb+7, (Xb+7):(Xb+15), :] = hline
            else:
                if X2%2==0:     #left
                    self.lattice[Yb:(Yb+8), Xb + 7,:] = vline
                else:           #right
                    self.lattice[(Yb+7):(Yb+15), Xb + 7, :] = vline

        #############################
        # Plot the vertices over the stings

        # Load vertice image
        bluevertice = mpimg.imread('bluevertice.jpg')
        bvL = bluevertice.shape[0]
        im = Image.new("RGBA", (self.latticeL,self.latticeL),(255,255,255,0))
        d = ImageDraw.Draw(im)
        d.fontmode = "1"

        # Loop over all vertices
        Yloc, Xloc = np.where(vertices == True)
        for i in range(len(Xloc)):
            Yb = Yloc[i]*self.baseL
            Xb = Xloc[i]*self.baseL
            self.lattice[Yb:(Yb+bvL),Xb:(Xb+bvL),:] = bluevertice
            d.text((Xb + 5,Yb+1),str(i), font=self.fnt, fill=(0, 0, 0, 255))

        imbase = Image.fromarray(self.lattice).convert("RGBA")
        self.lattice = Image.alpha_composite(imbase,im)

        if plot:
            plt.imshow(self.lattice)
            plt.show()

    def drawlines(self,inf,com):
        drawtext = True
        im = Image.new("RGBA", (self.latticeL,self.latticeL),(255,255,255,0))
        np.random.seed(1)
        color = np.array(np.round(np.random.random([com.shape[0],3])*255),dtype = int)
        imbase = self.lattice
        for string in range(com.shape[0]):
            c = color[string,:]
            if com[string,3] == 0 or com[string,3] == 2:
                d = ImageDraw.Draw(im)
                thiscolor1 = (c[0],c[1],c[2],150)
                topx = inf[com[string,0],1]
                topy = inf[com[string,0],0]
                botx = inf[com[string,1],1]
                boty = inf[com[string,1],0]
                top = (topx*self.baseL+7,topy*self.baseL+7)
                bot = (botx*self.baseL+7,boty*self.baseL+7)
                d.line([top,bot],fill = thiscolor1, width = 1)

                if drawtext:
                    d.fontmode = "1"
                    thiscolor2 = (c[0], c[1], c[2], 255)
                    midx = round((topx + botx)*self.baseL / 2)
                    midy = round((topy + boty)*self.baseL / 2)
                    d.text((midx,midy), str(string), font=self.fnt, fill=thiscolor2)
                im = Image.alpha_composite(imbase,im)
        plt.imshow(np.array(im))
        plt.show()