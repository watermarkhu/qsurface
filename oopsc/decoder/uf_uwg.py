'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

The Union-Find decoder as described by arXiv:1709.06218v1

An OOP implementation has been made here, where the boundary and support are not stored as separate lists, which have to accesed based on some key value of the cluster. We store the boundary list and support for each cluster, and other paramters, directly at the cluster object.
The decoder requires a graph object, containing the vertices (stabilizers) and edges (qubits) of the uf-lattice. The graph can either be 2D (perfect measurements) or 2D (noisy measurements).
Two decoder classes are defined in this file, toric and planar for their respective lattice types.
'''


from ..info.decorators import debug, plot
from ..info import printing as pr
from . import uf

class toric(uf.toric):
    '''
    Union-Find decoder for the toric lattice (2D and 3D)
    '''
    @debug.init_counters_uf()
    def __init__(self, plot_config=None, *args, **kwargs):
        '''
        Optionally acceps config dict which contains plotting options.
        Counters for decoder specific heuristics are initialized.
        Decoder options, defined in kwargs are stored as class variables.
        '''
        super().__init__(*args, **kwargs)
        self.type = "uf_uwg"


    '''
    ##################################################################################################

                                        General helper funtions

    ##################################################################################################
    '''

    def cluster_place_bucket(self, cluster, *args, **kwargs):
        """
        :param cluster      current cluster
        
        Place cluster in new bucket if 
        """
        if (cluster.parity % 2 == 1 and not cluster.on_bound) and cluster.bucket == 0:
            self.buckets[-1].append(cluster)
            cluster.bucket = 1


    def init_buckets(self):
        '''
        initializes buckets for bucket growth
        '''
        self.buckets = [[]]
        self.maxbucket = -1
        self.wastebucket = "unknown in uf_uwg"

    @plot.iter(name="Clusters grown", cname="plot_growth", flip=False)
    def grow_clusters(self, start_bucket=0, *args, **kwargs):
        '''
        Loops over all buckets to grow each bucket iteratively.
        Skips empty buckets during loop and breaks out when the largest bucket has been reached (defined by self.maxbucket)
        '''
        if self.print_steps:
            pr.print_graph(self.graph)

        bucket_i = 0
        while self.buckets[-1]:
            bucket = self.buckets[-1]
            self.buckets.append([])
            self.grow_bucket(bucket, bucket_i)
            self.fuse_bucket(bucket_i)

            if self.print_steps:
                pr.print_graph(self.graph, printmerged=0)

            bucket_i += 1

    @debug.counter(name="gbu")
    @plot.iter_grow_bucket()
    def grow_bucket(self, bucket, bucket_i, *args, **kwargs):
        '''
        Grows the clusters which are contained in the current bucket.
        Skips the cluster if it is already contained in a higher bucket or if the support parameters does not equal the current bucket support
        '''
        self.place, self.fusion = [], []
        for cluster in bucket:
            cluster = self.get_cluster_root(cluster)
            if cluster.bucket == 1:
                self.place.append(cluster)
                self.grow_boundary(cluster)
                cluster.bucket = 0

class planar(uf.planar, toric):
    pass
