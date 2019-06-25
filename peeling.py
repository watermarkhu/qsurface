from peeling_plot import toric_peeling_plot as tpplot
import graph_objects as G


class toric:
    def __init__(self, lat):
        '''
        :param size             size of the lattice
        :param qua_loc          tuple of anyon locations (y,x)
        :param erasures         tuple of all the erased qubits (td, y, x)
        :init_edge_data         tuple of edge neighbor and anyon data, see init_edge_data

        Optionally, the edge_data, which contains the neighbors information, can be loaded here.
        During loops, this has benefits to the computation time
        '''

        self.size = lat.size
        # self.qua_loc = lat.qua_loc
        # self.er_loc = lat.er_loc
        # self.edge_data = lat.edge_data
        # self.vertex_data = lat.vertex_data
        # self.num_vertex = lat.num_vertex
        # self.num_qubit = lat.num_qubit

        self.G = lat.G

        self.plot_load = lat.plot_load
        self.plotstep_grow = False
        self.plotstep_tree = False
        self.plotstep_peel = False
        self.plotstep_click = True


        if self.plot_load:
            self.pl = tpplot(lat, lat.LP.f, self.plotstep_peel, self.plotstep_click)
            self.pl.plot_lattice()


    '''
    Main functions
    '''
    def gettuple_edge(self, id):
        '''
        Gets the location of an edge (td, y, x) in tuple form
        '''
        y  = self.qubit_data[id][1]
        x  = self.qubit_data[id][2]
        td = self.qubit_data[id][3]
        return (y, x, td)


    def get_neighbors_id_tree(self, id, inlist, outlist):
        '''
        finds the neighbors of a vertex within the cluster, and not yet added to the trees
        '''
        n1 = self.qubit_data[id][5]
        n2 = self.qubit_data[id][7]
        cn1 = [cn for cn in n1 if cn in inlist and cn not in outlist]
        cn2 = [cn for cn in n2 if cn in inlist and cn not in outlist]
        return (cn1, cn2)


    def get_anyons_id(self, id):
        '''
        finds the two anyons/quasiparticles/vertices that are located on either sides of the edge
        '''
        a1 = self.qubit_data[id][8]
        a2 = self.qubit_data[id][9]
        return (a1, a2)

    def walk_leaf_tree(self, edges, cluster):
        '''
        :param edges            list of edges to walk over
        :param cluster          the current cluster to walk in
        This function walks over the pendant leafs from the list of edges that are within the cluster
        All leafs (edges that are not in a cycle) are stored in the self.e_tree list
        '''

        for edge in edges:
            if edge not in self.e_tree:

                # find neighbor of edge
                cn1, cn2 = self.get_neighbors_id_tree(edge, cluster, self.e_tree)

                # if edge is an ending branch, add to tree
                if cn1 == [] or cn2 == []:

                    # get branch body
                    cn = cn2 if cn1 == [] else cn1
                    old_e = edge

                    # find entire body of current branch, add to tree, and stop at bisection
                    while len(cn) == 1:
                        new_e = cn[0]
                        cn1, cn2 = self.get_neighbors_id_tree(new_e, cluster, self.e_tree)
                        cn = cn2 if old_e in cn1 else cn1
                        self.e_tree.append(old_e)
                        if self.plotstep_tree: self.pl.plot_tree_step(old_e)
                        old_e = new_e
                    else:
                        self.e_tree.append(old_e)
                        if self.plotstep_tree: self.pl.plot_tree_step(old_e)

    def walk_cycle_random(self, edge, cluster):
        '''
        :param edge         randomly chosen edge that is in a cycle
        :param cluster      the list of edges of the current cluster
        This function does a random walk over the edges in a cluster that are in cycles
        when it encounters an edge that it has already walked over, a cycle is detected and stored
        '''
        this_cycle = [edge]
        old_e = edge
        cn1, cn2 = self.get_neighbors_id_tree(edge, cluster, self.e_tree)
        cn = cn1 if random.random() < 0.5 else cn2
        while all([e not in this_cycle for e in cn]):
            new_e = cn[random.randint(0, len(cn) - 1)]
            this_cycle.append(new_e)
            cn1, cn2 = self.get_neighbors_id_tree(new_e, cluster, self.e_tree)
            cn = cn2 if old_e in cn1 else cn1
            old_e = new_e
        else:
            begin = [e for e in this_cycle if e in cn][-1]
            cut_cycle = this_cycle[this_cycle.index(begin):]
        return cut_cycle

    def walk_cycle_graph(self, eA, cluster):
        '''
        :param edge         randomly chose edge that is in a cycle
        :param clusters     the list of edges of the currect cluster
        This function makes a graph of all possible paths or branches, starting from the initial edge
        The branches are stored in a list named graph as:
            [edge, parent]
        where edge indicateds the edge id, and the parent points to the index of the previous branch in the graph
        for example:
             ..__ __..
               3  4
        is stored as [..[3, some parent],[4, 3]..]
        When a cycle is detected (the initial edge is encounted as a branch), we walk the graph from bottom to top to get the cycle
        '''

        eAn1, eAn2 = self.get_neighbors_id_tree(eA, cluster, self.e_tree)

        cA = eAn2
        eB = eAn1[0]

        eBn1, eBn2 = self.get_neighbors_id_tree(eB, cluster, self.e_tree)

        cB = eBn2 if eA in eBn1 else eBn1

        graphA = [(eA, None)]
        graphB = [(eB, None)]
        branchesA = [(e, 0) for e in cA]
        branchesB = [(e, 0) for e in cB]
        iA = 1
        iB = 1

        found_cycle = False

        while found_cycle == False:

            nodeA = []
            new_branchesA = []
            new_branchesB = []

            for branch, parent in branchesA:

                graphA.append((branch, parent))


                c1, c2 = self.get_neighbors_id_tree(branch, cluster, self.e_tree)
                a1, a2 = self.get_anyons_id(branch)

                if graphA[parent][0] in c1:
                    children = c2
                    node = a2
                else:
                    children = c1
                    node = a1

                new_branchesA += [(child, iA) for child in children]
                iA += 1
                nodeA.append(a1)

            print("A", graphA)


            for branch, parent in branchesB:

                graphB.append((branch, parent))

                c1, c2 = self.get_neighbors_id_tree(branch, cluster, self.e_tree)
                a1, a2 = self.get_anyons_id(branch)
                if graphB[parent][0] in c1:
                    children = c2
                    node = a2
                else:
                    children = c1
                    node = a1

                if node in nodeA:



                    cycle = [branch]
                    while parent != None:
                        branch = graphB[parent][0]
                        parent = graphB[parent][1]
                        cycle.append(branch)

                    (branch, parent) = branchesA[nodeA.index(node)]
                    cycle.append(branch)
                    while parent != None:
                        branch = graphA[parent][0]
                        parent = graphA[parent][1]
                        cycle.append(branch)

                    found_cycle = True
                    print(cycle)
                    input()
                    break

                new_branchesB += [(child, iB) for child in children]
                iB += 1

            print("B", graphB)
            input()

            branchesA = new_branchesA
            branchesB = new_branchesB


        return cycle

    def stab_get_neighbor_CL(self, sID, inlist, outlist, qua_loc):
        '''
        :param sID          ID number of the stab/vertex
        :param inlist       list of edges that the neighbors are allowed to be in
        :param outlist      list of edges that the neighbors are not allowed to be in
        :param qua_loc      list of anyon locations

        CL for cluster; neighbor function for cluster search

        For a given sID vertex, this function finds the neighboring edges that are in the inlist (for example the cluster) and that are not in the outlist (for example edges that have already been added to the cluster). {cluster_edges}
        {new_stabs} contains the connected vertices at the ends of these allowed edges.
        If any of these allowed vertices is an anyon, it will be outputted in {in_anyons}.
        If this specific sID vertex lies on the boundary of set inlist, {boundary} is outputted as true.

        '''
        stab_edges = self.stab_data[sID][4]                             # edges connected to this stabilizer/vertex
        new_edges = [e for e in stab_edges if e not in outlist]         # edges that are not yet walked over from outlist
        cluster_edges = [e for e in new_edges if e in inlist]           # edges that are within the given cluster/inlist

        new_stabs = []                                                  # get new stab/vertex location
        for qID in cluster_edges:
            s1 = self.qubit_data[qID][8]
            s2 = self.qubit_data[qID][9]
            if s1 == sID:
                new_stabs.append(s2)
            else:
                new_stabs.append(s1)

        in_anyons = [a for a in new_stabs if a in qua_loc]              # find out if vertices are anyons

        boundary = True if len(new_edges) > len(cluster_edges) else False   # Find out if new vertices are on the boundary

        return (cluster_edges, new_stabs, in_anyons, boundary)

    def print_graph_stop(self, cID=None, prestring=""):
        '''
        :param cID          either None, int or a list of int
        :param prestring    string to print before evertything else

        This function prints a clusters with its vertices, edges and boundary. A prestring is printed before printing everything else.
        Three different inputs can be given, to select for which clusters to print:
        1.  None:       All active clusters are printed
        2.  int:        Just one clusters with cID = int is printed
        3.  list:       The list of clusters with cID in the list are printed
        '''

        if type(cID) == int:
            cID = [cID]
        elif cID is None:
            cID = list(self.G.C.keys())

        for cid in cID:
            if prestring != "":
                print(prestring)

            if self.G.cluster_index[cid] == cid:
                print("Cluster", str(cid) + " (" + str(self.G.C[cid].cID) + ")", "with size: " + str(self.G.C[cid].size) + " and parity: " + str(self.G.C[cid].parity))
                print("V: ", list(self.G.C[cid].V.keys()))
                print("E: ", list(self.G.C[cid].E.keys()))
                print("B: ", list(self.G.C[cid].B.values()), "\n")
            else:
                if len(cID) == 1:
                    print("Cluster", str(cid), "is merged with", str(self.G.cluster_index_tree(cid)), "\n")


    def find_clusters(self):
        '''
        Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected and sorts them in separate clusters. A single anyon can also be its own cluster.

        - A graph object is initated
        - For each anyon that is not yet in a cluster:
            - initiate a cluster
            - add anyon vertex to cluster
            - find neighbors of anyon on edges that are eraures and add to cluster
            - while new neighbors are found:
                - add neighbors to clusters, find 2nd generation neighbors as new neighbors

        '''

        cID = 0

        for vertex in self.G.V.values():
            if vertex.state and vertex.cluster is None:

                self.G.add_cluster(cID)

                self.G.C[cID].add_vertex(vertex)

                round_new_vertices = self.G.cluster_new_vertex(cID, vertex)

                while not round_new_vertices == []:
                    new_vertices = []

                    for vertex in round_new_vertices:
                        new_vertices += self.G.cluster_new_vertex(cID, vertex)

                    round_new_vertices = new_vertices
                cID += 1

        self.G.cluster_index = [i for i in range(cID)]

    def select_growth_clusters(self):

        '''
        Select which clusters are valid for growth. All uneven clusters can be grown
        {weighted_growth} toggles the selection of only the smallers uneven clusters for growth.
        Returns: boolean list of N_clusters
        '''

        weighted_growth = True

        grow_cID = []
        grow_size = []


        for cID, parentcID in enumerate(self.G.cluster_index):
            if cID == parentcID:
                cluster = self.G.C[cID]

                if cluster.parity % 2 == 1:
                    grow_cID.append(cID)
                    grow_size.append(cluster.size)

        if weighted_growth:
            if grow_cID != []:
                minsize = min(grow_size)
                grow_cID = [cID for cID, size in zip(grow_cID, grow_size) if size == minsize]


        return grow_cID

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

    def grow_clusters(self):
        '''
        Clusters needs te be grown and merged until there are no uneven clusters left.
        The grow_clusters algorithm can be split into 5 steps:

        -   For each clusters selected for growth:
            - For each boundary on this cluster:

                1.  First half step growth:
                -   From the boundary of the cluster, grow edges by half
                -   If the other edge-half is from another cluster:
                    - append this boundary edge/cluster to {rem_list}
                    - append these two clusters to {merge_list}

                2.  Second half step growth:
                -   Continue from the boundary that is already grown in step 1, grow edges by another half
                -   Add this boundary edge to the clusters
                -   If this boundary vertex is 'free', not belonging to a cluster:
                    -   Add this vertex to the cluster
                    -   append this boundary edge/cluster to {new_bounds}
                    Else:
                    -   append these two clusters to {merge_list}

                3.  Remove merged boundaries from merge actions of first half step grown
                    - Remove boundary from both clusters

                4.  Remove old boundaries and add new boundaries for fully grown edges from second half step
                    - Remove old boundary
                    - Add new boundary

                5.  Merging clusters
                    - Find main cluster from {merge_list}
                    - Merge smaller clusters onto bigger clustter
        '''

        print_steps = False


        if print_steps:
            self.print_graph_stop()
            input()


        grow_id = self.select_growth_clusters()

        while grow_id != []:

            if print_steps:
                print("\n############################ GROW ############################ \nGrowing clusters:", grow_id, "\n")

            merge_list = []

            for cID in grow_id:

                cluster = self.G.C[cID]

                rem_bounds = []
                new_bounds = []

                if print_steps:
                    print("Growing:")
                    self.print_graph_stop(cID)

                for (edge, (base_vertex, grow_vertex)) in cluster.B.items():

                    base_cluster_cID = edge.halves[base_vertex]
                    grow_cluster_cID = edge.halves[grow_vertex]

                    if base_cluster_cID is None:
                        '''
                        1.  First half step growth:
                        '''

                        edge.halves[base_vertex] = cluster.cID

                        if self.plot_load:
                            self.pl.add_edge(edge)

                        if grow_cluster_cID is not None:

                            grow_cluster = self.G.C[self.G.cluster_index_tree(grow_cluster_cID)]

                            cluster.E[edge.qID] = edge
                            edge.cluster = cluster.cID
                            base_vertex.points_to[grow_vertex] = edge
                            grow_vertex.points_to[base_vertex] = edge

                            if grow_cluster is not cluster:

                                rem_bounds.append((edge, cluster, grow_cluster))

                                if cluster.size >= grow_cluster.size:
                                    merge_list.append((cID, grow_cluster.cID))
                                else:
                                    merge_list.append((grow_cluster.cID, cID))

                    else:
                        '''
                        2.  Second half step growth:
                        '''

                        cluster.E[edge.qID] = edge
                        edge.cluster = cluster.cID
                        edge.halves[grow_vertex] = cluster.cID
                        base_vertex.points_to[grow_vertex] = edge
                        grow_vertex.points_to[base_vertex] = edge

                        if self.plot_load:
                            self.pl.add_edge(edge)

                        if grow_vertex.cluster is None:

                            cluster.add_vertex(grow_vertex)

                            new_bounds.append((edge, grow_vertex))

                        else:

                            grow_cluster = self.G.C[self.G.cluster_index_tree(grow_vertex.cluster)]

                            if grow_cluster is not cluster:

                                if cluster.size >= grow_cluster.size:
                                    merge_list.append((cID, grow_cluster.cID))
                                else:
                                    merge_list.append((grow_cluster.cID, cID))

                '''
                3.  Remove merged boundaries from merge actions of step 1
                '''
                for edge, clusterA, clusterB in rem_bounds:

                    clusterA.rem_bound(edge)
                    clusterB.rem_bound(edge)

                '''
                4.  Remove old boundaries and add new boundaries for fully grown edges
                '''

                for edge, grow_vertex in new_bounds:

                    cluster.rem_bound(edge)
                    self.G.cluster_new_vertex(cID, grow_vertex)

                if self.plot_load and self.plotstep_grow:
                    self.pl.draw_plot("Cluster " + str(cID) + " grown.")


            if self.plot_load and not self.plotstep_grow:
                self.pl.draw_plot("Round of cluster growth.")
                if print_steps:
                    input()

            if print_steps:
                print("\n############################  MERGING ############################  \nMerging clusters: ", set(merge_list), "\n")

            '''
            5.  Merging clusters
            '''

            for (bcID, scID) in set(merge_list):

                BCID = self.G.cluster_index_tree(bcID)
                SCID = self.G.cluster_index_tree(scID)

                if SCID not in self.G.C[BCID].merged:

                    self.G.merge_clusters(BCID, SCID)

                    if print_steps:
                        print("merged: " + str(SCID) + " with " + str(BCID))
                        self.print_graph_stop(BCID)
                else:
                    if print_steps:
                        print("Already merged " + str(scID) + " with " + str(bcID), "\n")


            if print_steps:
                input()
                print("All clusters:\n")
                self.print_graph_stop()
                input()

            grow_id = self.select_growth_clusters()


    def init_trees(self):

        '''
        Makes trees from clusters.
        Within the clusters there are possibly cycles of the edges
        The peeling algorithm requires that all cycles are broken such that the cluster is a tree-like structure
        For example:
         _
        |_|     ->      |_|

        Here we apply a Breath-first search algorithm to traverse the tree.

        -   For each valid cluster
            -   From the first vertex is new node:
            -   While there are new nodes:
                -   Find neighboring edges and nodes
                -   If node is already in the tree:
                    -   Remove edge from cluster
                    Else:
                    -   add edge and node to tree, node is part of new nodes

        '''

        self.grown_clusters = [i for i, cID in enumerate(self.G.cluster_index) if i == cID]

        for cID in self.grown_clusters:

            cluster = self.G.C[cID]

            first_vertex = list(cluster.V.values())[0]

            first_vertex.tree = True

            new_vertices = [first_vertex]

            while new_vertices != []:

                neighbor_vertices = []

                for vertex in new_vertices:

                    neighbors = [(V, E) for V, E in vertex.points_to.items() if E.qID in cluster.E and not E.tree]

                    for vertex, edge in neighbors:

                        if vertex.tree:

                            cluster.remove_edge(edge)
                            edge.peeled = True

                            if self.plot_load and self.plotstep_tree:
                                self.pl.plot_edge_step(edge, "remove")

                        else:

                            vertex.tree = True
                            edge.tree = True
                            neighbor_vertices.append(vertex)

                            if self.plot_load and self.plotstep_tree:
                                self.pl.plot_edge_step(edge, "tree")

                new_vertices = neighbor_vertices

        if self.plot_load and not self.plotstep_tree:
            self.pl.plot_removed("Tree formed from graph.")

    def peel_trees(self):
        '''
        Peels the leafs (which are only connected by one of its two endpoints) from the
        tree until there are only matchings of the anyons left.

        -   For each cluster
            -   For each vertex in the cluster
                -   While the (pendant) vertex is connected to one edge:
                    -   If the pendant vertex is an anyon:
                        -   remove anyon status of pendant vertex
                        -   flip anyon status of other vertex
                        -   add edge to matching
                        Else:
                        -   remove/peel edge from tree
                    -   other vertex is the new pendant vertex

        '''

        peel_list = []

        for cID in self.grown_clusters:

            cluster = self.G.C[cID]

            for sID, vertex in cluster.V.items():

                while len(vertex.points_to) == 1:

                    (new_vertex, edge) = list(vertex.points_to.items())[0]

                    cluster.remove_edge(edge)

                    if vertex.state:
                        edge.matching = True
                        vertex.state = False
                        new_vertex.state = not new_vertex.state

                        if self.plot_load and self.plotstep_peel:

                            self.pl.plot_strip_step_anyon(vertex)
                            self.pl.plot_strip_step_anyon(new_vertex)
                            if self.plotstep_tree:
                                self.pl.plot_edge_step(edge, "confirm")
                            else:
                                self.pl.waitforkeypress("peel edge qID #", str(edge))

                    else:
                        edge.peeled = True
                        if self.plot_load:
                            peel_list.append(edge)
                            if self.plotstep_peel:
                                self.pl.plot_edge_step(edge, "peel")

                    vertex = new_vertex

        if self.plot_load and not self.plotstep_peel:
            self.pl.plot_removed("Peeling completed.")
