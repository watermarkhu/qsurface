import blossom_cpp as bl

testgraph=[[1,2,10],[1,3,25],[0,2,56],[0,1,15],[2,3,6]]
numNode = 4

result = bl.blossom(numNode,testgraph)

print(result)