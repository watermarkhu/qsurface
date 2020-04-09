DIRS := . MinCost GEOM 

SOURCES := $(foreach dir, $(DIRS), $(wildcard $(dir)/*.cpp)) # list of all cpp files
OBJS := $(patsubst %.cpp, %.o, $(SOURCES)) # creates a list of every cpp object with .cpp replaced with .o

#CFLAGS := -O3 -D_NDEBUG	# flags for .o compilation
CFLAGS:= -c -fPIC
CXX ?= icc		# cpp compiler
LIBS := -lrt
INCLUDES := 
LIBDIR := 

# Add librt if the target platform is not Darwin (OS X)
#ifneq ($(shell uname -s),Darwin)
#    LIBS += -lrt
#endif
 
all: PMlib.so

PMlib.so: ${OBJS}
	$(CXX) -shared ${OBJS} -o $@  ${LIBS}

#blossom5: ${OBJS}
#	$(CXX) $(CFLAGS) ${LIBDIR} -o $@ ${OBJS} ${LIBS}

.cpp.o:
	$(CXX) $(CFLAGS) ${INCLUDES} $< -o $@

clean:
	rm -f ${OBJS} blossom5
