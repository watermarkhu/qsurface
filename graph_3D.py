import graph_2D as go
import plot_graph_lattice as pgl
import plot_unionfind as puf
import random


class toric(go.toric):

    def __init__(self, size, decoder, plot2D, plot3D=0, plot_config={}, *args, **kwargs):
        super().__init__(size, decoder, *args, **kwargs)

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

        self.plot2D = plot2D
        self.plot_config = plot_config
        self.gl_plot = pgl.plot_3D(self, **plot_config) if plot3D else None

    def init_uf_plot(self):

        self.uf_plot = puf.plot_3D(self, **self.plot_config)
        return self.uf_plot

    def __repr__(self):
        return f"3D {self.__class__.__name__} graph object"

    '''
    ########################################################################################

                                    Surface code functions

    ########################################################################################
    '''


    def apply_and_measure_errors(self, pX, pZ, pE, pmX, pmZ, **kwargs):

        for z in self.range[:-1]:

            self.init_erasure(pE=pE, z=z)
            self.init_pauli(pX=pX, pZ=pZ, pE=pE, z=z)
            self.measure_stab(pmX=pmX, pmZ=pmZ, z=z)

        self.init_erasure(pE=pE, z=self.decode_layer)
        self.init_pauli(pX=pX, pZ=pZ, z=self.decode_layer)
        self.measure_stab(pmX=0, pmZ=0, z=self.decode_layer)

        if self.gl_plot:

            for z in self.range:
                self.gl_plot.plot_erasures(z)
                self.gl_plot.plot_errors(z)
                self.gl_plot.plot_syndrome(z)

            self.gl_plot.draw_plot("Errors and syndromes plotted")


    def init_erasure(self, pE=0, z=0, **kwargs):
        """
        :param pE           probability of an erasure error
        :param savefile     toggle to save the errors to a file

        Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
        """

        if pE == 0:
            return

        for qubitu in self.Q[z].values():

            qubitu.E[0].state, qubitu.E[1].state = (0,0) if z == 0 else (self.Q[z-1][qubitu.qID[:3]].E[n].state for n in range(2))

            if random.random() < pE:
                qubitu.erasure = True
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
        :param pX           probability of a Pauli X error
        :param pZ           probability of a Pauli Z error
        :param savefile     toggle to save the errors to a file

        initates Pauli X and Z errors on the lattice based on the error rates
        """

        if pX == 0 and pZ == 0:
            return

        for qubitu in self.Q[z].values():

            if pE == 0:
                qubitu.E[0].state, qubitu.E[1].state = (0,0) if z == 0 else (self.Q[z-1][qubitu.qID].E[n].state for n in [0, 1])

            if pX != 0 and random.random() < pX:
                qubitu.E[0].state = 1 - qubitu.E[0].state
            if pZ != 0 and random.random() < pZ:
                qubitu.E[1].state = 1 - qubitu.E[1].state


    def measure_stab(self, pmX=0, pmZ=0, z=0, **kwargs):
        """
        The measurement outcomes of the stabilizers, which are the vertices on the self are saved to their corresponding vertex objects. We loop over all vertex objects and over their neighboring edge or qubit objects.
        """

        for stab in self.S[z].values():

            stab.parity = 0
            for dir in self.dirs:
                if dir in stab.neighbors:
                    vertex, edge = stab.neighbors[dir]
                    if edge.state:
                        stab.parity = 1 - stab.parity

            pM = pmX if stab.sID[0] == 0 else pmZ
            if pM != 0 and random.random() < pM:
                stab.parity = 1 - stab.parity
                stab.mstate = 1

            stabd_state = 0 if z == 0 else self.S[z-1][stab.sID[:3]].parity
            stab.state = 0 if stabd_state == stab.parity else 1


    def logical_error(self):
        '''
        Plots a 2D lattice if specified
        Finds logical error on the last (most recent) z layer
        '''
        if self.plot2D:
            fp = pgl.plot_2D(self, z=self.decode_layer, **self.plot_config)
            fp.plot_errors(z=self.decode_layer)
            self.measure_stab(pmX=0, pmZ=0, z=self.decode_layer)
            fp.plot_syndrome(z=self.decode_layer)
        return super().logical_error(z=self.size-1)


    def count_matching_weight(self):
        '''
        Loops through all qubits on the layer and counts the number of matchings edges
        '''
        for z in self.range:
            super().count_matching_weight(z=z)
        for layer in self.G.values():
            for bridge in layer.values():
                if bridge.E.matching:
                    self.matching_weight += 1

    '''
    ########################################################################################

                                    Constructor functions

    ########################################################################################
    '''

    def reset(self):
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

'''
########################################################################################

                            Subclasses: Graph objects

########################################################################################
'''

class Bridge(object):
    def __init__(self, qID, z=0):

        self.qID = qID       # (ertype, y, x)
        self.z = z
        self.erasure = 0
        self.E = go.Edge(self, ertype=qID[0], edge_type=1, z=z)

    def __repr__(self):
        return "g({},{},{}:{})".format(*self.qID[1:], self.qID[0])

    def reset(self):
        self.E.reset()
