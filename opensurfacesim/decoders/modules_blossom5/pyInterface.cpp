#include <stdio.h>
#include "PerfectMatching.h"
#include "GEOM/GeomPerfectMatching.h"



extern "C" {

int* pyMatching(int node_num, int edge_num, int nodes1[], int nodes2[], int weights[])
{
	
	struct PerfectMatching::Options options;
	
	char* filename = NULL;
	bool check_perfect_matching = false;
	//int i, e, node_num, edge_num;
	int* edges;
	
	//int edge_num=sizeof(*nodes1);
	//printf("%d\n" sizeof(nodes1));
	//edges=

	
	//printf("%d %d\n",node_num,edge_num);
	
	//print the input
//	for(int k=0; k<edge_num; ++k)
//	{
//		printf("%d %d %d \n",nodes1[k],nodes2[k],weights[k]);
//	}

	
	PerfectMatching *pm = new PerfectMatching(node_num,edge_num);
	
	for(int k=0; k<edge_num;++k)	
	{
		pm->AddEdge(nodes1[k],nodes2[k],weights[k]);
	}

	pm->options = options;
	pm->Solve();
;

	int i, j;
	int* out = new int[node_num];
	for (i=0; i<node_num; i++)
	{
		j = pm->GetMatch(i);
		out[i]=j;
		//if (i < j) printf("%d %d\n", i, j);
	}



	




//	if (check_perfect_matching)
//	{
//		int res = CheckPerfectMatchingOptimality(node_num, //edge_num, edges, weights, pm);
//		printf("check optimality: res=%d (%s)\n", res, (res==0) ? "ok" : ((res==1) ? "error" : "fatal error"));
//	}

//	double cost = ComputePerfectMatchingCost(node_num, edge_num, edges, weights, pm);
//	printf("cost = %.1f\n", cost);
	//if (save_filename) SaveMatching(node_num, pm, save_filename);
	delete pm;
	
	if (filename)
	{
		delete [] edges;
		delete [] weights;
	}
	


	
	return out;
}

}
