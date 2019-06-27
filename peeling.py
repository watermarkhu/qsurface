from peeling_plot import toric_peeling_plot as tpplot
import random


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

        self.G = lat.G

        self.plot_load = lat.plot_load
        self.plotstep_tree = False
        self.plotstep_grow = False
        self.plotstep_peel = False
        self.plotstep_click = True
        self.print_steps = False

        if self.plot_load:
            self.pl = tpplot(lat, lat.LP.f, self.plotstep_click)
            self.pl.plot_lattice()


    def print_graph_stop(self, clusters=None):
        '''
        :param cID          either None, int or a list of int
        :param prestring    string to print before evertything else

        This function prints a clusters with its vertices, edges and boundary. A prestring is printed before printing everything else.
        Three different inputs can be given, to select for which clusters to print:
        1.  None:       All active clusters are printed
        2.  int:        Just one clusters with cID = int is printed
        3.  list:       The list of clusters with cID in the list are printed
        '''

        if clusters is None:
            clusters = list(self.G.C.values())
            print("\nShowing all clusters:")

        for cluster in clusters:

            if cluster.parent == cluster:
                print("\n")
                print(cluster, "with size:", cluster.size, "parity:", cluster.parity, "and halfgrown:", cluster.half_grown)
                print("Boundary:  ", end="")
                boundary = cluster.half_bound if cluster.half_grown else cluster.full_bound
                for (base_vertex, edge, _) in boundary:
                    print("[", str(base_vertex) + "-" + str(edge), "]", end=" ; ")
            else:
                print("\n", str(cluster), "is merged with", str(cluster.parent), "\n")

    def cluster_new_vertex(self, cluster, vertex):
        '''
        :param vertex           vertex that is recently added to the cluster
        :param cID              ID number of the current cluster

        For a given sID vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph. If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, otherwise it will be added to the boundary. If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
        Newly found vertices that lie within the cluster are outputted to {new_stabs}.

        '''
        random_wind = True

        if random_wind:
            random.sample(self.G.wind, 4)

        for wind in self.G.wind:
            if wind in vertex.neighbors:

                (new_vertex, new_edge) = vertex.neighbors[wind]

                if new_edge.erasure:
                    if new_edge.cluster is None and not new_edge.peeled:   # if edge not already traversed
                        if new_vertex.cluster is None:          # if no cycle detected
                            cluster.add_edge(new_edge)
                            cluster.add_vertex(new_vertex)
                            if self.plot_load and self.plotstep_tree:
                                self.pl.plot_edge_step(new_edge, "confirm")
                            self.cluster_new_vertex(cluster, new_vertex)
                        else:                                   # cycle, peel edge
                            new_edge.peeled = True
                            if self.plot_load and self.plotstep_tree:
                                self.pl.plot_edge_step(new_edge, "remove")
                else:
                    if new_vertex.cluster is not cluster:
                        cluster.add_full_bound(vertex, new_edge, new_vertex)

    def select_growth_clusters(self):

        '''
        Select which clusters are valid for growth. All uneven clusters can be grown
        {weighted_growth} toggles the selection of only the smallers uneven clusters for growth.
        Returns: boolean list of N_clusters
        '''

        weighted_growth = True

        grow_clusters = []
        grow_size = []

        for cluster in self.G.C.values():
            if cluster is cluster.parent:

                if cluster.parity % 2 == 1:
                    grow_clusters.append(cluster)
                    grow_size.append(cluster.size)

        if weighted_growth:
            if grow_clusters != []:
                minsize = min(grow_size)
                grow_clusters = [cluster for cluster, size in zip(grow_clusters, grow_size) if size == minsize]

        return grow_clusters

    def cluster_index_tree(self, cluster):
        '''
        :param cID      input cluster index, can be a branch or a base of the tree

        Loops through the {cluster_index} tree to find the base cID of the cluster index tree.
        Returns: cID, must be the base of the cluster index tree
        '''
        if cluster is not None:
            if cluster is not cluster.parent and cluster.parent is not cluster.parent.parent:
                cluster.parent = self.cluster_index_tree(cluster.parent)
            return cluster.parent
        else:
            return None


    '''
    Main functions
    '''

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

                cluster = self.G.add_cluster(cID)

                cluster.add_vertex(vertex)

                self.cluster_new_vertex(cluster, vertex)

                cID += 1

        self.G.cluster_index = [i for i in range(cID)]

        if self.plot_load and not self.plotstep_tree:
            self.pl.plot_removed("Clusters initiated")

    def grow_cluster(self, cluster, root_cluster):

        string = str(cluster) + " grown."

        if cluster.childs != [] and self.print_steps:
            print("Cluster has children:", cluster.childs)

        while cluster.childs != []:
            child_cluster = cluster.childs.pop()
            self.grow_cluster(child_cluster, root_cluster)

        if not cluster.half_grown:

            '''
            1.  First half step growth:
            '''
            while cluster.full_bound != []:

                root_cluster = self.cluster_index_tree(root_cluster)

                (base_vertex, edge, grow_vertex) = cluster.full_bound.pop()
                grow_cluster = grow_vertex.cluster
                grrt_cluster = self.cluster_index_tree(grow_cluster)

                if grrt_cluster is None:
                    edge.cluster = 0
                    root_cluster.half_bound.append((base_vertex, edge, grow_vertex))
                    if self.plot_load:
                        self.pl.add_edge(edge, base_vertex)
                else:
                    if grrt_cluster is not root_cluster:
                        if edge.cluster == 0:
                            edge.cluster = grrt_cluster
                            string += " Merged with " + str(grrt_cluster) + "."
                            root_cluster.merge_with(grrt_cluster)

                        else:
                            edge.cluster = 0
                            root_cluster.half_bound.append((base_vertex, edge, grow_vertex))
                        if self.plot_load:
                            self.pl.add_edge(edge, base_vertex)
        else:
            '''
            2.  Second half step growth:
            '''

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

                        if self.plot_load:
                            self.pl.add_edge(edge, base_vertex)

        cluster.half_grown = not cluster.half_grown
        if self.plot_load and self.plotstep_grow:
            self.pl.draw_plot(string)



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

        '''


        if self.print_steps:
            self.print_graph_stop()
            input("Press any key to continue...")

        grow_clusters = self.select_growth_clusters()

        while grow_clusters != []:

            if self.print_steps:
                print("\n############################ GROW ############################ \nGrowing clusters:", grow_clusters, "\n")

            for root_cluster in grow_clusters:

                if self.print_steps:
                    self.print_graph_stop([root_cluster])
                    print("")

                self.grow_cluster(root_cluster, root_cluster)

            if self.plot_load and not self.plotstep_grow:
                self.pl.draw_plot("Round of cluster growth.")
                if self.print_steps:
                    input()

            if self.print_steps:
                self.print_graph_stop()
                input("Press any key to continue...")

            grow_clusters = self.select_growth_clusters()


    def peel_edge(self, cluster, vertex):
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

        for vertex in self.G.V.values():
            if vertex.cluster is not None:
                cluster = self.cluster_index_tree(vertex.cluster)
                self.peel_edge(cluster, vertex)

        if self.plot_load and not self.plotstep_peel:
            self.pl.plot_removed("Peeling completed.")
