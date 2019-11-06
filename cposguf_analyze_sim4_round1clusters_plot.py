import pickle
from collections import defaultdict as dd


def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def d1(): return [0,0]
def d2(): return dd(d1)

data = load_obj("sim3_data")



def sort_data(data, type=None):
    if type == None:
        sortdata = sorted(data.items(),
            key=lambda kv:
            sum([v1 + v2 for v1, v2 in list(kv[1].values())]),
            reverse = True
        )
    elif type in data:
        sortdata = sorted(data.items(),
            key=lambda kv:
            sum(kv[type]),
            reverse = True
        )
    else:
        raise(KeyError)
    return sortdata


sdp = sort_data(data["data_p"])



# fig = cca.plot_clusters(clusters, count, plotnum)
#
# folder = "../../../OneDrive - Delft University of Technology/MEP - thesis Mark/Simulations/cposguf_sim3_round1clusters/"
# file_name = "cposguf_sim3_L-"
# file_name += "None_p-" if l is None else "{0:d}_p-".format(l)
# file_name += "None" if p is None else "{0:.3f}".format(p)
# fname = folder + "figures/" + file_name + ".pdf"
# fig.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
# plt.close(fig)
#
# f = open(folder + "data/" + file_name + ".txt", "w")
# f.write("Count: " + str(count))
# for line in clusters:
#     f.write(str(line) + "\n")
# f.close()
