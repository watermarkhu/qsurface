import sys
sys.path.append("../")
from matplotlib import pyplot as plt
from cposguf_run import input_error_array, sql_connection, fetch_query
from cposguf_plotcompare import plot_both
import cposguf_cluster_actions as cca
import graph_objects as go
import toric_code as tc
import unionfind_tree as uf


def get_grown_from_graph(graph):
    qubits_grown, qubits_matching = [], []
    for qubit in [graph.E[(0, y, x, td)] for y in range(graph.size) for x in range(graph.size) for td in range(2)]:
        if qubit.support == 2:
            qubits_grown.append(qubit.qID[1:])
            if qubit.matching:
                qubits_matching.append(qubit.qID[1:])
    return qubits_grown, qubits_matching


def get_states_from_graph(graph):
    '''
    Returns the qubits in the graph that have value 1
    '''
    return [(y, x, td) for y in range(graph.size) for x in range(graph.size) for td in range(2) if graph.E[(0, y, x, td)].state]



def analyze_sim2_A(lattice, array):

    graph = go.init_toric_graph(lattice)
    # graph_v = go.init_toric_graph(lattice)
    # plot_both(graph, graph_v, array)

    input_error_array(graph, array)
    tc.measure_stab(graph)
    # initial_state = get_states_from_graph(graph)
    uf.find_clusters(graph)
    uf.grow_clusters(graph, vcomb=0)
    uf.peel_clusters(graph)
    ugs, ups = get_grown_from_graph(graph)
    # tc.apply_matching_peeling(graph)
    # ufs = get_states_from_graph(graph)


    graph.reset()

    input_error_array(graph, array)
    tc.measure_stab(graph)
    uf.find_clusters(graph, vcomb=1)
    uf.grow_clusters_full(graph, vcomb=1)
    uf.peel_clusters(graph)
    vgs, vps = get_grown_from_graph(graph)
    # tc.apply_matching_peeling(graph)
    # vfs = get_states_from_graph(graph)


    graph.reset()

    # efs, cfs = (ufs, vfs) if type else (vfs, ufs)
    #
    # e_dict_clusters = cca.get_clusters_from_list(efs, lattice)
    #
    # logical_qubits = cca.get_logical_cluster(e_dict_clusters, lattice)
    #
    # peel_union = set(ups) | set(vps)
    # peel_dict = cca.get_clusters_from_list(list(peel_union), lattice)
    #
    # involved_qubits = set(ufs) | set(vfs)
    #
    # for cluster in peel_dict.values():
    #     for qubit in cluster:
    #         if qubit in involved_qubits:
    #             involved_qubits = involved_qubits | set(cluster)
    #             break
    #
    # involved_errors = set(initial_state) & (set(involved_qubits))
    #
    # plt.figure(3)
    # i = 1
    # py, px = 4, 3
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("Errors")
    # cca.plot_cluster(initial_state, lattice-1, lattice-1, ax=ax, color='r')
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("UBUCK grown state (UGS)")
    # cca.plot_cluster(ugs, lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("VCOMB grown state (VGS)")
    # cca.plot_cluster(vgs, lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("UGS ^ VGS")
    # cca.plot_cluster(set(ugs) ^ set(vgs), lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("UBUCK matching (UM)")
    # cca.plot_cluster(ups, lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("VCOMB matching (VM)")
    # cca.plot_cluster(vps, lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("UM $\cup$ VM")
    # cca.plot_cluster(peel_union , lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("UBUCK end state (UES)")
    # cca.plot_cluster(ufs, lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("VCOMB end state (VES)")
    # cca.plot_cluster(vfs, lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("Logical qubits")
    # cca.plot_cluster(logical_qubits, lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("Involved qubits")
    # cca.plot_cluster(involved_qubits, lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # ax = plt.subplot(py, px ,i)
    # ax.set_title("Involved errors")
    # cca.plot_cluster(involved_errors, lattice-1, lattice-1, ax=ax)
    # i += 1
    #
    # plt.show()

    # plot_both(graph, graph_v, list(map(list, zip(*involved_errors))))
    return len(ups), len(vps)

p = None
l = 12
extra = None

con, cur = sql_connection("../cposguflocal.ini")
query = fetch_query("lattice, p, vcomb_solved, error_data", p, l, extra=extra, limit=None)
cur.execute(query)
sims = cur.fetchall()

cur.close()
con.close()

uc, us, vc, vs = 0, 0, 0, 0
for lattice, p, type, array in sims:
    ul, vl = analyze_sim2_A(lattice, array)
    analyze_sim2_A(lattice, array)
    if type == 0: #UBUCK
        us += 1
        if ul < vl: uc += 1
    elif type == 1: # VCOMB
        vs += 1
        if vl < ul: vc += 1

print("UBUCK win: ubuck has less qubits in matching: {0:d}/{1:d} = {2:3.3f}%".format(uc, us, uc/us*100))
print("VCOMB win: vcomb has less qubits in matching: {0:d}/{1:d} = {2:3.3f}%".format(vc, vs, vc/vs*100))
