import graph_2D as go
import random


class toric(go.toric):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.G = {}

        for z in range(1, self.size):
            self.init_graph_layer(z=z)

            for vU, vD in zip(self.S[z].values(), self.S[z-1].values()):
                bridge = self.G[vU.sID] = Bridge(gID=vU.sID)

                vU.neighbors["d"] = (vD, bridge.E)
                vD.neighbors["u"] = (vU, bridge.E)


    def __repr__(self):
        numC = 0
        for cluster in self.C.values():
            if cluster.parent == cluster:
                numC += 1
        numS = len([len(layer) for layer in self.S])
        numQ = len([len(layer) for layer in self.Q])
        numG = len(self.G)
        name = f"3D {self.type} graph object with: {numC} clusters, {numS} stabs, {numQ} qubits, {numG} bridges"
        return name

    '''
    ########################################################################################

                                    Surface code functions

    ########################################################################################
    '''


    def apply_and_measure_errors(self, pX, pZ, pE, pmX, pmZ, **kwargs):

        for z in self.range[:-1]:

            self.init_erasure(pE=pE, z=z)
            self.init_pauli(pX=pX, pZ=z)

        for z in self.range:
            self.measure_stab(pmX=pmX, pmZ=pmZ, z=z)


            print("\n",z)
            for vertex in self.S[z].values():
                print(vertex, vertex.state)


    def init_erasure(self, pE=0, z=0, **kwargs):
        """
        :param pE           probability of an erasure error
        :param savefile     toggle to save the errors to a file

        Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
        """

        if pE == 0:
            return

        for qubitu in self.Q[z].values():

            qubitd_states = [0,0] if z ==0 else [self.Q[z-1][qubitu.qID].E[n].state for n in range(1)]

            if random.random() < pE:
                qubitu.erasure = True
                rand = random.random()
                if rand < 0.25:
                    qubitu.E[0].state = 1 - qubitd_states[0]
                elif rand >= 0.25 and rand < 0.5:
                    qubitu.E[1].state = 1 - qubitd_states[1]
                elif rand >= 0.5 and rand < 0.75:
                    qubitu.E[0].state = 1 - qubitd_states[0]
                    qubitu.E[1].state = 1 - qubitd_states[1]


    def init_pauli(self, pX=0, pZ=0, z=0, **kwargs):
        """
        :param pX           probability of a Pauli X error
        :param pZ           probability of a Pauli Z error
        :param savefile     toggle to save the errors to a file

        initates Pauli X and Z errors on the lattice based on the error rates
        """

        if pX == 0 and pZ == 0:
            return

        for qubitu in self.Q[z].values():
            qubitd_states = [0,0] if z ==0 else [self.Q[z-1][qubitu.qID].E[n].state for n in range(1)]

            if pX != 0 and random.random() < pX:
                qubitu.E[0].state = 1 - qubitd_states[0]
            if pZ != 0 and random.random() < pZ:
                qubitu.E[1].state = 1 - qubitd_states[1]

    def measure_stab(self, pmX=0, pmZ=0, z=0, **kwargs):
        """
        The measurement outcomes of the stabilizers, which are the vertices on the self are saved to their corresponding vertex objects. We loop over all vertex objects and over their neighboring edge or qubit objects.
        """
        for stab in self.S[z].values():

            for vertex, edge in stab.neighbors.values():
                if edge.state:
                    stab.state = 1 - stab.state

            pM = pmX if stab.sID[0] == 0 else pmZ

            if pM != 0:

                if z != self.size - 1 and random.random() < pM:
                    stab.state = 1 - stab.state
                    stab.meas_error = 1

                stabd_state = 0 if z == 0 else self.S[z-1][stab.sID[:3]].meas_error
                if stabd_state:
                    stab.state = 1 - stab.state




    def logical_error(self):
        return super().logical_error(z=self.size-1)

    '''
    ########################################################################################

                                    Constructor functions

    ########################################################################################
    '''

    def reset(self):
        super().reset()
        for bridge in self.G.values():
            bridge.reset()


class planar(go.planar, toric):
    def __repr__(self):
        numC = 0
        for cluster in self.C.values():
            if cluster.parent == cluster:
                numC += 1
        numS = len([len(layer) for layer in self.S])
        numQ = len([len(layer) for layer in self.Q])
        numB = len([len(layer) for layer in self.B])
        numG = len(self.G)
        name = f"3D {self.type} graph object with: {numC} clusters, {numS} stabs, {numQ} qubits, {numB} boundaries, {numG} bridges"
        return name


class Bridge(object):
    def __init__(self, gID):

        self.qID = gID       # (td, y, x, z)
        self.erasure = 0
        self.E = go.Edge(self, ertype=gID[0], edge_type=1)

    def __repr__(self):
        return "g({},{},{}:{})".format(*self.gID[1:], self.gID[0])

    def reset(self):
        self.E.reset()
