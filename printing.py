import logging

def printlog(message, print_message=True, log_message=False):
    if print_message:
        print(message)
    if log_message:
        logging.warning(message)

def print_graph(graph, clusters=None, prestring="", poststring=None, printmerged=1, return_string=False):
    """
    :param clusters     either None or a list of clusters
    :param prestring    string to print before evertything else

    This function prints a cluster's size, parity, growth state and appropiate bucket number. If None is inputted, all clusters will be displayed.
    """
    string = ""
    if clusters is None:
        clusters = list(graph.C.values())
        string += "Showing all clusters:\n"

    for cluster in clusters:
        if cluster.parent == cluster:
            string += prestring + f"{cluster} (S{cluster.support},"
            if cluster.bucket is None:
                string += f" B{cluster.bucket})"
            else:
                if cluster.bucket < graph.numbuckets:
                    string += f"B{cluster.bucket})"
                else:
                    string += f"B_)"
            if cluster.cID != clusters[-1].cID: string += "\n"
        elif printmerged:
            string += str(cluster) + " is merged with " + str(cluster.parent) + ""
            if cluster is not clusters[-1]: string += "\n"
    if poststring is not None:
        string += "\n" + poststring
    if return_string:
        return string
    else:
        printlog(string)
