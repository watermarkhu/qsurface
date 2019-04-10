import os

cwd = os.getcwd()

testgraph=[[1,2,10],[1,3,25],[0,2,56],[0,1,15],[2,3,6]]
numNode = 4
numGraph = len(testgraph)

# Write the graph to a list of edges
input_file = open("graph.txt", "w", encoding="UTF-8")
input_file.write(str(numNode) + " " + str(numGraph) + "\n")
for graph in testgraph:
    line = str(graph[0]) + " " + str(graph[1]) + " " + str(graph[2]) + "\n"
    input_file.write(line)
input_file.close()

# Run C++ code from the command line, save results to file
cmd_command = "cd " + cwd + "& blossom5 -e graph.txt -w results.txt"
os.system(cmd_command)

# Read output file
with open("results.txt") as f:
    lines = f.readlines()
result = []
for line in lines:
    result.append([int(line[0]),int(line[2])])
result = result[1:]

print(result)