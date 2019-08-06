from peeling_plot import toric_peeling_plot as tpplot
import random


class toric:
    def __init__(self, lat, anyon_order="random", random_traverse=1, intervention=0):
        '''
        :param lat                  lattice object from toric_lat.py
        :param anyon_order          Random order on cluster finding order: row_row, random, neighbor_count or rev_count
        :param random_traverse      Random order on traversing direction of the tree
        :param intervention         Intervention on merge during growth

        The graph objects, lattice size and plot toggle is taken from the lattice object.
        Some options can be toggled for stepwise plotting during the decoder operation. {plotstep_tree} toggles stepwise plotting during the cluster initialization, {potstep_grow} toggles stepwise plotting during cluster growth, and {plotstep_peel} toggles stepwise plotting during the peeling operation. {plotstep_click} toggles user interaction after each plot step. {print_steps} enables some extra information of the clusters and buckets during cluster growth.
        The buckets and the wastebasket are also initialzed here.
        '''
        self.G = lat.G
        self.size = lat.size
        self.plot_load = lat.plot_load
        self.plot_size = lat.plot_size

        self.plotstep_tree = 1
        self.plotstep_grow = 1
        self.plotstep_peel = 0
        self.plotstep_click = 0
        self.print_steps = 0

        self.numbuckets = self.size - self.size % 2
        self.buckets = [[] for _ in range(self.numbuckets)]
        self.buckmax = [(i+1)**2 + (i+2)**2 for i in range(self.size//2)]
        self.wastebasket = []
        self.maxbucket = 0

        self.anyon_order = anyon_order
        self.random_traverse = random_traverse
        self.intervention = intervention

        if self.plot_load:
            self.pl = tpplot(lat, lat.LP.f, self.plotstep_click)
            self.pl.plot_lattice()

    '''
    Printing functions:
    '''

    def print_graph_stop(self, clusters=None, prestring=""):
        '''
        :param clusters     either None or a list of clusters
        :param prestring    string to print before evertything else

        This function prints a cluster's size, parity, growth state and appropiate bucket number. If None is inputted, all clusters will be displayed.
        '''

        if clusters is None:
            clusters = list(self.G.C.values())
            print("\nShowing all clusters:")

        for cluster in clusters:

            if cluster.parent == cluster:
                print(prestring + str(cluster), end="")
                print(" with size: " + str(cluster.size), end="")
                print(", parity: " + str(cluster.parity), end="")
                print(", full edged: " + str(cluster.full_edged), end="")
                if cluster.bucket is None:
                    print(", and bucket: " + str(cluster.bucket))
                else:
                    if cluster.bucket < self.numbuckets:
                        print(", and bucket: " + str(cluster.bucket))
                    else:
                        print(", and bucket: wastebasket")
            else:
                print(str(cluster), "is merged with", str(cluster.parent))

    '''
    Helper functions:
    '''

    def cluster_place_bucket(self, cluster, merge=False):
        '''
        :param cluster      current cluster

        The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropiate bucket number of the cluster intil the fitting bucket has been reached. The cluster is then appended to that bucket.
        If the max bucket number has been reached. The cluster is appended to the wastebasket, which will never be selected for growth.
        '''
        if cluster.bucket is None:
            cluster.bucket = 2*int(-((1.5 - .25*(-4+8*cluster.size + 1)**(1/2))//1))
        else:
            if cluster.bucket < self.numbuckets:
                if cluster.size >= self.buckmax[cluster.bucket//2]:
                    cluster.bucket = 2*int(-((1.5 - .25*(-4+8*cluster.size + 1)**(1/2))//1))

        if not cluster.full_edged:                      # Additional level added if currently in growth state 1
            cluster.bucket += 1

        if cluster.bucket < self.numbuckets:
            if cluster.parity % 2 == 1:
                self.buckets[cluster.bucket].append(cluster)
                if cluster.bucket > self.maxbucket:
                    self.maxbucket = cluster.bucket
            else:
                cluster.bucket = None
        else:
            self.wastebasket.append(cluster)

    '''
    Helper recursive functions:
    '''

    def cluster_new_vertex(self, cluster, vertex):
        '''
        :param cluster          current cluster
        :param vertex           vertex that is recently added to the cluster

        Recursive function which adds all connected erasure edges to a cluster, or finds the boundary on a vertex.

        For a given vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph.
        If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, and the function is started again on the new vertex. Otherwise it will be added to the boundary.
        If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
        '''

        traverse_wind = random.sample(self.G.wind, 4) if self.random_traverse else self.G.win

        for wind in traverse_wind:
            if wind in vertex.neighbors:
                (new_vertex, new_edge) = vertex.neighbors[wind]

                if new_edge.erasure:
                    if new_edge.cluster is None and not new_edge.peeled:    # if edge not already traversed
                        if new_vertex.cluster is None:                      # if no cycle detected
                            cluster.add_edge(new_edge)
                            cluster.add_vertex(new_vertex)
                            if self.plot_load and self.plotstep_tree:
                                self.pl.plot_edge_step(new_edge, "confirm")
                            self.cluster_new_vertex(cluster, new_vertex)
                        else:                                               # cycle detected, peel edge
                            new_edge.peeled = True
                            if self.plot_load and self.plotstep_tree:
                                self.pl.plot_edge_step(new_edge, "remove")
                else:
                    if new_vertex.cluster is not cluster:                   # Make sure new bound does not lead to self
                        cluster.add_full_bound(vertex, new_edge, new_vertex)


    def cluster_index_tree(self, cluster):
        '''
        :param cluster      input cluster

        Loops through the cluster tree to find the root cluster of the given cluster. When the parent cluster is not at the root level, the function is started again on the parent cluster. The recursiveness of the function makes sure that at each level the parent is pointed towards the root cluster, furfilling the collapsing rule.
        '''
        if cluster is not None:
            if cluster is not cluster.parent and cluster.parent is not cluster.parent.parent:
                cluster.parent = self.cluster_index_tree(cluster.parent)
            return cluster.parent
        else:
            return None

    '''
    Main recursive functions
    '''

    def grow_cluster(self, cluster, root_cluster, full_edged, family_growth=True):
        '''
        :param cluster          the current cluster selected for growth
        :param root_cluster     the root cluster of the selected cluster
        :param full_edged       determines the growth state of the initial root cluster
        :family_growth          detemines whether growth happens on parent or child cluster

        Recursive function which first grows a cluster's children and then itself.

        There are two distinct growth steps. 1) first half step from a given vertex, the cluster size does not increase, no new edges or vertices are added to the cluster, except for during a merge. 2) second half step in which a new vertex is reached, and the edge is added to the cluster.
        During the inital {find_clusters} function, the initial boundary, which contains edges ready for growth step 1, are added to {full_bound}. {half_bound} which contains the boundary edges for growth step 2, is yet empty. From here, clusters from even buckets go into growth step 1 on edges from {full_bound}, and clusters from uneven buckets go into growth step 2 on edges from "half_bound". New boundary edges are added to the other boundary list.
        After growth, the cluster is placed into a new bucket using {cluster_place_bucket}. If a merge happens, the root cluster of the current cluster is made a child of the pendant root_cluster. And the pendant root cluster is placed in a new bucket instead.
        If a cluster has children, these clusters are grown first. The new boundaries from these child clusters are appended to the root_cluster. Such that a parent does not need to remember its children.
        '''

        root_level = True if cluster == root_cluster else False         # Check for root at beginning
        string = str(cluster) + " grown."

        if cluster.foster != [] and self.print_steps:
            print(cluster, "has fosters:", cluster.foster)
        while cluster.foster != []:
            foster_cluster = cluster.foster.pop()
            self.grow_cluster(foster_cluster, root_cluster, full_edged, family_growth=False)

        if family_growth:
            if cluster.childs != [] and self.print_steps:
                print(cluster, "has children:", cluster.childs)
            while cluster.childs != []:                                 # First go through child clusters
                child_cluster = cluster.childs.pop()
                self.grow_cluster(child_cluster, root_cluster, full_edged)

        merge_cluster = None

        if full_edged:                               # 1.  First half step growth:
            if family_growth:
                cluster.full_edged = False

            if self.random_traverse:
                cluster.full_bound.reverse()

            while cluster.full_bound != []:
                root_cluster = self.cluster_index_tree(root_cluster)
                (base_vertex, edge, grow_vertex) = cluster.full_bound.pop()
                grow_cluster = grow_vertex.cluster
                grrt_cluster = self.cluster_index_tree(grow_cluster)

                if grrt_cluster is None:
                    edge.cluster = 0                # 0 value to indicate half-grown status
                    root_cluster.half_bound.append((base_vertex, edge, grow_vertex))
                    if self.plot_load:
                        self.pl.add_edge(edge, base_vertex)
                else:
                    if grrt_cluster is not root_cluster:
                        if edge.cluster == 0:
                            edge.cluster = grrt_cluster
                            string += " Merged with " + str(grrt_cluster) + "."
                            root_cluster.merge_with(grrt_cluster)
                            merge_cluster = grrt_cluster
                            if self.plot_load:
                                self.pl.add_edge(edge, base_vertex)
                            if self.intervention and family_growth and grrt_cluster.parity % 2 == 0:
                                grrt_cluster.foster.append(root_cluster)
                                if self.print_steps:
                                    print("intervention on merge.")
                                break
                        else:
                            edge.cluster = 0
                            root_cluster.half_bound.append((base_vertex, edge, grow_vertex))
                            if self.plot_load:
                                self.pl.add_edge(edge, base_vertex)

        else:                                       # 2.  Second half step growth:
            if family_growth:
                cluster.full_edged = True
            while cluster.half_bound != []:
                root_cluster = self.cluster_index_tree(root_cluster)
                (base_vertex, edge, grow_vertex) = cluster.half_bound.pop()
                grow_cluster = grow_vertex.cluster
                grrt_cluster = self.cluster_index_tree(grow_cluster)

                if grrt_cluster is None:
                    edge.cluster = root_cluster
                    root_cluster.add_vertex(grow_vertex)
                    self.cluster_new_vertex(root_cluster, grow_vertex)
                    if self.plot_load:
                        self.pl.add_edge(edge, base_vertex)
                else:
                    if grrt_cluster is not root_cluster:
                        edge.cluster = grrt_cluster
                        string += " Merged with " + str(grrt_cluster) + "."
                        root_cluster.merge_with(grrt_cluster)
                        merge_cluster = grrt_cluster
                        if self.plot_load:
                            self.pl.add_edge(edge, base_vertex)
                        if self.intervention and family_growth and grrt_cluster.parity % 2 == 0:
                            grrt_cluster.foster.append(root_cluster)
                            if self.print_steps:
                                print("intervention on merge.")
                            break

        if root_level:          # only at the root level will a cluster be placed in a new bucket
            if merge_cluster is None:
                self.cluster_place_bucket(root_cluster)
            else:
                self.cluster_place_bucket(merge_cluster, merge=True)

        if self.plot_load and self.plotstep_grow:
            self.pl.draw_plot(string)
        if self.print_steps and root_level:
            print_cluster = root_cluster if merge_cluster is None else merge_cluster
            self.print_graph_stop([print_cluster], prestring="A: ")
            if self.plot_load and self.plotstep_click:
                self.pl.waitforkeypress()
            else:
                if self.plotstep_click:
                    input("Press any key to continue...")

    def peel_edge(self, cluster, vertex):
        '''
        :param cluster          current active cluster
        :param vertex           pendant vertex of the edge to be peeled

        Recursive function which peels a branch of the tree if the input vertex is a pendant vertex

        If there is only one neighbor of the input vertex that is in the same cluster, this vertex is a pendant vertex and can be peeled. The function calls itself on the other vertex of the edge leaf.
        '''
        num_connect = 0
        for wind in self.G.wind:
            (NV, NE) = vertex.neighbors[wind]
            if NE.cluster != 0:
                new_cluster = self.cluster_index_tree(NE.cluster)
                if new_cluster is cluster and not NE.peeled:
                    num_connect += 1
                    edge, new_vertex = NE, NV
            if num_connect > 1:
                break
        if num_connect == 1:
            edge.peeled = True
            if vertex.state:
                edge.matching = True
                vertex.state = False
                new_vertex.state = not new_vertex.state
                if self.plot_load and self.plotstep_peel:
                    self.pl.plot_edge_step(edge, "match")
                    self.pl.plot_strip_step_anyon(vertex)
                    self.pl.plot_strip_step_anyon(new_vertex)
            else:
                if self.plot_load and self.plotstep_peel:
                    self.pl.plot_edge_step(edge, "peel")
            self.peel_edge(cluster, new_vertex)

    '''
    Main functions
    '''

    def find_clusters(self):
        '''
        Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected and sorts them in separate clusters. A single anyon can also be its own cluster.
        It loops over all vertices (randomly if toggled, which produces a different tree), and calls {cluster_new_vertex} to find all connected erasure qubits, and finds the boundary for growth step 1. Afterwards the cluster is placed in a bucket based in its size.

        '''
        cID = 0

        vertices = self.G.V.values()

        if self.anyon_order in ["row_row", ""]:
            anyons = [vertex for vertex in vertices if vertex.state]
        elif self.anyon_order == "random":
            vertices = random.sample(set(vertices), len(vertices))
            anyons = [vertex for vertex in vertices if vertex.state]
        elif self.anyon_order == "neighbor_count":
            count_lists = [[] for _ in range(len(self.G.wind) + 1)]
            for vertex in vertices:
                if vertex.state:
                    count = 0
                    for neighbor in [vertex.neighbors[wind][0] for wind in self.G.wind]:
                        if neighbor.state:
                            count += 1
                    vertex.count = count
                    count_lists[count].append(vertex)
                else:
                    vertex.count = 0
            anyons = []
            while count_lists != []:
                anyons += count_lists.pop()
        elif self.anyon_order == "rev_count":
            count_lists = [[] for _ in range(len(self.G.wind) + 1)]
            for vertex in vertices:
                if vertex.state:
                    count = 0
                    for neighbor in [vertex.neighbors[wind][0] for wind in self.G.wind]:
                        if neighbor.state:
                            count += 1
                    vertex.count = count
                    count_lists[count].append(vertex)
                else:
                    vertex.count = 0
            anyons = [item for sublist in count_lists for item in sublist]

        for vertex in anyons:
            if vertex.cluster is None:

                cluster = self.G.add_cluster(cID)
                cluster.add_vertex(vertex)
                self.cluster_new_vertex(cluster, vertex)
                self.cluster_place_bucket(cluster)
                cID += 1

        if self.plot_load and not self.plotstep_tree:
            self.pl.plot_removed("Clusters initiated")


    def grow_bucket(self):
        '''
        Grows the clusters, and merges them until there are no uneven clusters left.
        Starting from the lowest bucket, clusters are popped from the list and grown with {grow_cluster}. Due to the nature of how clusters are appended to the buckets, a cluster needs to be checked for 1) root level 2) bucket level and 3) parity before it can be grown.

        '''
        if self.print_steps:
            self.print_graph_stop()
            if self.plot_load:
                self.pl.waitforkeypress()
            else:
                input("Press any key to continue...")

        for grow_bucket in range(self.size):

            if grow_bucket > self.maxbucket:                                # Break from upper buckets if top bucket has been reached.
                if self.plot_load or self.print_steps:
                    txt = "Max bucket number reached."
                    if self.plot_load:
                        self.pl.waitforkeypress(txt)
                    else:
                        input(txt + " Press any key to continue...\n")
                break

            if self.print_steps:
                print("\n############################ GROW ############################")
                print("Growing bucket", grow_bucket, "of", self.maxbucket, ":", self.buckets[grow_bucket])
                print("All buckets:", self.buckets, self.wastebasket)
                if self.plot_load:
                    self.pl.waitforkeypress()
                    print("")
                else:
                    input("Press any key to continue...\n")

            while self.buckets[grow_bucket] != []:                          # Loop over all clusters in the current bucket

                cluster = self.buckets[grow_bucket].pop()
                root_cluster = self.cluster_index_tree(cluster)

                if root_cluster is cluster:                                 # Check that cluster is at root. Otherwise merged onto another
                    if root_cluster.bucket == grow_bucket:                  # Check that cluster is not already in a higher bucket

                        if self.print_steps:
                            self.print_graph_stop([root_cluster], prestring="B: ")

                        self.grow_cluster(root_cluster, root_cluster, root_cluster.full_edged)

                        if self.print_steps:
                            print("")
                    else:
                        if self.print_steps:
                            if root_cluster.bucket is None:
                                print(root_cluster, "is even.\n")
                            else:
                                if root_cluster.bucket > self.maxbucket:
                                    print(root_cluster, "is already in the wastebasket\n")
                                else:
                                    print(root_cluster, "is already in another bucket.\n")
                else:
                    if self.print_steps:
                        print(cluster, "is not at root level (" + str(root_cluster) + ").\n")

            if self.plot_load and not self.plotstep_grow:
                self.pl.draw_plot("Growing bucket #" + str(grow_bucket) + "/" + str(self.maxbucket) + ".")
                if self.print_steps and self.plotstep_click:
                    input()
            elif self.plot_load:
                print("Growing bucket #" + str(grow_bucket) + "/" + str(self.maxbucket) + ".")


        if self.print_steps:
            self.print_graph_stop()
            if self.plot_load and self.plotstep_click:
                self.pl.waitforkeypress()
            else:
                if self.plotstep_click:
                    input("Press any key to continue...")



    def peel_trees(self):
        '''
        Loops overal all vertices to find pendant vertices which are selected from peeling using {peel_edge}

        '''
        for vertex in self.G.V.values():
            if vertex.cluster is not None:
                cluster = self.cluster_index_tree(vertex.cluster)
                self.peel_edge(cluster, vertex)

        if self.plot_load and not self.plotstep_peel:
            self.pl.plot_removed("Peeling completed.")
