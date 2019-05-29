class Graph(object):
    '''
    :param stab_data        stab_data information tuple
    :param er_loc           list of qID of the erasure errors
    :param qua_loc          list of sID of the anyon locations    Graph obejct with parameters:

    C           Dict of clusters with
                    Key:    cID number
                    Value:  Cluster object
    V           Dict of vertices with
                    Key:    sID number
                    Value:  Vertex object
    E           Dict of edges with
                    Key:    qID number
                    Value:  Edge object

    '''

    def __init__(self, stab_data, er_loc, qua_loc):
        self.C = {}
        self.V = {}
        self.E = {}
        self.stab_data = stab_data
        self.er_loc = er_loc
        self.qua_loc = qua_loc
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

    def add_vertex(self, sID, y, x, anyon):
        '''Adds a vertex with vertex ID number sID'''
        self.V[sID] = Vertex(sID, y, x, anyon)

    def add_edge(self, qID, sID1, sID2):
        '''Adds an edge with edge ID number qID with pointers to vertices. Also adds pointers to this edge on the vertices. '''
        V1 = self.V[sID1]
        V2 = self.V[sID2]
        self.E[qID] = Edge(qID, V1, V2)

    def stab_add_neigbors(self, base_sID, cID):

        '''
        :param base_sID         ID number of the stab/vertex
        :param cID              ID number of the current cluster

        For a given sID vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph. If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, otherwise it will be added to the boundary. If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
        Newly found vertices that lie within the cluster are outputted to {new_stabs}.

        '''

        new_stabs = []

        for grow_sID, qID in zip(self.stab_data[base_sID][3], self.stab_data[base_sID][4]):

            if grow_sID not in self.V:
                anyon = True if grow_sID in self.qua_loc else False

                (y, x) = self.stab_data[grow_sID][1:3]
                self.add_vertex(grow_sID, y, x, anyon)
                self.add_edge(qID, base_sID, grow_sID)
            else:
                if qID not in self.E:
                    self.add_edge(qID, base_sID, grow_sID)

            if qID in self.er_loc:

                self.C[cID].add_edge(self.V[base_sID], self.V[grow_sID], self.E[qID])

                if grow_sID not in self.C[cID].V:
                    new_stabs.append(grow_sID)
                self.C[cID].add_vertex(self.V[grow_sID])

            else:
                self.C[cID].add_bound(self.V[base_sID], self.E[qID], self.V[grow_sID])

        return(new_stabs)

    def merge_clusters(self, bcID, scID):
        '''Merges two clusters'''

        self.C[bcID].merged.append(scID)
        self.C[scID].merged.append(bcID)

        self.C[bcID].merge_with(self.C[scID])
        self.C[scID].delete_atr()
        self.cluster_index[scID] = bcID

    def cluster_index_tree(self, cID):
        '''
        :param cID      input cluster index, can be a branch or a base of the tree
        Loops through the {cluster_index} tree to find the base cID of the cluster index tree.
        Returns: cID, must be the base of the cluster index tree
        '''

        if cID is not None:
            while cID != self.cluster_index[cID]:
                cID = self.cluster_index[cID]
        return cID



class Cluster(object):
    '''
    Cluster obejct with parameters:
    cID         ID number of cluster
    V           Dict of vertices contained within this cluster with
                    Key:    sID number
                    Value:  Vertex object
    E           Dict of edges contained within this cluster with
                    Key:    qID number
                    Value:  Edge object
    B           Dict of Boundary edges of this cluster with
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
        self.merged = [cID]
        self.V = {}         # Vertices
        self.E = {}         # Edges
        self.B = {}         # Boundary

    def __repr__(self):
        return "C" + str(self.cID)

    def __len__(self):
        return len(self.V)

    def add_vertex(self, vertex):
        '''Adds a vertex to a cluster. Also update cluster value of this vertex.'''
        if vertex.sID not in self.V:
            self.size += 1
            if vertex.anyon:
                self.parity += 1
        self.V[vertex.sID] = vertex
        vertex.cluster = self.cID

    def add_edge(self, vertex1, vertex2, edge):
        '''Adds both sides of an edge to a cluster'''
        self.E[edge.qID] = edge
        edge.cluster = self.cID
        edge.halves[vertex1] = self.cID
        edge.halves[vertex2] = self.cID
        vertex1.points_to[vertex2] = edge
        vertex2.points_to[vertex1] = edge

    def remove_edge(self, edge):
        CV = list(edge.halves.keys())
        del CV[0].points_to[CV[1]]
        del CV[1].points_to[CV[0]]
        del self.E[edge.qID]

    def add_bound(self, base_vertex, edge, grow_vertex):
        '''Add an edge to the boundary of the cluster'''
        self.B[edge] = (base_vertex, grow_vertex)

    def rem_bound(self, edge):
        '''Removes an edge to the boundary of the cluster'''
        del self.B[edge]

    def merge_with(self, cluster):
        '''Updates this clusters attributes with anothers attributes'''
        self.V.update(cluster.V)
        self.B.update(cluster.B)
        self.E.update(cluster.E)
        self.size += cluster.size
        self.parity += cluster.parity
    #
    # def inherit_atr_of(self, cluster):
    #     '''Links this clusters attributes to anothers attributes'''
    #     self.__dict__.update(cluster.__dict__)

    def delete_atr(self):
        del self.V
        del self.B
        del self.E



class Vertex(object):
    '''
    Vertex object with parameters:
    sID         ID number of vertex
    anyon       Boolean indicating anyon state of vertex
    cluster     Cluster object of which this vertex is apart of
    points_to   Dict of other connected vertices with
                    Key:    Vertex object
                    Value:  Edge object
    '''

    def __init__(self, sID, y, x, anyon):
        self.sID = sID
        self.loc = (y, x)
        self.anyon = anyon
        self.cluster = None
        self.points_to = {}
        self.tree = False

    def __repr__(self):
        return "V" + str(self.sID)


class Edge(object):
    '''
    Edge object with parameters:
    qID         ID number of qubit/edge
    halves      Dict of connected vertices with
                    Key:    Vertex object
                    Value:  Cluster cID
    tree        boolean: confirmed into the tree
    peeled      boolean: peeled this edge already
    '''

    def __init__(self, qID, V1, V2):
        self.qID = qID
        # self.halves = {V1.sID: Half_edge(V1), V2.sID: Half_edge(V2)}
        self.halves = {V1: None, V2: None}
        self.cluster = None
        self.tree = False
        self.peeled = False

    def __repr__(self):
        return "E" + str(self.qID)
