class Graph(object):
    '''
    The graph in which the vertices, edges and clusters exist. Has the following parameters

    C           dict of clusters with
                    Key:    cID number
                    Value:  Cluster object
    V           dict of vertices with
                    Key:    sID number
                    Value:  Vertex object
    E           dict of edges with
                    Key:    qID number
                    Value:  Edge object
    wind        dict keys from the possible directions of neighbors.

    '''

    def __init__(self, stab_data, er_loc, qua_loc):
        self.C = {}
        self.V = {}
        self.E = {}
        self.wind = ["u", "d", "l", "r"]

        self.cluster_index = []

    def __repr__(self):

        numC = 0
        for i, cID in enumerate(self.cluster_index):
            if i == cID:
                numC += 1
        return "Graph object with " + str(numC) + " Clusters, " + str(len(self.V)) + " Vertices and " + str(len(self.E)) + " Edges."

    def __len__(self):
        return len(self.C)

    def add_cluster(self, cID):
        '''Adds a cluster with cluster ID number cID'''
        self.C[cID] = Cluster(cID)
        return self.C[cID]

    def add_vertex(self, sID):
        '''Adds a vertex with vertex ID number sID'''
        self.V[sID] = Vertex(sID)
        return self.V[sID]

    def add_edge(self, qID, sIDlu, sIDrd, orientation):
        '''Adds an edge with edge ID number qID with pointers to vertices. Also adds pointers to this edge on the vertices. '''
        V1 = self.V[sIDlu]
        V2 = self.V[sIDrd]
        E = Edge(qID, V1, V2)
        self.E[qID] = E

        if orientation == 'H':
            V1.neighbors['r'] = (V2, E)
            V2.neighbors['l'] = (V1, E)
        elif orientation == 'V':
            V1.neighbors['d'] = (V2, E)
            V2.neighbors['u'] = (V1, E)
        return E

    def merge_clusters(self, bcID, scID):
        '''Merges two clusters'''

        self.C[bcID].merged.append(scID)
        self.C[scID].merged.append(bcID)

        self.C[bcID].merge_with(self.C[scID])
        self.C[scID].delete_atr()
        self.cluster_index[scID] = bcID

    def reset(self):
        '''
        Resets the graph by deleting all clusters and resetting the edges and vertices

        '''
        self.C = {}
        for edge in self.E.values():
            edge.reset()
        for vertex in self.V.values():
            vertex.reset()


class Cluster(object):
    '''
    Cluster obejct with parameters:
    cID         ID number of cluster
    V           dict of vertices contained within this cluster with
                    Key:    sID number
                    Value:  Vertex object
    E           dict of edges contained within this cluster with
                    Key:    qID number
                    Value:  Edge object
    B           dict of Boundary edges of this cluster with
                    Key:    Edge object
                    Value:  (base vertex object, grow vertex object)
    size        Size of this cluster based on the number contained vertices
    parity      Parity of this cluster based on the number of contained anyons
    merged      list of other clusters merged into this cluster
    '''

    def __init__(self, cID):
        # self.inf = {"cID": cID, "size": 0, "parity": 0}
        self.cID = cID
        self.size = 0
        self.parity = 0

        self.parent = self
        self.childs = []

        self.half_grown = False
        self.half_bound = []
        self.full_bound = []

    def __repr__(self):
        return "C" + str(self.cID)

    def add_vertex(self, vertex):
        '''Adds a vertex to a cluster. Also update cluster value of this vertex.'''
        self.size += 1
        if vertex.state:
            self.parity += 1
        vertex.cluster = self

    def add_edge(self, edge):
        '''Adds both sides of an edge to a cluster'''
        edge.cluster = self

    def add_full_bound(self, base_vertex, edge, grow_vertex):
        '''Add an edge to the boundary of the cluster'''
        self.full_bound.append((base_vertex, edge, grow_vertex))

    def merge_with(self, cluster):
        '''Updates this clusters attributes with anothers attributes'''
        self.parent = cluster
        cluster.childs.append(self)
        cluster.size += self.size
        cluster.parity += self.parity


class Vertex(object):
    '''
    Vertex object with parameters:
    sID         ID number of vertex
    neighbors   dict of the neighobrs (in the graph) of this vertex with
                    Key:    wind
                    Value   (Vertex object, Edge object)
    state       boolean indicating anyon state of vertex
    cluster     Cluster object of which this vertex is apart of
    tree        boolean indicating whether this vertex has been traversed
    '''

    def __init__(self, sID):
        # fixed paramters
        self.sID = sID
        self.neighbors = {}

        # iteration parameters
        self.state = False
        self.cluster = None
        self.tree = False

    def __repr__(self):
        type = "X" if self.sID[0] == 0 else "Z"
        return "v" + type + "(" + str(self.sID[1]) + "," + str(self.sID[2]) + ")"

    def reset(self):
        '''
        Changes all iteration paramters to their initial value
        '''
        self.state = False
        self.cluster = None
        self.tree = False


class Edge(object):
    '''
    Edge object with parameters:
    qID         ID number of qubit/edge
    vertices    tuple of the two conected vertices
    state       boolean indicating the state of the qubit
    cluster     Cluster object of which this edge is apart of
    tree        boolean indicating whether this edge has been traversed
    peeled      boolean indicating whether this edge has peeled
    matching    boolean indicating whether this edge is apart of the matching
    '''

    def __init__(self, qID, V1, V2):
        # fixed parameters
        self.qID = qID
        self.vertices = (V1, V2)

        # iteration parameters
        self.state = False
        self.erasure = False
        self.cluster = None
        self.peeled = False
        self.matching = False

    def __repr__(self):
        if self.qID[0] == 0:
            errortype = "X"
            edgetype = "-" if self.qID[3] == 0 else "|"
        else:
            errortype = "Z"
            edgetype = "|" if self.qID[3] == 0 else "-"
        return "e" + errortype + edgetype + "(" + str(self.qID[1]) + "," + str(self.qID[2]) + ")"

    def reset(self):
        '''
        Changes all iteration paramters to their initial value
        '''
        self.state = False
        self.erasure = False
        self.cluster = None
        self.peeled = False
        self.matching = False
