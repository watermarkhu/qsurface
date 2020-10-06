DIRS := . MinCost GEOM 

SOURCES := $(foreach dir, $(DIRS), $(wildcard $(dir)/*.cpp)) # list of all cpp files
OBJS := $(patsubst %.cpp, %.o, $(SOURCES)) # creates a list of every cpp object with .cpp replaced with .o

CFLAGS:= -c -fPIC
CXX ?= icc		# cpp compiler
LIBS := -lrt
INCLUDES := 
LIBDIR := 
 
all: PMlib.so

PMlib.so: ${OBJS}
	$(CXX) -shared ${OBJS} -o $@  ${LIBS}

.cpp.o:
	$(CXX) $(CFLAGS) ${INCLUDES} $< -o $@

clean:
	rm -f ${OBJS} blossom5
