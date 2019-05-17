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

        Optionally, the edge_data, which contains the neighbors information, can be loaded here.
        During loops, this has benefits to the computation time
        '''

        self.size = lat.size
        self.qua_loc = lat.qua_loc
        self.er_loc = lat.er_loc
        self.edge_data = lat.qubit_data
        self.anyon_data = lat.stab_data

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
        y  = self.edge_data[id][1]
        x  = self.edge_data[id][2]
        td = self.edge_data[id][3]
        return (y, x, td)


    def get_neighbors_id_tree(self, id, inlist, outlist):
        '''
        finds the neighbors of a vertex within the cluster, and not yet added to the trees
        '''
        n1 = self.edge_data[id][5]
        n2 = self.edge_data[id][7]
        cn1 = [cn for cn in n1 if cn in inlist and cn not in outlist]
        cn2 = [cn for cn in n2 if cn in inlist and cn not in outlist]
        return (cn1, cn2)


    def get_anyons_id(self, id):
        '''
        finds the two anyons/quasiparticles/vertices that are located on either sides of the edge
        '''
        a1 = self.edge_data[id][8]
        a2 = self.edge_data[id][9]
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

    def walk_cycle_graph(self, edge, cluster):
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

        cn1, cn2 = self.get_neighbors_id_tree(edge, cluster, self.e_tree)
        cn = cn1 + cn2
        branches = cn
        graph = [[edge]] + [[branch, 0] for branch in cn]

        found_cycle = False
        parent = 1

        while found_cycle == False:
            new_branches = []
            for branch in branches:
                children1, children2 = self.get_neighbors_id_tree(branch, cluster, self.e_tree)
                children = children2 if graph[graph[parent][1]][0] in children1 else children1
                graph += [[child, parent] for child in children]

                if edge in children:
                    cycle = [graph[parent][0]]
                    cycle_parent = graph[parent][1]
                    found_cycle = True
                    break

                parent += 1
                new_branches += children

            branches = new_branches

        while cycle_parent != 0:
            cycle.append(graph[cycle_parent][0])
            cycle_parent = graph[cycle_parent][1]
        else:
            cycle.append(graph[0][0])

        return cycle


    '''
    Main functions
    '''

    def find_clusters(self):
        '''
        Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected
            and sorts them in separate clusters
        '''

        self.cluster_list = []
        in_a_cluster = []

        print(self.er_loc)

        for id in self.er_loc:
            if id not in in_a_cluster:
                this_cluster = [id]
                in_a_cluster += [id]
                new_e = [id]

                while not new_e == []:
                    nb_e = []
                    for new_id in new_e:
                        cn1, cn2 = self.get_neighbors_id_tree(id, self.er_loc, in_a_cluster)
                        nb_e += cn1 + cn2

                    non_dub_nb_e = list(set(nb_e))

                    this_cluster += non_dub_nb_e
                    in_a_cluster += non_dub_nb_e
                    new_e = non_dub_nb_e

                self.cluster_list.append(this_cluster)


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

            ertype = self.edge_data[cluster[0]][0]
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
            (ertype, td, y, x) = self.edge_data[edge][0:4]
            if ertype == 0:
                matchingX.append((td, y, x))
            else:
                matchingZ.append((td, y, x))

        match_loc = [matchingX, matchingZ]

        # if self.plot_load:
        #     self.pl.plot_matching(self.qua_loc, self.er_loc, match_loc)

        return match_loc
