import graph_objects as G


class bidict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            self.inverse.setdefault(value, []).append(key)

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key)
        super().__setitem__(key, value)
        self.inverse.setdefault(value, []).append(key)

    def __delitem__(self, key):
        self.inverse.setdefault(self[key], []).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super().__delitem__(key)


G = G.Graph("bla", "bla", "black")

G.add_cluster(0)
G.add_cluster(1)
G.add_vertex(0, 1, 1, True)
G.add_vertex(1, 0 ,0 ,True)
G.C[0].add_vertex(G.V[0])
G.C[1].add_vertex(G.V[1])

G.C[0].V[0].cluster

G.C[0].merge_with(G.C[1])

G.C[0].V[1].cluster

G.C[1].inherit_atr_of(G.C[0])

G.C[1].V

G.add_vertex(2, 4, 3, True)
G.C[0].add_vertex(G.V[2])
G.C[0].cID = 2

G.C[0]
G.C[1]


G.C[0].cID = G.C[1].cID
G.C[0].cID
G.C[1].cID = 2
G.C[1].cID

G.C[0] = G.C[1]
G.C[0]
hash(G.C[0])

a = [0, 1]
b = [2, 3]
c = 0

c in a and c not in b

print(a)
# class A:
#     def __init__(self,num,ind,val):
#         self.num = {'i':num,'o':num}
#         self.ID = num
#         self.C = {}
#         self.C[ind] = val
#         self.bla = None
#
#     def merge(self,B):
#         self.C.update(B.C)
#
#
#     def inherit(self,B):
#         self.__dict__.update(B.__dict__)
#
#     def __hash__(self):
#         return hash(("A",self.ID))
#
#
# class C:
#     def __init__(self,ind,val):
#         self.P = {}
#         self.P[ind] = val
#
#     def test(self, a):
#         a.bla = self
#
# a = A('a',0, 0)
# b = A('b',1, 2)
# c = C(a, b)
# D = [a,b]
#
# hash(a)
# hash(b)
#
# b.merge(a)
# a.inherit(b)
# # a = b
#
# hash(a)
# hash(b)
# b.num["i"] = "c"
# b.C[2] = 6
# a.C[3] = 6
#
# print(D)
# print(a, a.num, a.C)
# print(b, b.num, b.C)
