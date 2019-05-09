from peeling_plot import toric_peeling_plot as tpplot
import numpy as np
import random

class toric:
    def __init__(self, size, qua_loc, erasures, loadplot = True, plotstep = False):

        self.size = size
        self.qua_loc = qua_loc
        self.erasures = erasures

        self.loadplot = loadplot
        self.plotstep = plotstep

        if self.loadplot:
            self.pl = tpplot(size)
            self.pl.plot_lattice(qua_loc, erasures)

        self.find_clusters()
        self.init_trees()



    # def __init__(self):
    #     self.cluster_list = [[[(0,0,0), (1,0,0), (0,1,0), (0,2,0), (1,1,1), (0,2,1), (1,2,1), (0,3,1), (1,3,2), (0,4,1)]],[]]
    #     self.size = 5


    def find_neighbors(self, ertype, vertice):
        '''
        Finds the neighbors of the input qvertices for both the X and Z lattice
        On qvertices on the X and Z lattices are defined by the unit cell:
            X:     Z:
                    _
            _|     |

        For each qvertice _, this fucntions finds all _|_|_
                                                       | |

                                                      _|_
        For each qvertice |, this functions finds all _|_
                                                       |

        v1-v3 and v4-v6 are neighbors located at opposite sides of the qvertice
        '''
        hv = vertice[0]
        y = vertice[1]
        x = vertice[2]

        if ertype == 0:
            v1 = (1 - hv, y, x)
            v2 = (0, (y + 1) % self.size, x)
            v3 = (1, y, (x + 1) % self.size)
            v4 = (0, (y - 1 + hv) % self.size, (x - hv) % self.size)
            v5 = (1, (y - 1 + hv) % self.size, (x - hv) % self.size)
            v6 = (1 - hv, (y - 1 + 2*hv) % self.size, (x + 1 - 2*hv) % self.size)
        else:
            v1 = (1 - hv, y, x)
            v2 = (0, y, (x - 1) % self.size)
            v3 = (1, (y - 1) % self.size, x)
            v4 = (0, (y + hv) % self.size, (x + 1 - hv) % self.size)
            v5 = (1, (y + hv) % self.size, (x + 1 - hv) % self.size)
            v6 = (1 - hv, (y - 1 + 2*hv) % self.size, (x + 1 - 2*hv) % self.size)


        ### This part replaces the previous if loop, but is it better?
        # v1 = (1 - hv, y, x)
        # v2 = (ertype, (y + 1 - 2*ertype) % self.size, x)
        # v3 = (ertype, y, (x + 1 - 2*ertype) % self.size)
        # v4 = (0, (y + hv + ertype - 1) % self.size, (x - hv + ertyppythoe) % self.size)
        # v5 = (0, (y + hv + ertype - 1) % self.size, (x - hv + ertype) % self.size)
        # v6 = (1 - hv, (y - 1 + 2*hv) % self.size, (x + 1 - 2*hv) % self.size)

        return ([v1, v2, v3], [v4, v5, v6])

    def find_neighbors_all(self, ertype, vertices):
        '''
        Finds all the (unique) neighbors given a set of qvertices
        '''

        neighbors = []
        for v in vertices:
            n123, n456 = self.find_neighbors(ertype, v)
            neighbors += n123
            neighbors += n456

        non_dub_neighbors = list(set(neighbors))
        return non_dub_neighbors



    def find_clusters(self):

        '''
        Initiate cluster array (XZ, HV, y, x) with zeros
        In each error dimension XZ, the algorithm will loop over all the qvertices
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
                        v0 = (hv, y, x)
                        if clusters[v0] == 0 and v0 in self.erasures:

                            this_cluster = [v0]
                            new_v = [v0]

                            while new_v != []:
                                for ver in new_v:
                                    clusters[ver] = id_num

                                neighbors = self.find_neighbors_all(ertype, new_v)
                                new_v = [ver for ver in neighbors if (clusters[ver] == 0 and ver in self.erasures)]
                                this_cluster += new_v

                            id_num += 1
                            cluster_list.append(this_cluster)
            self.cluster_list.append(cluster_list)

    def find_neighbors_tree(self, ertype, v, cluster, v_tree):
        '''
        finds the neighbors of a vertice within the cluster, and not yet added to the trees
        '''
        n1, n2 = self.find_neighbors(ertype, v)
        cn1 = [cn for cn in n1 if cn in cluster and cn not in v_tree]
        cn2 = [cn for cn in n2 if cn in cluster and cn not in v_tree]

        return (cn1, cn2)


    def init_trees(self):
        '''
        Makes trees from clusters
        '''

        self.rem_list = []
        for ertype in range(2):
            rem_list = []
            for c_i in range(len(self.cluster_list[ertype])):

                cluster = self.cluster_list[ertype][c_i]

                v_tree = []
                v_rem = []

                # find all vertices that are already in tree form
                for v in cluster:
                    if v not in v_tree:

                        # find neighbor of vertice
                        cn1, cn2 = self.find_neighbors_tree(ertype, v, cluster, v_tree)

                        # if vertice is an ending branch, add to tree
                        if cn1 == [] or cn2 == []:

                            # get branch body
                            cn = cn2 if cn1 == [] else cn1
                            old_v = v

                            # find entire body of current branch, add to tree, and stop at bisection
                            while len(cn) == 1:
                                new_v = cn[0]
                                cn1, cn2 = self.find_neighbors_tree(ertype, new_v, cluster, v_tree)
                                cn = cn2 if old_v in cn1 else cn1
                                v_tree.append(old_v)
                                if self.plotstep: self.pl.plot_tree_step(ertype, old_v)
                                old_v = new_v
                            else:
                                v_tree.append(old_v)
                                if self.plotstep: self.pl.plot_tree_step(ertype, old_v)

                # find all vertices that are in a cycle
                v_cycle = [v for v in cluster if v not in v_tree]

                while v_cycle != []:
                    for v in v_cycle:
                        if v not in v_tree:

                            # find a cycle and store its vertices in this_cycle
                            this_cycle = [v]
                            old_v = v
                            cn, cn2 = self.find_neighbors_tree(ertype, v, cluster, v_tree)
                            while all([v not in this_cycle for v in cn]):
                                new_v = cn[0]
                                this_cycle.append(new_v)
                                cn1, cn2 = self.find_neighbors_tree(ertype, new_v, cluster, v_tree)
                                cn = cn2 if old_v in cn1 else cn1
                                old_v = new_v
                            else:
                                begin = [v for v in this_cycle if v in cn][-1]
                                cut_cycle = this_cycle[this_cycle.index(begin):]

                            # remove a random vertice from this cycle
                            rand = random.randint(0, len(cut_cycle)-1)
                            # rand = 3
                            rem_v = cut_cycle.pop(rand)
                            v_tree.append(rem_v)
                            v_rem.append(rem_v)
                            if self.plotstep: self.pl.plot_removed_step(ertype, rem_v)

                            # other vertices of the cycle are checked for tree form, added to tree if yes
                            for v in cut_cycle:
                                cn1, cn2 = self.find_neighbors_tree(ertype, v, cluster, v_tree)
                                if cn1 == [] or cn2 == []:

                                    cn = cn2 if cn1 == [] else cn1
                                    old_v = v
                                    while len(cn) == 1:
                                        new_v = cn[0]
                                        cn1, cn2 = self.find_neighbors_tree(ertype, new_v, cluster, v_tree)
                                        cn = cn2 if old_v in cn1 else cn1
                                        v_tree.append(old_v)
                                        if self.plotstep: self.pl.plot_tree_step(ertype, old_v)
                                        old_v = new_v
                                    else:
                                        v_tree.append(old_v)
                                        if self.plotstep: self.pl.plot_tree_step(ertype, old_v)

                    for v in v_tree:
                        if v in v_cycle:
                            v_cycle.remove(v)
                for v in v_rem:
                    self.cluster_list[ertype][c_i].remove(v)

                rem_list += v_rem
            self.rem_list.append(rem_list)

        if self.loadplot:
            self.pl.plot_removed(self.rem_list)
