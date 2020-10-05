
#%%
from . import elements as el


class Ancilla_qubit(el.Ancilla_qubit):

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


class Boundary(el.Boundary):
    pass


class Data_qubit(el.Data_qubit):
    pass


class Edge(el.Edge):

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
