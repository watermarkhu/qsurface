
#%%
import elements_base as eb


class Ancilla_qubit(eb.Ancilla_qubit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uf_init()

    def uf_init(self):
        self.cluster = None
        self.forest = 0
        self.tree = 0

    def picker(self):
        cluster = self.cluster.parent if self.cluster else None
        return "{}-{}".format(self.__repr__(), cluster)

    def reset(self):
        super().reset()
        self.uf_init


class Boundary(eb.Boundary):
    pass


class Data_qubit(eb.Data_qubit):
    pass


class Edge(eb.Edge):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uf_init()

    def uf_init(self):
        self.support = 0
        self.peeled = 0
        self.matching = 0
        self.forest = 0

    def reset(self):
        super().reset()
        self.uf_init()


# %%
