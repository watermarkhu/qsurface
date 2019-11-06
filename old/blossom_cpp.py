import os


def blossom(numNode, edges):

    cwd = os.getcwd()
    numGraph = len(edges)

    # Write the graph to a list of edges
    input_file = open("./blossom5/graph.txt", "w", encoding="UTF-8")
    input_file.write(str(numNode) + " " + str(numGraph) + "\n")
    for graph in edges:
        line = str(graph[0]) + " " + str(graph[1]) + " " + str(graph[2]) + "\n"
        input_file.write(line)
    input_file.close()

    # Run C++ code from the command line, save results to file
    cmd_command = "cd " + cwd + "/blossom5 & blossom5 -e graph.txt -w results.txt -V"
    os.system(cmd_command)

    # Read output file
    with open("./blossom5/results.txt") as f:
        lines = f.readlines()
    result = []
    for line in lines[:]:
        split = line.split(" ")
        result.append([int(split[0]), int(split[1])])
    result = result[1:]

    # delete files
    cmd_command = "cd " + cwd + "/blossom5 & del graph.txt & del results.txt"
    os.system(cmd_command)

    return result
