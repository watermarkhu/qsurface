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

    def __init__(self, size, *args, dim=2, elements=None, benchmarker=None, **kwargs):
        self.dim = dim
        self.size = size
        self.range = range(size)
        self.decode_layer = 0
        self.AQ, self.DQ = {}, {}
        self.benchmarker = benchmarker

        if elements is None:
            from simulator.graph import elements_base as elements
        self.elements = elements
        
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.init_graph_layer()


    def __repr__(self):
        return f"{self.__module__.__name__} {self.__class__.__name__}"


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

    def add_ancilla_qubit(self, x, y, z, EID, **kwargs):
        """Adds a stabilizer with stab ID number sID"""
        ancilla_type = "star" if EID == 0 else "plaq"
        ancilla = self.elements.Ancilla_qubit(loc=(x,y,z), Type=ancilla_type, EID=EID)
        self.AQ[z][(x,y)] = ancilla
        return ancilla

    def add_data_qubit(self,x,y,z, **kwargs):
        data_qubit = self.elements.Data_qubit(loc=(x,y,z))
        self.DQ[z][(x,y)] = data_qubit
        return data_qubit

    def setup_parity(self, ancilla_qubit, **kwargs):
        (x, y, z) = ancilla_qubit.loc
        ancilla_qubit.add_parity_qubit("e", self.DQ[z][((x + .5) % self.size, y)])
        ancilla_qubit.add_parity_qubit("w", self.DQ[z][((x - .5) % self.size, y)])
        ancilla_qubit.add_parity_qubit("n", self.DQ[z][(x, (y + .5) % self.size)])
        ancilla_qubit.add_parity_qubit("s", self.DQ[z][(x, (y - .5) % self.size)])


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


# %%
