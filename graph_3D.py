'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
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

The 3D graph (toric/planar) is a cubic lattice with many layer of these unit cells.

'''

import graph_2D as go
import plot_graph_lattice as pgl
import plot_unionfind as puf
import random


class toric(go.toric):
    '''
    Inherits all the class variables and methods of graph_2D.toric

    Additions:
        G   dict of qubit-like objects called bridges containing the vertical edges connecting stabs of different layers
                Key:    sID number
                Value:  Stab object
    Replaces:
        init_uf_plot()
        apply_and_measure_errors()
        init_erasure()
        init_paul()
        measure_stab()
        logical_error()
        count_matching_weight()
        reset()

    3D graph is initilized by calling the init_graph_layer() method of the parent graph_2D.toric object.
    From here, we call that method size-1 times again, on each layer of the cubic lattice. Furthermore, qubit-like objects bridges containing vertical edges are added between the layers.
    Dim dimension is set to 3 and decoder_layer is set to last layer.
    '''

    def __init__(self, size, decoder, plot_config={}, dim=3, *args, **kwargs):

        plot2D = kwargs.pop("plot2D", 0)
        super().__init__(size, decoder, *args, plot2D=0, dim=3, **kwargs)

        self.dim = 3
        self.decode_layer = self.size - 1
        self.G = {}

        for z in range(1, self.size):
            self.init_graph_layer(z=z)
            self.G[z] = {}

            for vU, vD in zip(self.S[z].values(), self.S[z-1].values()):
                bridge = self.G[z][vU.sID] = Bridge(qID=vU.sID, z=z)

                vU.neighbors["d"] = (vD, bridge.E)
                vD.neighbors["u"] = (vU, bridge.E)


        for key, value in kwargs.items():
            setattr(self, key, value)
        self.plot2D = plot2D
        self.plot_config = plot_config
        self.gl_plot = pgl.plot_3D(self, **plot_config) if self.plot3D else None


    def init_uf_plot(self):
        self.uf_plot = puf.plot_3D(self, **self.plot_config)
        return self.uf_plot


    def __repr__(self):
        return f"3D {self.__class__.__name__} graph object"


    def count_matching_weight(self):
        '''
        Applies count_matching_weight() method of parent graph_2D object on each layer of the cubic lattice. Additionally counts the weight of the edges in the bridge objects present in the 3D graph.
        '''
        weight = 0
        for z in self.range:
            for qubit in self.Q[z].values():
                if qubit.E[0].matching == 1:
                    weight += 1
                if qubit.E[1].matching == 1:
                    weight += 1
        for layer in self.G.values():
            for bridge in layer.values():
                if bridge.E.matching:
                    weight += 1
        self.matching_weight.append(weight)

    '''
    ########################################################################################

                                    Surface code methods

    ########################################################################################
    '''


    def apply_and_measure_errors(self, pX, pZ, pE, pmX, pmZ, **kwargs):
        '''
        Initilizes errors on the qubits and measures the stabilizers on the graph on each layer of the cubic lattice.
        For the first size-1 layers, measurement errors are applied.
        For the final layer, perfect measurements are applied to ensure anyon creation.
        '''

        # first layers initilized with measurement error
        for z in self.range[:-1]:
            self.init_erasure(pE=pE, z=z)
            self.init_pauli(pX=pX, pZ=pZ, pE=pE, z=z)
            self.measure_stab(pmX=pmX, pmZ=pmZ, z=z)

        # final layer initialized with perfect measurements
        self.init_erasure(pE=pE, z=self.decode_layer)
        self.init_pauli(pX=pX, pZ=pZ, z=self.decode_layer)
        self.measure_stab(pmX=0, pmZ=0, z=self.decode_layer)

        if self.gl_plot:
            if pE != 0:
                for z in self.range:
                    self.gl_plot.plot_erasures(z, draw=False)
                self.gl_plot.draw_plot()
            for z in self.range:
                self.gl_plot.plot_errors(z, draw=False)
            self.gl_plot.draw_plot()
            for z in self.range:
                self.gl_plot.plot_syndrome(z)
            self.gl_plot.draw_plot()



    def init_erasure(self, pE=0, z=0, **kwargs):
        """
        Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
        Qubit states from previous layer are copied to this layer, whereafter erasure error is applied.
        """

        if pE == 0:
            return

        for qubitu in self.Q[z].values():

            # Get qubit state from previous layer
            if z != 0:
                qubitu.E[0].state, qubitu.E[1].state = (self.Q[z-1][qubitu.qID[:3]].E[n].state for n in range(2))

            # Apply errors
            if random.random() < pE:
                qubitu.erasure = 1
                rand = random.random()
                if rand < 0.25:
                    qubitu.E[0].state = 1 - qubitu.E[0].state
                elif rand >= 0.25 and rand < 0.5:
                    qubitu.E[1].state = 1 - qubitu.E[1].state
                elif rand >= 0.5 and rand < 0.75:
                    qubitu.E[0].state = 1 - qubitu.E[0].state
                    qubitu.E[1].state = 1 - qubitu.E[1].state


    def init_pauli(self, pX=0, pZ=0, pE=0, z=0, **kwargs):
        """
        initates Pauli X and Z errors on the lattice based on the error rates
        Qubit states from previous layer are copied to this layer, whereafter pauli error is applied.
        """

        if pX == 0 and pZ == 0:
            return

        for qubitu in self.Q[z].values():

            # Get qubit state from previous layer if not aleady done
            if pE == 0 and z != 0:
                qubitu.E[0].state, qubitu.E[1].state = (self.Q[z-1][qubitu.qID].E[n].state for n in [0, 1])

            # Apply errors
            if pX != 0 and random.random() < pX:
                qubitu.E[0].state = 1 - qubitu.E[0].state
            if pZ != 0 and random.random() < pZ:
                qubitu.E[1].state = 1 - qubitu.E[1].state


    def measure_stab(self, pmX=0, pmZ=0, z=0, **kwargs):
        """
        The measurement outcomes of the stabilizers, which are the vertices on the self are saved to their corresponding vertex objects.
        """

        for stab in self.S[z].values():

            # Get parity of stabilizer
            stab.parity = 0
            for dir in self.dirs:
                if dir in stab.neighbors:
                    vertex, edge = stab.neighbors[dir]
                    if edge.state:
                        stab.parity = 1 - stab.parity

            # Apply measurement error
            pM = pmX if stab.sID[0] == 0 else pmZ
            if pM != 0 and random.random() < pM:
                stab.parity = 1 - stab.parity
                stab.mstate = 1

            # Save vertex as anyon if parity different than previous layer
            stabd_state = 0 if z == 0 else self.S[z-1][stab.sID[:3]].parity
            stab.state = 0 if stabd_state == stab.parity else 1


    def logical_error(self):
        '''
        Applies logical_error() method of parent graph_2D object on the last layer.
        '''
        if self.plot2D:
            self.gl2_plot = pgl.plot_2D(self, z=self.decode_layer, from3D=1, **self.plot_config)
            self.gl2_plot.new_iter("Final layer errors")
            self.gl2_plot.plot_errors(z=self.decode_layer, draw=1)
        return super().logical_error(z=self.size-1)

    '''
    ########################################################################################

                                    Constructor methods

    ########################################################################################
    '''

    def reset(self):
        '''
        Applies reset() method of parent graph_2D object. Also resets all the bridge objects present in the 3D graph.
        '''
        super().reset()
        for layer in self.G.values():
            for bridge in layer.values():
                bridge.reset()

'''
########################################################################################

                                        Planar class

########################################################################################
'''

class planar(toric, go.planar):
    '''
    Inherits all the calss variables and methods of graph_3D.toric and graph_3D.planar.

    graph_3D.planar -> graph_3D.toric -> graph_2D.planar -> graph_2D.toric

    All super().def() methods in graph_3D.toric now call on graph_2D.planar, such that the planar structure is preserved.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

'''
########################################################################################

                            Subclasses: Graph objects

########################################################################################
'''

class Bridge(object):
    '''
    Qubit-like object that contains a single vertical Edge object that connects Stabs between different layers in the cubic lattice.

    qID         (td, y, x)
    z           layer of graph to which this stab belongs
    E           list countaining the two edges of the primal and secundary lattice
    erasure     placeholder to ensure decoder works
    '''
    def __init__(self, qID, z=0):
        self.qID = qID       # (ertype, y, x)
        self.z = z
        self.erasure = 0
        self.E = go.Edge(self, ertype=qID[0], edge_type=1, z=z)

    def __repr__(self):
        errortype = "X" if self.qID[0] == 0 else "Z"
        return "g{}({},{}:{})".format(errortype, *self.qID[1:], self.z)

    def picker(self):
        return self.__repr__()

    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.E.reset()
