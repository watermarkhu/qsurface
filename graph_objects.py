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
        self.wind = ("u", "d", "l", "r")

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

    def add_vertex(self, sID):
        '''Adds a vertex with vertex ID number sID'''
        self.V[sID] = Vertex(sID)

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

    def cluster_new_vertex(self, cID, vertex):

        '''
        :param vertex           vertex that is recently added to the cluster
        :param cID              ID number of the current cluster

        For a given sID vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph. If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, otherwise it will be added to the boundary. If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
        Newly found vertices that lie within the cluster are outputted to {new_stabs}.

        '''

        cluster = self.C[cID]
        new_vertices = []

        for wind in self.wind:
            if wind in vertex.neighbors:
                (new_vertex, new_edge) = vertex.neighbors[wind]
                if new_edge.erasure:
                    cluster.add_edge(vertex, new_vertex, new_edge)
                    if new_vertex.sID not in cluster.V:
                        cluster.add_vertex(new_vertex)
                        new_vertices.append(new_vertex)
                else:
                    if new_edge.erasure:
                        cluster.add_edge(vertex, new_vertex, new_edge)
                        cluster.add_vertex(new_vertex)
                        new_vertices += self.cluster_new_vertex(cID, new_vertex)
                    else:
                        cluster.add_bound(vertex, new_edge, new_vertex)


        return new_vertices


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

    def reset(self):
        self.C = {}
        for edge in self.E.values():
            edge.reset()
        for vertex in self.V.values():
            vertex.reset()



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
            if vertex.state:
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

    def __init__(self, sID):
        # fixed paramters
        self.sID = sID
        self.neighbors = {}

        # iteration parameters
        self.state = False
        self.cluster = None
        self.points_to = {}
        self.tree = False

    def __repr__(self):
        type = "X" if self.sID[0] == 0 else "Z"
        return "v" + type + str(self.sID[1:])

    def reset(self):
        self.state = False
        self.cluster = None
        self.points_to = {}
        self.tree = False


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
        # fixed parameters
        self.qID = qID
        self.vertices = (V1, V2)

        # iteration parameters
        self.state = False
        self.erasure = False
        self.halves = {V1: None, V2: None}
        self.cluster = None
        self.tree = False
        self.peeled = False
        self.matching = False

    def __repr__(self):
        if self.qID[0] == 0:
            errortype = "X"
            edgetype = "-" if self.qID[3] == 0 else "|"
        else:
            errortype = "Z"
            edgetype = "|" if self.qID[3] == 0 else "-"
        return "e" + errortype + edgetype + str(self.qID[1:3])

    def reset(self):
        self.state = False
        self.erasure = False
        self.halves[self.vertices[0]] = None
        self.halves[self.vertices[1]] = None
        self.cluster = None
        self.tree = False
        self.peeled = False
        self.matching = False


class minbidict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inverse = {}
        self.seclist = {}
        self.minlist = []
        self.min_ind = -1

        for key, value in self.items():
            self.inverse.setdefault(value, []).append(key)
            self.seclist.__setitem__(key, True)
            if self.minlist != []:
                self.insert_value(value)
            else:
                self.minlist = [value]

    def __setitem__(self, key, value):
        if key in self:
            if self[key] == self.minlist[-1]:
                self.minlist.pop()
            else:
                print("Not minimal value selected")
            self.inverse[self[key]].remove(key)
            if self.inverse[self[key]] == []:
                del self.inverse[self[key]]

        self.insert_value(value)

        super().__setitem__(key, value)
        self.inverse.setdefault(value, []).append(key)

    def __delitem__(self, key):
        value = self[key]
        if value == self.minlist[-1]:
            self.minlist.pop()
        else:
            print("Not minimal value selected")

        self.inverse.setdefault(self[key], []).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super().__delitem__(key)

    def min_keys(self):


        min_val = self.minlist[self.min_ind]
        while min_val not in self.inverse:
            self.minlist.pop(self.min_ind)
            min_val = self.minlist[self.min_ind]

        return self.inverse[min_val]

    def insert_value(self, value):
        if value <= self.minlist[-1]:
            self.minlist.append(value)
        elif value >= self.minlist[0]:
            self.minlist.insert(0, value)
        else:
            ma = self.minlist[0]
            mi = self.minlist[-1]
            pos_ind = len(self.minlist) - 1

            ind = pos_ind - round((value - mi + 1)/(ma - mi)*pos_ind) + 1
            self.minlist.insert(ind, value)
