from peeling_plot import toric_peeling_plot as tpplot
import numpy as np
import random
import copy
import csv
import os

class toric:
    def __init__(self, size, qua_loc, erasures, loadplot = True):

        self.size = size
        self.qua_loc = qua_loc
        self.erasures = erasures

        self.loadplot = loadplot
        self.plotstep_tree = False
        self.plotstep_peel = True
        self.plotstep_click = False

        if not os.path.exists("./peel_data/"):
            os.makedirs("./peel_data/")

        # self.init_edges()
        # self.find_cluster_dev()

        if self.loadplot:
            self.pl = tpplot(size, self.plotstep_peel, self.plotstep_click)
            self.pl.plot_lattice(qua_loc, erasures)


    # def init_edges(self):
    #
    #     filename = "./peel_data/edgelist_toric_L" + str(self.size) + ".csv"
    #
    #     if os.path.exists(filename):
    #
    #         with open(filename, "r") as csvFile:
    #             self.edge_list = [list(map(int,rec)) for rec in csv.reader(csvFile)]
    #         csvFile.close()
    #
    #     else:
    #
    #         edge_list = []
    #
    #         for ertype in range(2):
    #             for hv in range(2):
    #                 for y in range(self.size):
    #                     for x in range(self.size):
    #
    #                         edge_list.append([ertype, hv, y, x])
    #
    #         neighbor_list = []
    #         anyon_list = []
    #
    #         for edge in edge_list:
    #             ertype  = edge[0]
    #             hv      = edge[1]
    #             y       = edge[2]
    #             x       = edge[3]
    #
    #             if ertype == 0:
    #                 v1 = edge_list.index([0, 1 - hv, y, x])
    #                 v2 = edge_list.index([0, 0, (y + 1) % self.size, x])
    #                 v3 = edge_list.index([0, 1, y, (x + 1) % self.size])
    #                 v4 = edge_list.index([0, 0, (y - 1 + hv) % self.size, (x - hv) % self.size])
    #                 v5 = edge_list.index([0, 1, (y - 1 + hv) % self.size, (x - hv) % self.size])
    #                 v6 = edge_list.index([0, 1 - hv, (y - 1 + 2*hv) % self.size, (x + 1 - 2*hv) % self.size])
    #             else:
    #                 v1 = edge_list.index([1, 1 - hv, y, x])
    #                 v2 = edge_list.index([1, 0, y, (x - 1) % self.size])
    #                 v3 = edge_list.index([1, 1, (y - 1) % self.size, x])
    #                 v4 = edge_list.index([1, 0, (y + hv) % self.size, (x + 1 - hv) % self.size])
    #                 v5 = edge_list.index([1, 1, (y + hv) % self.size, (x + 1 - hv) % self.size])
    #                 v6 = edge_list.index([1, 1 - hv, (y - 1 + 2*hv) % self.size, (x + 1 - 2*hv) % self.size])
    #
    #             neighbor_list.append([v1, v2, v3, v4, v5, v6])
    #
    #             if ertype == 0 and hv == 0:
    #                 a = [(y - 1) % self.size, x]
    #             elif ertype == 0 and hv == 1:
    #                 a = [y, (x - 1) % self.size]
    #             elif ertype == 1 and hv == 0:
    #                 a = [y, (x + 1) % self.size]
    #             else:
    #                 a = [(y + 1) % self.size, x]
    #
    #             anyon_list.append(a)
    #
    #         self.edge_list = []
    #
    #         for (edge, neighbor, anyon) in zip(edge_list, neighbor_list, anyon_list):
    #             self.edge_list.append(edge + neighbor + anyon)
    #
    #         with open(filename, "w") as csvFile:
    #             writer = csv.writer(csvFile)
    #             writer.writerows(self.edge_list)
    #
    #         csvFile.close()
    #
    #     self.num_edge = len(self.edge_list)


    '''
    Helper functions
    '''


    def find_neighbors(self, ertype, edge):
        '''
        Finds the neighbors of the input edges for both the X and Z lattice
        The edges on the X and Z lattices are defined by the unit cell:
            X:     Z:
                    _
            _|     |

        For each edge _, this fucntions finds all _|_|_
                                                       | |

                                                      _|_
        For each edge |, this functions finds all _|_
                                                       |

        v1-v3 and v4-v6 are neighbors located at opposite sides of the edge
        '''
        hv = edge[0]
        y = edge[1]
        x = edge[2]

        if ertype == 0:
            e1 = (1 - hv, y, x)
            e2 = (0, (y + 1) % self.size, x)
            e3 = (1, y, (x + 1) % self.size)
            e4 = (0, (y - 1 + hv) % self.size, (x - hv) % self.size)
            e5 = (1, (y - 1 + hv) % self.size, (x - hv) % self.size)
            e6 = (1 - hv, (y - 1 + 2*hv) % self.size, (x + 1 - 2*hv) % self.size)
        else:
            e1 = (1 - hv, y, x)
            e2 = (0, y, (x - 1) % self.size)
            e3 = (1, (y - 1) % self.size, x)
            e4 = (0, (y + hv) % self.size, (x + 1 - hv) % self.size)
            e5 = (1, (y + hv) % self.size, (x + 1 - hv) % self.size)
            e6 = (1 - hv, (y - 1 + 2*hv) % self.size, (x + 1 - 2*hv) % self.size)

        return ([e1, e2, e3], [e4, e5, e6])


    def find_neighbors_all(self, ertype, edges):
        '''
        Finds all the (unique) neighbors given a set of edges
        '''

        neighbors = []
        for e in edges:
            n123, n456 = self.find_neighbors(ertype, e)
            neighbors += n123
            neighbors += n456

        non_dub_neighbors = list(set(neighbors))
        return non_dub_neighbors


    def find_anyons(self, ertype, edge):
        '''
        finds the two anyons/quasiparticles/vertices that are located on either sides of the edge
        '''
        hv = edge[0]
        y = edge[1]
        x = edge[2]

        a1 = (y, x)

        if ertype == 0 and hv == 0:
            a2 = ((y - 1) % self.size, x)
        elif ertype == 0 and hv == 1:
            a2 = (y, (x - 1) % self.size)
        elif ertype == 1 and hv == 0:
            a2 = (y, (x + 1) % self.size)
        else:
            a2 = ((y + 1) % self.size, x)

        return (a1, a2)


    def find_neighbors_tree(self, ertype, edge, cluster, e_tree):
        '''
        finds the neighbors of a vertex within the cluster, and not yet added to the trees
        '''
        n1, n2 = self.find_neighbors(ertype, edge)
        cn1 = [cn for cn in n1 if cn in cluster and cn not in e_tree]
        cn2 = [cn for cn in n2 if cn in cluster and cn not in e_tree]

        return (cn1, cn2)


    '''
    Main functions
    '''

    # def gettuple_edge3(self, id):
    #     hv = self.edge_list[id][1]
    #     y  = self.edge_list[id][2]
    #     x  = self.edge_list[id][3]
    #     return (hv, y, x)
    #
    #
    # def find_cluster_dev(self):
    #
    #     cluster_list = []
    #     in_a_cluster = []
    #
    #     for id in range(self.num_edge):
    #         edge = self.gettuple_edge3(id)
    #         if edge in self.erasures and id not in in_a_cluster:
    #             this_cluster = [id]
    #             in_a_cluster += [id]
    #             new_e = [id]
    #
    #             while not new_e == []:
    #
    #                 nb_e = []
    #                 for new_id in new_e:
    #                     for nb_id in self.edge_list[new_id][4:10]:
    #                         if self.gettuple_edge3(nb_id) in self.erasures and nb_id not in in_a_cluster:
    #                             nb_e.append(nb_id)
    #
    #                 this_cluster += nb_e
    #                 in_a_cluster += nb_e
    #                 new_e = nb_e
    #
    #             cluster_list.append(this_cluster)
    #
    #     print(cluster_list)


    def find_clusters(self):

        '''
        Initiate cluster array (XZ, HV, y, x) with zeros
        In each error dimension XZ, the algorithm will loop over all the edges
        and label each cluster with an #ID number
        The set of clusters for each error is saved in a list [cluster0=[(hv,y,x),..],..]

        '''

        self.cluster_list = []

        for ertype in range(2):
            clusters = np.zeros((2, self.size, self.size))
            cluster_list = []
            id_num = 1

            for hv in range(2):
                for y in range(self.size):
                    for x in range(self.size):
                        e0 = (hv, y, x)
                        if clusters[e0] == 0 and e0 in self.erasures:

                            this_cluster = [e0]
                            new_e = [e0]

                            while new_e != []:
                                for edge in new_e:
                                    clusters[edge] = id_num

                                neighbors = self.find_neighbors_all(ertype, new_e)
                                new_e = [edge for edge in neighbors if (clusters[edge] == 0 and edge in self.erasures)]
                                this_cluster += new_e

                            id_num += 1
                            cluster_list.append(this_cluster)
            self.cluster_list.append(cluster_list)


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
        for ertype in range(2):
            rem_list = []
            for c_i in range(len(self.cluster_list[ertype])):

                cluster = self.cluster_list[ertype][c_i]
                e_tree = []     # edges that are confirmed into the tree
                e_rem = []      # edges that are to be removed from the cluster

                ### Step 1. Find existing leafs or branches
                for edge in cluster:
                    if edge not in e_tree:

                        # find neighbor of edge
                        cn1, cn2 = self.find_neighbors_tree(ertype, edge, cluster, e_tree)

                        # if edge is an ending branch, add to tree
                        if cn1 == [] or cn2 == []:

                            # get branch body
                            cn = cn2 if cn1 == [] else cn1
                            old_e = edge

                            # find entire body of current branch, add to tree, and stop at bisection
                            while len(cn) == 1:
                                new_e = cn[0]
                                cn1, cn2 = self.find_neighbors_tree(ertype, new_e, cluster, e_tree)
                                cn = cn2 if old_e in cn1 else cn1
                                e_tree.append(old_e)
                                if self.plotstep_tree: self.pl.plot_tree_step(ertype, old_e)
                                old_e = new_e
                            else:
                                e_tree.append(old_e)
                                if self.plotstep_tree: self.pl.plot_tree_step(ertype, old_e)

                # find all edges that are in a cycle
                e_cycle = [edge for edge in cluster if edge not in e_tree]

                while e_cycle != []:
                    for edge in e_cycle:
                        if edge not in e_tree:

                            ### Step 2. find a cycle and store its edges in this_cycle
                            this_cycle = [edge]
                            old_e = edge
                            cn, cn2 = self.find_neighbors_tree(ertype, edge, cluster, e_tree)
                            while all([e not in this_cycle for e in cn]):
                                new_e = cn[0]
                                this_cycle.append(new_e)
                                cn1, cn2 = self.find_neighbors_tree(ertype, new_e, cluster, e_tree)
                                cn = cn2 if old_e in cn1 else cn1
                                old_e = new_e
                            else:
                                begin = [e for e in this_cycle if e in cn][-1]
                                cut_cycle = this_cycle[this_cycle.index(begin):]

                            ### Step 3. remove a random edge from this cycle
                            rand = random.randint(0, len(cut_cycle)-1)
                            rem_e = cut_cycle.pop(rand)
                            e_tree.append(rem_e)
                            e_rem.append(rem_e)
                            if self.plotstep_tree: self.pl.plot_removed_step(ertype, rem_e)

                            ### Step 4. other edges of the cycle are checked for tree form, added to tree if yes
                            for edge in cut_cycle:
                                cn1, cn2 = self.find_neighbors_tree(ertype, edge, cluster, e_tree)
                                if cn1 == [] or cn2 == []:

                                    cn = cn2 if cn1 == [] else cn1
                                    old_e = edge
                                    while len(cn) == 1:
                                        new_e = cn[0]
                                        cn1, cn2 = self.find_neighbors_tree(ertype, new_e, cluster, e_tree)
                                        cn = cn2 if old_e in cn1 else cn1
                                        e_tree.append(old_e)
                                        if self.plotstep_tree: self.pl.plot_tree_step(ertype, old_e)
                                        old_e = new_e
                                    else:
                                        e_tree.append(old_e)
                                        if self.plotstep_tree: self.pl.plot_tree_step(ertype, old_e)

                    for edge in e_tree:
                        if edge in e_cycle:
                            e_cycle.remove(edge)
                for edge in e_rem:
                    self.cluster_list[ertype][c_i].remove(edge)

                rem_list += e_rem
            self.rem_list.append(rem_list)

        if self.loadplot:
            self.pl.plot_removed(self.rem_list)


    def peel_tree(self):
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

        for ertype in range(2):

            qua_loc = copy.deepcopy(self.qua_loc[ertype])
            matching = []

            for cluster in self.cluster_list[ertype]:

                e_strip = []

                for edge in cluster:
                    if edge not in e_strip:

                        cn1, cn2 = self.find_neighbors_tree(ertype, edge, cluster, e_strip)
                        va1, va2 = self.find_anyons(ertype, edge)

                        # if edge is an ending branch, add to tree
                        if cn1 == [] or cn2 == []:

                            # get branch body
                            cn = cn2 if cn1 == [] else cn1
                            ea = va1 if cn1 == [] else va2
                            ba = va2 if cn1 == [] else va1

                            if ea in qua_loc:
                                matching.append(edge)
                                qua_loc.remove(ea)

                                if self.plotstep_peel: self.pl.plot_strip_step(ertype, edge)
                                if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ea, 1)

                                if ba in qua_loc:
                                    qua_loc.remove(ba)
                                    if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ba, 1)
                                else:
                                    qua_loc.append(ba)
                                    if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ba)
                            else:
                                if self.plotstep_peel: self.pl.plot_removed_step(ertype, edge)

                            old_e = edge

                            # find entire body of current branch, add to tree, and stop at bisection
                            while len(cn) == 1:
                                new_e = cn[0]
                                cn1, cn2 = self.find_neighbors_tree(ertype, new_e, cluster, e_strip)
                                va1, va2 = self.find_anyons(ertype, new_e)

                                cn = cn2 if old_e in cn1 else cn1
                                ea = va1 if old_e in cn1 else va2
                                ba = va2 if old_e in cn1 else va1

                                e_strip.append(old_e)

                                if ea in qua_loc:
                                    matching.append(new_e)
                                    qua_loc.remove(ea)
                                    if self.plotstep_peel: self.pl.plot_strip_step(ertype, new_e)
                                    if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ea, 1)

                                    if ba in qua_loc:
                                        qua_loc.remove(ba)
                                        if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ba, 1)
                                    else:
                                        qua_loc.append(ba)
                                        if self.plotstep_peel: self.pl.plot_strip_step_anyon(ertype, ba)
                                else:
                                    if self.plotstep_peel: self.pl.plot_removed_step(ertype, new_e)

                                old_e = new_e
                            else:
                                e_strip.append(old_e)



            self.matching.append(matching)

        if self.loadplot:
            self.pl.plot_matching(self.qua_loc, self.erasures, self.matching)

        return self.matching
