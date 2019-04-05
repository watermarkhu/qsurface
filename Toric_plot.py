from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from PIL import Image,ImageDraw,ImageFont
import math
import numpy as np
import cv2



def makebaseimage(input_size = 13):

    qubit_size = (input_size-input_size%4) + 1
    baseL = 2 * qubit_size + 2
    vecL  = int((qubit_size - 1 )/2 + 1)
    erL = vecL - 2
    gray = 150
    w = 1

    im = np.ones((baseL,baseL,3),np.uint8)*255
    im = cv2.line(im,(vecL,0), (vecL,qubit_size+1),(gray,gray,gray),w)
    im = cv2.line(im,(0,vecL), (qubit_size+1,vecL),(gray,gray,gray),w)
    im = cv2.circle(im,(vecL,qubit_size+vecL+1),vecL-1,(0,0,0),w)
    im = cv2.circle(im,(qubit_size+vecL+1,vecL),vecL-1,(0,0,0),w)

    p = qubit_size + 2
    mid = qubit_size+vecL+1
    while p < baseL:
        im[mid,p,:] = gray
        im[p,mid,:] = gray
        p += 2


    half = int(erL/2)
    end = erL -1

    Xim = np.ones((erL,erL,3), np.uint8)*255
    Xim = cv2.line(Xim, (0,0), (end,end),(0,0,0),w)
    Xim = cv2.line(Xim, (0,end), (end,0), (0,0,0),w)

    Zim = np.ones((erL,erL,3), np.uint8)*255
    Zim = cv2.line(Zim, (0,0), (end,0),(0,0,0),w)
    Zim = cv2.line(Zim, (0,end), (end,0), (0,0,0),w)
    Zim = cv2.line(Zim, (0,end), (end,end),(0,0,0),w)


    Yim = np.ones((erL,erL,3), np.uint8)*255
    Yim = cv2.line(Yim, (half,half), (half,end),(0,0,0),w)
    Yim = cv2.line(Yim, (half,half), (0,0),(0,0,0),w)
    Yim = cv2.line(Yim, (half,half), (end,0),(0,0,0),w)

    return(im,Xim,Yim,Zim)

class plotlattice:


    def __init__(self,size = 10,plot = True, base_image_size = 17, plot_indices = False):
        self.size = size
        self.plot_indices = plot_indices
        (self.base, self.Xer, self.Yer, self.Zer) = makebaseimage(base_image_size)
        self.baseL = self.base.shape[0]
        self.vecL = int(self.baseL/4)
        self.erL = self.Xer.shape[0]
        self.latticeL = self.baseL*size
        self.lattice = np.tile(self.base,[size,size,1])
        self.l1 = int(((self.baseL-2)/2 - self.erL)/2 + 1)
        self.l2 = int(self.baseL/2 + self.l1)
        self.fnt = ImageFont.truetype("arial.ttf", 10, encoding="unic")
        self.fig = plt.figure()
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
        line = np.zeros([self.vecL+1,3])
        line[:,1] = 255

        # Loop over all stings
        Yloc,Xloc = np.where(strings==True)
        for Y2,X2 in zip(Yloc,Xloc):
            Yb = math.floor(Y2/2)*self.baseL
            Xb = math.floor(X2/2)*self.baseL
            if Y2%2==0:
                if X2%2==0:     #top
                    self.lattice[Yb+self.vecL, Xb:(Xb+self.vecL + 1), :] = line
                else:           #bottom
                    self.lattice[Yb+self.vecL, (Xb+self.vecL):(Xb+2*self.vecL + 1), :] = line
            else:
                if X2%2==0:     #left
                    self.lattice[Yb:(Yb+self.vecL + 1), Xb + self.vecL,:] = line
                else:           #right
                    self.lattice[(Yb+self.vecL):(Yb+self.vecL*2 + 1), Xb + self.vecL, :] = line

        #############################
        # Plot the vertices over the stings

        # Load vertice image
        line = np.zeros([self.vecL*2+1,3])
        line[:,2] = 255

        im = Image.new("RGBA", (self.latticeL,self.latticeL),(255,255,255,0))
        d = ImageDraw.Draw(im)
        d.fontmode = "1"

        # Loop over all vertices
        Yloc, Xloc = np.where(vertices == True)
        for i in range(len(Xloc)):
            Yb = Yloc[i]*self.baseL
            Xb = Xloc[i]*self.baseL
            self.lattice[Yb + self.vecL, Xb:(Xb + self.vecL * 2 + 1), :] = line
            self.lattice[Yb:(Yb + self.vecL * 2 + 1), Xb + self.vecL, :] = line
            if self.plot_indices:
                d.text((Xb + 5,Yb+1),str(i), font=self.fnt, fill=(0, 0, 0, 255))

        imbase = Image.fromarray(self.lattice).convert("RGBA")
        self.lattice = Image.alpha_composite(imbase,im)

        if plot:
            plt.imshow(self.lattice)
            plt.show()

    def drawlines(self,inf,com):
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
                top = (topx*self.baseL+self.vecL,topy*self.baseL+self.vecL)
                bot = (botx*self.baseL+self.vecL,boty*self.baseL+self.vecL)
                d.line([top,bot],fill = thiscolor1, width = 1)

                if self.plot_indices:
                    d.fontmode = "1"
                    thiscolor2 = (c[0], c[1], c[2], 255)
                    midx = round((topx + botx)*self.baseL / 2)
                    midy = round((topy + boty)*self.baseL / 2)
                    d.text((midx,midy), str(string), font=self.fnt, fill=thiscolor2)
                im = Image.alpha_composite(imbase,im)

        er = int(round(self.vecL/4))
        for string in range(com.shape[0]):
            c = color[string,:]
            if com[string,3] == 0 or com[string,3] == 2:
                d = ImageDraw.Draw(im)
                thiscolor1 = (c[0],c[1],c[2],150)
                topx = inf[com[string,0],1]
                topy = inf[com[string,0],0]
                botx = inf[com[string,1],1]
                boty = inf[com[string,1],0]
                top = [topx*self.baseL+self.vecL,topy*self.baseL+self.vecL]
                bot = [botx*self.baseL+self.vecL,boty*self.baseL+self.vecL]
                d.ellipse([top[0] - er, top[1] - er, top[0] + er, top[1] + er], fill=thiscolor1)
                d.ellipse([bot[0] - er, bot[1] - er, bot[0] + er, bot[1] + er], fill=thiscolor1)

        return np.array(im)