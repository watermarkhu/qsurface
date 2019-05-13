import ctypes
from numpy.ctypeslib import ndpointer
import os
import time



def getMatching_fast(numNodes,nodes1, nodes2, weights):
	
	numEdges=len(nodes1);

	PMlib=ctypes.CDLL("%s/PMlib.so"%"/".join((os.path.realpath(__file__)).split("/")[:-1]))

	PMlib.pyMatching.argtypes = [ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int)]


	PMlib.pyMatching.restype = ndpointer(dtype=ctypes.c_int, shape=(numNodes,))

# initialize ctypes array and fill with edge data
	n1=(ctypes.c_int*numEdges)();
	n2=(ctypes.c_int*numEdges)();
	w=(ctypes.c_int*numEdges)();

	for i in range(numEdges):
		n1[i],n2[i],w[i]=nodes1[i],nodes2[i],weights[i]

	result=PMlib.pyMatching(ctypes.c_int(numNodes),ctypes.c_int(numEdges),n1,n2,w)

	return result






def getMatching(numNodes,graphArray):
	
	mtime0 = time.time()

	numEdges=len(graphArray);
	
	

	PMlib=ctypes.CDLL("%s/PMlib.so"%"/".join((os.path.realpath(__file__)).split("/")[:-1]))

	PMlib.pyMatching.argtypes = [ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int)]


	PMlib.pyMatching.restype = ndpointer(dtype=ctypes.c_int, shape=(numNodes,))

# initialize ctypes array and fill with edge data
	nodes1=(ctypes.c_int*numEdges)();
	nodes2=(ctypes.c_int*numEdges)();
	weights=(ctypes.c_int*numEdges)();

	#c_int_array = ctypes.c_int*numEdges
	
#	nodes1 = c_int_array(*[graphArray[i][0] for i in range(numEdges)])


	for i in range(numEdges):
		nodes1[i]=graphArray[i][0]
		nodes2[i]=graphArray[i][1]
		weights[i]=graphArray[i][2]

	

#	mtime1 = time.time()
#	print "matching overhead = ", mtime1-mtime0

	result=PMlib.pyMatching(ctypes.c_int(numNodes),ctypes.c_int(numEdges),nodes1,nodes2,weights)

#	mtime2 = time.time()
#	print "matching time = ",mtime2 - mtime1
	return result






# pyInterface.o
# example.o
# misc.o
# PMduals.o
# PMexpand.o
# PMinit.o
# PMinterface.o
# PMmain.o
# PMrepair.o
# PMshrink.o
# MinCost/MinCost.o
# GEOM/GPMinit.o
# GEOM/GPMinterface.o
# GEOM/GPMkdtree.o
# GEOM/GPMmain.o 

#compile all these files as: 

# g++ -c -fPIC filename.cpp -lrt

# then compile all .o files into a shared library

# g++ -shared filename1.o filename2.o .... -o PMlib.so -lrt

# NOTE: the -lrt must come AFTER the filename
