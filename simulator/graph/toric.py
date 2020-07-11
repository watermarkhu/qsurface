'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

We define the unit cell, which contains two qubits, a star operator and plaquette operator.

    |       |
- Star  -  Q_0 -     also top (T) qubit
    |       |
-  Q_1  - Plaq  -    also down (D) qubit
    |       |

Each cell is indicated by its y and x coordiantes. As such every qubit and stabilizer can by identified by a unique ID number:

Qubits: qID (td, y, x)          Stabilizers: sID (ertype, y, x)
    Q_0:    (0, y, x)               Star:   (0, y, x)
    Q_1:    (1, y, x)               Plaq:   (1, y, x)

The 2D graph (toric/planar) is a square lattice with 1 layer of these unit cells.
'''
import random 


class perfect_measurements(object):
    """
    The graph in which the vertices, edges and clusters exist. Has the following parameters

    size            1D size of the graph
    range           range over 1D that is often used
    decode_layer    z layer on which the qubits is decoded, 0 for 2D graph graph
    C               dict of clusters with
                        Key:    cID number
                        Value:  Cluster object
    S               dict of stabilizers with
                        Key:    sID number
                        Value:  Stab object
    Q               dict of qubits with
                        Key:    qID number
                        Value:  Qubit object with two Edge objects
    matching_weight total length of edges in the matching
    """

    def __init__(self, size, *args, dim=2, elements=None, benchmarker=None, primary_lattice=True, dual_lattice=True, **kwargs):
        self.dim = dim
        self.size = size
        self.range = range(size)
        self.decode_layer = 0
        self.AQ, self.DQ = {}, {}
        self.benchmarker = benchmarker
        self.primary_lattice = primary_lattice
        self.dual_lattice = dual_lattice

        if elements is None:
            from simulator.graph import elements_base as elements
        self.elements = elements
        
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.init_graph_layer()


    def __repr__(self):
        code = self.__module__.split(".")[-1]
        classname = self.__class__.__name__
        return f"{code} {self.size}x{self.size} graph with {classname}"


    def count_matching_weight(self, z=0):
        '''
        Loops through all qubits on the layer and counts the number of matchings edges
        '''
        weight = 0
        for qubit in self.DQ[z].values():
            if qubit.E[0].matching == 1:
                weight += 1
            if qubit.E[1].matching == 1:
                weight += 1
        return weight
    '''
    ########################################################################################

                                    Surface code functions

    ########################################################################################
    '''

    def init_graph_layer(self, z=0):
        '''
        param z     layer
        Initializes a layer of the graph structure of a toric lattice
        '''
        self.AQ[z], self.DQ[z] = {}, {}

        # Add edges to graph
        for y in self.range:
            for x in self.range:
                self.add_data_qubit(x+.5, y, z)
                self.add_data_qubit(x, y+.5, z)

        # Add stab objects to graph
        for y in self.range:
            for x in self.range:
                star = self.add_ancilla_qubit(x, y, z, 0)
                plaq = self.add_ancilla_qubit(x+.5, y+.5, z, 1)
                self.setup_parity(star)
                self.setup_parity(plaq)


    def measure_parity(self, z=0, **kwargs):
        """
        The measurement outcomes of the stabilizers, which are the vertices on the self are saved to their corresponding vertex objects.
        """
        for ancilla_qubit in self.AQ[z].values():
            ancilla_qubit.measure_parity()

    def logical_error(self, z=0, **kwargs):
        """
        Finds whether there are any logical errors on the lattice/self. The logical error is returned as [Xvertical, Xhorizontal, Zvertical, Zhorizontal], where each item represents a homological Loop
        """

        logical_error = [0, 0, 0, 0]

        for i in self.range:
            if self.DQ[z][(i+.5, 0)].E[0].state:
                logical_error[0] = 1 - logical_error[0]
            if self.DQ[z][(0, i+.5)].E[0].state:
                logical_error[1] = 1 - logical_error[1]
            if self.DQ[z][(i, .5)].E[1].state:
                logical_error[2] = 1 - logical_error[2]
            if self.DQ[z][(.5, i)].E[1].state:
                logical_error[3] = 1 - logical_error[3]

        no_error = True if logical_error == [0, 0, 0, 0] else False
        return logical_error, no_error

    '''
    ########################################################################################

                                    Constructor functions

    ########################################################################################
    '''

    def add_ancilla_qubit(self, x, y, z, ErrorType, **kwargs):
        """Adds a stabilizer with stab ID number sID"""
        ancilla_type = "star" if ErrorType == 0 else "plaq"
        ancilla = self.elements.Ancilla_qubit(loc=(x,y,z), Type=ancilla_type, ErrorType=ErrorType)
        self.AQ[z][(x,y)] = ancilla
        return ancilla

    def add_data_qubit(self,x,y,z, **kwargs):
        data_qubit = self.elements.Data_qubit(loc=(x,y,z))
        self.DQ[z][(x,y)] = data_qubit
        return data_qubit


    def setup_parity(self, ancilla_qubit, report_error=True, **kwargs):
        (x, y, z) = ancilla_qubit.loc

        def add_parity(key, direction):
            if key in self.DQ[z]:
                ancilla_qubit.add_parity_qubit(direction, self.DQ[z][key])
            elif report_error:
                raise KeyError("Data qubit not initiated")

        add_parity(((x + .5) % self.size, y), "e")
        add_parity(((x - .5) % self.size, y), "w")
        add_parity((x, (y + .5) % self.size), "n")
        add_parity((x, (y - .5) % self.size), "s")


    def reset(self):
        """
        Resets the graph by deleting all clusters and resetting the edges and vertices
        """
        for dlayer in self.DQ.values():
            for qubit in dlayer.values():
                qubit.reset()
        for alayer in self.AQ.values():
            for qubit in alayer.values():
                qubit.reset()


class faulty_measurements(perfect_measurements):

    def __init__(self, size, *args, **kwargs):
        super().__init__(size, *args, dim=3, **kwargs)
        self.decode_layer = self.size - 1
        self.VE = []

        for z in range(1, self.size):
            self.init_graph_layer(z=z)
            for upper in self.AQ[z].values():
                lower = self.AQ[z-1][upper.loc[:2]]
                self.add_vertical_edge(upper, lower)
                

    def add_vertical_edge(self, upperAncilla, lowerAncilla):
        vedge = self.elements.Edge(upperAncilla, lattice=upperAncilla.ErrorType, rep="|")
        self.VE.append(vedge)
        upperAncilla.add_vertical_ancilla("d", lowerAncilla, vedge)
        lowerAncilla.add_vertical_ancilla("u", upperAncilla, vedge)


    def count_matching_weight(self):
        '''
        Applies count_matching_weight() method of parent graph_2D object on each layer of the cubic lattice. Additionally counts the weight of the edges in the bridge objects present in the 3D graph.
        '''
        weight = 0
        for z in self.range:
            weight += super().count_matching_weight(z)
        for vedge in self.VE:
            if vedge.matching:
                weight += 1
        return weight

    def measure_parity(self, pmX=0, pmZ=0, z=0, **kwargs):
        """
        The measurement outcomes of the stabilizers, which are the vertices on the self are saved to their corresponding vertex objects.
        """
        for ancilla_qubit in self.AQ[z].values():
            ancilla_qubit.measure_parity()

            # Apply measurement error
            pM = pmX if ancilla_qubit.ErrorType == 0 else pmZ
            if pM != 0 and random.random() < pM:
                ancilla_qubit.state = 1 - ancilla_qubit.state
                ancilla_qubit.mstate = 1

            # Save vertex as anyon if parity different than previous layer
            if "d" in ancilla_qubit.vertical_qubits:
                lower_state = ancilla_qubit.vertical_qubits["d"][0].state
            else:
                lower_state = 0

            ancilla_qubit.state = 0 if ancilla_qubit.state == lower_state else 1

    def logical_error(self):
        '''
        Applies logical_error() method of parent graph_2D object on the last layer.
        '''
        return super().logical_error(z=self.size-1)

    def reset(self):
        '''
        Applies reset() method of parent graph_2D object. Also resets all the bridge objects present in the 3D graph.
        '''
        super().reset()
        for vedge in self.VE:
            vedge.reset()
