from peeling_plot import toric_peeling_plot as tpplot
import numpy as np
import random
import copy
import csv
import os

class toric:
    def __init__(self, size, qua_loc, erasures, edge_data = (), loadplot = True):
        '''
        :param size             size of the lattice
        :param qua_loc

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

        self.size = size
        self.qua_loc = qua_loc
        self.erasures = erasures

        self.loadplot = loadplot
        self.plotstep_tree = False
        self.plotstep_peel = False
        self.plotstep_click = False

        if edge_data == ():
            self.init_edge_data()
        else:
            self.edge_data = edge_data

    def init_edge_data(self):



        edge_list = []

        for ertype in range(2):
            for hv in range(2):
                for y in range(self.size):
                    for x in range(self.size):

                        edge_list.append([ertype, hv, y, x])

        neighbor_list = []
        anyon_list = []

        for edge in edge_list:
            ertype  = edge[0]
            hv      = edge[1]
            y       = edge[2]
            x       = edge[3]

            if ertype == 0:
                v1 = edge_list.index([0, 1 - hv, y, x])
                v2 = edge_list.index([0, 0, (y + 1) % self.size, x])
                v3 = edge_list.index([0, 1, y, (x + 1) % self.size])
                v4 = edge_list.index([0, 0, (y - 1 + hv) % self.size, (x - hv) % self.size])
                v5 = edge_list.index([0, 1, (y - 1 + hv) % self.size, (x - hv) % self.size])
                v6 = edge_list.index([0, 1 - hv, (y - 1 + 2*hv) % self.size, (x + 1 - 2*hv) % self.size])
            else:
                v1 = edge_list.index([1, 1 - hv, y, x])
                v2 = edge_list.index([1, 0, y, (x - 1) % self.size])
                v3 = edge_list.index([1, 1, (y - 1) % self.size, x])
                v4 = edge_list.index([1, 0, (y + hv) % self.size, (x + 1 - hv) % self.size])
                v5 = edge_list.index([1, 1, (y + hv) % self.size, (x + 1 - hv) % self.size])
                v6 = edge_list.index([1, 1 - hv, (y - 1 + 2*hv) % self.size, (x + 1 - 2*hv) % self.size])

            neighbor_list.append([v1, v2, v3, v4, v5, v6])

            if ertype == 0 and hv == 0:
                a = [(y - 1) % self.size, x]
            elif ertype == 0 and hv == 1:
                a = [y, (x - 1) % self.size]
            elif ertype == 1 and hv == 0:
                a = [y, (x + 1) % self.size]
            else:
                a = [(y + 1) % self.size, x]

            anyon_list.append(a)

        edge_data = []

        for (edge, neighbor, anyon) in zip(edge_list, neighbor_list, anyon_list):
            edge_data.append(tuple(edge + neighbor + anyon))

        self.edge_data = tuple(edge_data)

        if self.loadplot:
            self.pl = tpplot(self.size, self.edge_data, self.plotstep_peel, self.plotstep_click)
            self.pl.plot_lattice(self.qua_loc, self.erasures)

        return self.edge_data


    '''
    Helper functions
    '''
    def gettuple_edge(self, id):
        hv = self.edge_data[id][1]
        y  = self.edge_data[id][2]
        x  = self.edge_data[id][3]
        return (hv, y, x)

    def get_neighbors_id_tree(self, id, cluster, e_tree):
        '''
        finds the neighbors of a vertex within the cluster, and not yet added to the trees
        '''
        n1 = self.edge_data[id][4:7]
        n2 = self.edge_data[id][7:10]
        cn1 = [cn for cn in n1 if cn in cluster and cn not in e_tree]
        cn2 = [cn for cn in n2 if cn in cluster and cn not in e_tree]
        return (cn1, cn2)

    def get_anyons_id(self, id):
        '''
        finds the two anyons/quasiparticles/vertices that are located on either sides of the edge
        '''
        a1 = (self.edge_data[id][2], self.edge_data[id][3])
        a2 = (self.edge_data[id][10], self.edge_data[id][11])
        return (a1, a2)


    '''
    Main functions
    '''

    def find_clusters(self):

        self.cluster_list = []
        in_a_cluster = []

        for id in range(len(self.edge_data)):
            edge = self.gettuple_edge(id)
            if edge in self.erasures and id not in in_a_cluster:
                this_cluster = [id]
                in_a_cluster += [id]
                new_e = [id]

                while not new_e == []:

                    nb_e = []
                    for new_id in new_e:
                        for nb_id in self.edge_data[new_id][4:10]:
                            if self.gettuple_edge(nb_id) in self.erasures and nb_id not in in_a_cluster:
                                nb_e.append(nb_id)

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

        for c_i in range(len(self.cluster_list)):

            cluster = self.cluster_list[c_i]
            e_tree = []     # edges that are confirmed into the tree
            e_rem = []      # edges that are to be removed from the cluster

            ### Step 1. Find existing leafs or branches
            for edge in cluster:
                if edge not in e_tree:

                    # find neighbor of edge
                    cn1, cn2 = self.get_neighbors_id_tree(edge, cluster, e_tree)

                    # if edge is an ending branch, add to tree
                    if cn1 == [] or cn2 == []:

                        # get branch body
                        cn = cn2 if cn1 == [] else cn1
                        old_e = edge

                        # find entire body of current branch, add to tree, and stop at bisection
                        while len(cn) == 1:
                            new_e = cn[0]
                            cn1, cn2 = self.get_neighbors_id_tree(new_e, cluster, e_tree)
                            cn = cn2 if old_e in cn1 else cn1
                            e_tree.append(old_e)
                            if self.plotstep_tree: self.pl.plot_tree_step(old_e)
                            old_e = new_e
                        else:
                            e_tree.append(old_e)
                            if self.plotstep_tree: self.pl.plot_tree_step(old_e)

            # find all edges that are in a cycle
            e_cycle = [edge for edge in cluster if edge not in e_tree]

            while e_cycle != []:
                for edge in e_cycle:
                    if edge not in e_tree:

                        ### Step 2. find a cycle and store its edges in this_cycle
                        this_cycle = [edge]
                        old_e = edge
                        cn, cn2 = self.get_neighbors_id_tree(edge, cluster, e_tree)
                        while all([e not in this_cycle for e in cn]):
                            new_e = cn[0]
                            this_cycle.append(new_e)
                            cn1, cn2 = self.get_neighbors_id_tree(new_e, cluster, e_tree)
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
                        if self.plotstep_tree: self.pl.plot_removed_step(rem_e)

                        ### Step 4. other edges of the cycle are checked for tree form, added to tree if yes
                        for edge in cut_cycle:
                            cn1, cn2 = self.get_neighbors_id_tree(edge, cluster, e_tree)
                            if cn1 == [] or cn2 == []:

                                cn = cn2 if cn1 == [] else cn1
                                old_e = edge
                                while len(cn) == 1:
                                    new_e = cn[0]
                                    cn1, cn2 = self.get_neighbors_id_tree(new_e, cluster, e_tree)
                                    cn = cn2 if old_e in cn1 else cn1
                                    e_tree.append(old_e)
                                    if self.plotstep_tree: self.pl.plot_tree_step(old_e)
                                    old_e = new_e
                                else:
                                    e_tree.append(old_e)
                                    if self.plotstep_tree: self.pl.plot_tree_step(old_e)

                for edge in e_tree:
                    if edge in e_cycle:
                        e_cycle.remove(edge)
            for edge in e_rem:
                self.cluster_list[c_i].remove(edge)

            self.rem_list += e_rem

        if self.loadplot:
            self.pl.plot_removed(self.rem_list)

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
            (ertype, hv, y, x) = self.edge_data[edge][0:4]
            if ertype == 0:
                matchingX.append((hv, y, x))
            else:
                matchingZ.append((hv, y, x))

        match_loc = [matchingX, matchingZ]

        if self.loadplot:
            self.pl.plot_matching(self.qua_loc, self.erasures, match_loc)

        return match_loc
