from peeling_plot import toric_peeling_plot as tpplot
import numpy as np
import random
import copy
import csv
import os

class toric:
    def __init__(self, lat):
        '''
        :param size             size of the lattice
        :param qua_loc          tuple of anyon locations (y,x)
        :param erasures         tuple of all the erased qubits (td, y, x)
        :init_edge_data         tuple of edge neighbor and anyon data, see init_edge_data

        Optionally, the qubit_data, which contains the neighbors information, can be loaded here.
        During loops, this has benefits to the computation time
        '''

        self.size = lat.size
        self.qua_loc = lat.qua_loc
        self.er_loc = lat.er_loc
        self.qubit_data = lat.qubit_data
        self.stab_data = lat.stab_data
        self.num_stab = lat.num_stab
        self.num_qubit = lat.num_qubit

        self.plot_load = lat.plot_load
        self.plotstep_tree = False
        self.plotstep_peel = False
        self.plotstep_click = False


        if self.plot_load:
            self.pl = tpplot(lat, self.plotstep_peel, self.plotstep_click)
            self.pl.plot_lattice()


    '''
    Helper functions
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


    def stab_get_neighbor_GR(self, sID, elist):
        '''
        :param sID          ID number of the stab/vertex
        :param elist        list of edges that the neighbors are not allowed to be in

        GR for growth; neighbor function for cluster growth

        For a given sID vertex, this function finds the neighboring edges that are not in the outlist (for example the current cluster), and returns the edges that are not yet in elist :{new_edges}
        {new_stabs} contains the connected vertices at the ends of these allowed edges.

        '''

        stab_edges = self.stab_data[sID][4]
        new_edges = [e for e in stab_edges if e not in elist]
        new_stabs = []                                                  # get new stab/vertex location
        for qID in new_edges:
            s1 = self.qubit_data[qID][8]
            s2 = self.qubit_data[qID][9]
            if s1 == sID:
                new_stabs.append(s2)
            else:
                new_stabs.append(s1)

        return (new_edges, new_stabs)

    '''
    Main functions
    '''

    def find_clusters(self):
        '''
        Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected
            and sorts them in separate clusters. A single anyon can also be its own cluster.

        Each cluster is stored with the following information:
         - {CL_edges}        list of edges (qID) contained in each cluster
         - {CL_size}         number of edges in the cluster
         - {CL_parity}       number of anyons in the cluster
         - {CL_boundary}     list of vertices that are on the boundary of the cluster

        Furthermore, {stab_state} a list of 2*L*L is initiated. The value of stab_state on list index sID points to which cluster with cluster index cID it belongs to.

        This algorithm loops over all detected anyons and checks whether there are connected erasures to it, in which case it further expands this 'neighbor check' to find all connected edges that are an erasure. In this process, we also keep track of the vertices, to which cluster they belong and whether a vertex is on the boundary, and whether it is an anyon.
        Two seperate lists, {in_cluster_edge} and {in_cluster_anyon} are kept which are the edges and anyons that have already been checked before, such that the 'neighbor check' and initial loop are not redundant.
        '''

        self.CL_edges       = []
        self.CL_size        = []
        self.CL_parity      = []
        self.CL_boundary    = []
        self.stab_state     = [None for _ in range(self.num_stab)]
        # self.edge_state     = [0 for _ in range(self.num_qubit)]

        in_cluster_edge     = []
        in_cluster_anyon    = []


        cID = 0
        for sID in self.qua_loc:
            if sID not in in_cluster_anyon:

                (new_edges, NEW_stabs, in_anyons, boundary) = self.stab_get_neighbor_CL(sID, self.er_loc, in_cluster_edge, self.qua_loc)

                this_cluster_anyon = [sID] + in_anyons
                in_cluster_anyon += in_anyons
                this_cluster_edge = new_edges
                in_cluster_edge += new_edges
                this_cluster_boundary = [sID] if boundary else []
                self.stab_state[sID] = cID

                # If neigbors are found, this cluster is not a single-anyon cluster, and while loops begins, until there are no new neighbors

                while not NEW_stabs == []:

                    cluster_stabs = []
                    round_anyons = []
                    round_bound = []

                    for sID2 in NEW_stabs:
                        (new_edges, new_stabs, in_anyons, boundary) = self.stab_get_neighbor_CL(sID2, self.er_loc, in_cluster_edge, self.qua_loc)

                        cluster_stabs += new_stabs
                        round_anyons += in_anyons
                        this_cluster_edge += new_edges
                        in_cluster_edge += new_edges
                        if boundary: round_bound.append(sID2)
                        self.stab_state[sID2] = cID

                    NEW_stabs = list(set(cluster_stabs))
                    new_anyons = list(set(round_anyons))
                    this_cluster_boundary += list(set(round_bound))
                    this_cluster_anyon += new_anyons
                    in_cluster_anyon += new_anyons


                # for edge in this_cluster_edge: self.edge_state[edge] = 2
                self.CL_edges.append(this_cluster_edge)
                self.CL_size.append(len(this_cluster_edge))
                self.CL_parity.append(len(this_cluster_anyon))
                self.CL_boundary.append(this_cluster_boundary)
                cID += 1

        self.num_clusters = len(self.CL_size)

    def select_growth_clusters(self):

        '''
        Select which clusters are valid for growth. All uneven clusters can be grown
        {weighted_growth} toggles the selection of only the smallers uneven clusters for growth.
        Returns: boolean list of N_clusters
        '''

        weighted_growth = True


        if weighted_growth:

            valid_cID = []
            valid_size = []
            for cID,(size,parity) in enumerate(zip(self.CL_size, self.CL_parity)):
                if size != None and parity % 2 == 1:
                    valid_cID.append(cID)
                    valid_size.append(size)

            grow_cID = [False for _ in range(self.num_clusters)]

            if valid_cID != []:
                minsize = min(valid_size)
                min_cID = [cID for cID,size in zip(valid_cID,valid_size) if size == minsize]

                for cID in min_cID:
                    grow_cID[cID] = True

        else:

            grow_cID = []
            for cID, parity in enumerate(self.CL_parity):
                if parity != None and parity % 2 == 1:
                    grow_cID.append(cID)

        return grow_cID

    def cluster_index_tree(self, cID):
        '''
        :param cID      input cluster index, can be a branch or a base of the tree
        Loops through the {cluster_index} tree to find the base cID of the cluster index tree.
        Returns: cID, must be the base of the cluster index tree
        '''

        if cID != None:
            while cID != self.cluster_index[cID]:
                cID = self.cluster_index[cID]
        return cID

    def grow_clusters(self):
        '''
        Clusters needs te be grown and merged until there are no uneven clusters left.
        The grow_clusters algorithm can be split into four steps:

            1.  Find new edges and vertices from old cluster boundary, select half-step growth clusters for step A

                a.  Find uneven edges that are eligable for growth, possibly select only the smallest uneven clusters

                b.  From {CL_boundary} and {CL_edges}, find edges connected to the boundary that are not yet in the cluster. hese edges are the new edges to grow onto: {CL_half_edges}. The vertices on the other end of these new edges are the new boundary: {CL_new_bounds}.

                c.  Remove {CL_boundary} from this cluster. This clusters can not be selected for step A before step B is finished. {Fusion_A} contains all edges that are to be (half) grown.

            2.  Growth step A, half edges grown

                a.  For each edge in {Fusion_A}, find out to which cluster the two connected vertices belong in {stab_data}. In order to prevent that {stab_data} needs to be updated every time clusters merge, we build a tree {cluster_index} of N_clusters that point to the root index of the cluster. When two clusters merge, the value of the root of the smaller clusters is pointed toward the index number of the bigger cluster.

                b.  Check that the two clusters are in different clusters.

                c.  Check that both clusters are in the same step of the growth. Union is only possible here if both clusters are in growth step A. Otherwise, union will take place during growth step 2.

                d.  Find smaller cluster and merge smaller cluster onto bigger cluster.

            3.  Find clusters eligable for growth step B

                a.  Find uneven clusters and from {CL_half_edges} get list of edges for growth step B :{Fusion_B}

            4.  Growth step B, full edges grown and new vertices are new cluster boundary

                    For each edge in {Fusion_B}, find out to which cluster the two connected vertices belong in {stab_data}. There are four situations that can occur:

                a.  Vertex I belongs to cluster, vertex II to none. Add edge to {CL_edges} and add Vertex II to {CL_boundary}, which is now eligable for growth step A again.

                b.  Vertex II belongs to cluster, vertex I to none. Add edge to {CL_edges} and add Vertex I to {CL_boundary}, which is now eligable for growth step A again.

                c.  Vertex I and II both belong to the same cluster. This is due that either vertex I or II was already added via another edge in sitation a or b. Add edge to {CL_edges}

                d.  Vertex I and II belong to different clusters. This can either be between two clusters grown in step A, or a single cluster grown in step A and an ungrown cluster. Merge the clusters. Remove {CL_new_bounds} and {CL_half_edges}. This clusters can now be initated again in step 1.




        '''

        # for i,a in enumerate(self.stab_data):
        #     print(i,a)
        # print("Clusters after initilization:")
        # for i,a in enumerate(zip(self.CL_size, self.CL_parity, self.CL_edges, self.CL_boundary)):
        #     print(i,a)
        # input()

        grow_id = self.select_growth_clusters()

        self.cluster_index = [i for i in range(self.num_clusters)]
        CL_half_edges = [[] for _ in range(self.num_clusters)]
        CL_new_bounds = [[] for _ in range(self.num_clusters)]


        while any(grow_id):

            '''
            Step 1: Find new edges and vertices from old cluster boundary, select half-step growth clusters for step A
            '''

            Fusion_A = []

            for cID, growth in enumerate(grow_id):

                cluster_stabs = []
                cluster_half_edges = []
                cluster_new_bounds = []

                if growth:
                    for sID in self.CL_boundary[cID]:

                        (new_edges, new_stabs) = self.stab_get_neighbor_GR(sID, self.CL_edges[cID])

                        Fusion_A += new_edges
                        cluster_stabs += new_stabs
                        cluster_half_edges += new_edges

                    self.CL_boundary[cID] = []

                CL_half_edges[cID] = cluster_half_edges
                CL_new_bounds[cID] = cluster_stabs

            # print("After growth of first half-step:")
            # for i,a in enumerate(zip(self.CL_size, self.CL_parity, self.CL_edges, self.CL_boundary, CL_half_edges, CL_new_bounds)):
            #     print(i,a)
            # input()

            '''
            Step 2: Growth step A, half edges grown
            '''

            union_qID = []

            for qID in Fusion_A:

                sID1 = self.qubit_data[qID][8]
                sID2 = self.qubit_data[qID][9]

                cID1 = self.cluster_index_tree(self.stab_state[sID1])
                cID2 = self.cluster_index_tree(self.stab_state[sID2])

                if cID1 != None and cID2 != None and cID1 != cID2:
                    if qID in CL_half_edges[cID1] and qID in CL_half_edges[cID2]:

                        union_qID.append(qID)

                        size1 = self.CL_size[cID1]
                        size2 = self.CL_size[cID2]

                        if self.CL_size[cID1] < self.CL_size[cID2]:
                            main_cID = cID2
                            appe_cID = cID1
                        else:
                            main_cID = cID1
                            appe_cID = cID2

                        self.cluster_index[appe_cID] = main_cID
                        self.stab_state[sID1] = main_cID
                        self.stab_state[sID2] = main_cID
                        # self.edge_state[qID] = 1

                        qindexm = CL_half_edges[main_cID].index(qID)
                        qindexa = CL_half_edges[appe_cID].index(qID)
                        del CL_half_edges[main_cID][qindexm]
                        del CL_half_edges[appe_cID][qindexa]
                        del CL_new_bounds[main_cID][qindexm]
                        del CL_new_bounds[appe_cID][qindexa]

                        self.CL_size[main_cID]      += self.CL_size[appe_cID] + 1
                        self.CL_parity[main_cID]    += self.CL_parity[appe_cID]
                        self.CL_edges[main_cID]     += self.CL_edges[appe_cID] + [qID]
                        CL_half_edges[main_cID]     += CL_half_edges[appe_cID]
                        self.CL_boundary[main_cID]  += self.CL_boundary[appe_cID]
                        CL_new_bounds[main_cID]     += CL_new_bounds[appe_cID]

                        self.CL_size[appe_cID]      = None
                        self.CL_edges[appe_cID]     = None
                        self.CL_parity[appe_cID]    = None
                        self.CL_boundary[appe_cID]  = None
                        CL_half_edges[appe_cID]     = []
                        CL_new_bounds[appe_cID]     = []


            # print("After first union operation:")
            # for i,a in enumerate(zip(self.CL_size, self.CL_parity, self.CL_edges, self.CL_boundary, CL_half_edges, CL_new_bounds)):
            #     print(i,a)
            # input()

            '''
            Step 3: Find clusters eligable for growth step B
            '''
            Fusion_B = []
            for parity, half_edges in zip(self.CL_parity, CL_half_edges):
                if parity != None and parity % 2 == 1:
                    Fusion_B += half_edges


            '''
            Step 4: Growth step B, full edges grown and new vertices are new cluster boundary
            '''

            for qID in Fusion_B:

                sID1 = self.qubit_data[qID][8]
                sID2 = self.qubit_data[qID][9]

                cID1 = self.cluster_index_tree(self.stab_state[sID1])
                cID2 = self.cluster_index_tree(self.stab_state[sID2])

                if cID1 == None and cID2 != None:
                    self.CL_size[cID2] += 1
                    self.CL_edges[cID2].append(qID)
                    qindex = CL_half_edges[cID2].index(qID)
                    self.CL_boundary[cID2].append(CL_new_bounds[cID2][qindex])
                    del CL_half_edges[cID2][qindex]
                    del CL_new_bounds[cID2][qindex]
                    self.stab_state[sID1] = cID2

                elif cID1 != None and cID2 == None:
                    self.CL_size[cID1] += 1
                    self.CL_edges[cID1].append(qID)
                    qindex = CL_half_edges[cID1].index(qID)
                    self.CL_boundary[cID1].append(CL_new_bounds[cID1][qindex])
                    del CL_half_edges[cID1][qindex]
                    del CL_new_bounds[cID1][qindex]
                    self.stab_state[sID2] = cID1

                elif cID1 != None and cID2 != None:
                    if cID1 == cID2:          # if two vetices from the sa

                        self.CL_size[cID1] += 1
                        self.CL_edges[cID1].append(qID)
                        qindex = CL_half_edges[cID1].index(qID)
                        del CL_half_edges[cID1][qindex]
                        del CL_new_bounds[cID1][qindex]

                    else:

                        size1 = self.CL_size[cID1]
                        size2 = self.CL_size[cID2]

                        if self.CL_size[cID1] < self.CL_size[cID2]:
                            main_cID = cID2
                            appe_cID = cID1
                        else:
                            main_cID = cID1
                            appe_cID = cID2

                        self.cluster_index[appe_cID] = main_cID

                        self.CL_size[main_cID]      += self.CL_size[appe_cID] + 1
                        self.CL_parity[main_cID]    += self.CL_parity[appe_cID]
                        self.CL_edges[main_cID]     += self.CL_edges[appe_cID] + [qID]
                        self.CL_boundary[main_cID]  += self.CL_boundary[appe_cID]


                        if qID in CL_half_edges[cID1]:
                            qindex = CL_half_edges[cID1].index(qID)
                            del CL_half_edges[cID1][qindex]
                            del CL_new_bounds[cID1][qindex]
                        if qID in CL_half_edges[cID2]:
                            qindex = CL_half_edges[cID2].index(qID)
                            del CL_half_edges[cID2][qindex]
                            del CL_new_bounds[cID2][qindex]

                        CL_half_edges[main_cID] += CL_half_edges[appe_cID]
                        CL_new_bounds[main_cID] += CL_new_bounds[appe_cID]

                        self.CL_size[appe_cID]      = None
                        self.CL_edges[appe_cID]     = None
                        self.CL_parity[appe_cID]    = None
                        self.CL_boundary[appe_cID]  = None
                        CL_half_edges[appe_cID]     = []
                        CL_new_bounds[appe_cID]     = []

                    # print(qID, sID1, sID2, cID1, cID2)
                    # for i,a in enumerate(zip(self.CL_size, self.CL_parity, self.CL_edges, self.CL_boundary, CL_half_edges, CL_new_bounds)):
                    #     print(i,a)
                    # input()

            # print("After second union operation:")
            # for i,a in enumerate(zip(self.CL_size, self.CL_parity, self.CL_edges, self.CL_boundary, CL_half_edges, CL_new_bounds)):
            #     print(i,a)
            # input()

            if self.plot_load:
                self.pl.plot_growth(Fusion_B + union_qID)

            grow_id = self.select_growth_clusters()




    def init_trees(self):
        '''
        Makes trees from clusters.
        Within the clusters there are possibly cycles of the edges
        The peeling algorithm requires that all cycles are broken such that the cluster is a tree-like structure
        For example:
         _
        |_|     ->      |_|

        The trees are initiated in 5 steps:
            1.  Find all existing leafs (pendant edges) of the cluster and confirm them into the tree
                All unconfirmed vertices are in cycles
            2.  Find a cycle by a random walk over the edges until it encounters itself
            3.  Randomly remove an edge of this cycle from the cluster
            4.  Apply step 1 to remaining edges within the cycle
            5.  Repeat steps 2-4 until there are no cycles left
        '''

        self.rem_list = []

        for c_i, cluster in enumerate(self.cluster_list):

            self.e_tree = []     # edges that are confirmed into the tree
            e_rem = []      # edges that are to be removed from the cluster

            ### Step 1. Find existing leafs or branches

            self.walk_leaf_tree(cluster, cluster)

            # find all edges that are in a cycle
            e_cycle = [edge for edge in cluster if edge not in self.e_tree]

            while e_cycle != []:
                for edge in e_cycle:
                    if edge not in self.e_tree:

                        ### Step 2. find a cycle and store its edges in this_cycle
                        cycle = self.walk_cycle_random(edge, cluster)
                        # cycle = self.walk_cycle_graph(edge, cluster)

                        ### Step 3. remove a random edge from this cycle
                        rand = random.randint(0, len(cycle)-1)
                        rem_e = cycle.pop(rand)
                        self.e_tree.append(rem_e)
                        e_rem.append(rem_e)
                        if self.plotstep_tree: self.pl.plot_removed_step(rem_e)

                        ### Step 4. other edges of the cycle are checked for tree form, added to tree if yes
                        self.walk_leaf_tree(cycle, cluster)

                for edge in self.e_tree:
                    if edge in e_cycle:
                        e_cycle.remove(edge)
            for edge in e_rem:
                self.cluster_list[c_i].remove(edge)

            self.rem_list += e_rem

        # if self.plot_load:
        #     self.pl.plot_removed(self.rem_list)

    def peel_trees(self):
        '''
        Peels the leafs (which are only connected by one of its two endpoints) from the
        tree until there are only matchings of the anyons left.

        For each leaf:
            if there is an anyon on its pendant vertex, add this leaf to the matching
                and flip the value of the other vertex.
                 -> if its other vertex is an anyon, remove this anyon; if not, make this vertex an anyon
            if there is not, simply remove this edge from the cluster

        '''

        self.matching = []

        for cluster in self.cluster_list:

            ertype = self.qubit_data[cluster[0]][0]
            qua_loc = list(self.qua_loc[ertype])
            e_strip = []

            for edge in cluster:
                if edge not in e_strip:

                    cn1, cn2 = self.get_neighbors_id_tree(edge, cluster, e_strip)
                    va1, va2 = self.get_anyons_id(edge)

                    # if edge is an ending branch, add to tree
                    if cn1 == [] or cn2 == []:

                        # get branch body
                        cn = cn2 if cn1 == [] else cn1
                        ea = va1 if cn1 == [] else va2
                        ba = va2 if cn1 == [] else va1

                        if ea in qua_loc:
                            self.matching.append(edge)
                            qua_loc.remove(ea)

                            if self.plotstep_peel: self.pl.plot_strip_step(edge)
                            if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ea, 1)

                            if ba in qua_loc:
                                qua_loc.remove(ba)
                                if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ba, 1)
                            else:
                                qua_loc.append(ba)
                                if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ba)
                        else:
                            if self.plotstep_peel: self.pl.plot_removed_step(edge)

                        old_e = edge

                        # find entire body of current branch, add to tree, and stop at bisection
                        while len(cn) == 1:
                            new_e = cn[0]
                            cn1, cn2 = self.get_neighbors_id_tree(new_e, cluster, e_strip)
                            va1, va2 = self.get_anyons_id(new_e)

                            cn = cn2 if old_e in cn1 else cn1
                            ea = va1 if old_e in cn1 else va2
                            ba = va2 if old_e in cn1 else va1

                            e_strip.append(old_e)

                            if ea in qua_loc:
                                self.matching.append(new_e)
                                qua_loc.remove(ea)
                                if self.plotstep_peel: self.pl.plot_strip_step(new_e)
                                if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ea, 1)

                                if ba in qua_loc:
                                    qua_loc.remove(ba)
                                    if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ba, 1)
                                else:
                                    qua_loc.append(ba)
                                    if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ba)
                            else:
                                if self.plotstep_peel: self.pl.plot_removed_step(new_e)

                            old_e = new_e
                        else:
                            e_strip.append(old_e)

    def match_to_loc(self):

        matchingX = []
        matchingZ = []
        for edge in self.matching:
            (ertype, td, y, x) = self.qubit_data[edge][0:4]
            if ertype == 0:
                matchingX.append((td, y, x))
            else:
                matchingZ.append((td, y, x))

        match_loc = [matchingX, matchingZ]

        # if self.plot_load:
        #     self.pl.plot_matching(self.qua_loc, self.er_loc, match_loc)

        return match_loc
