#include <time.h>>
#include <stdio.h>


inline double get_time()
{
	struct timespec t;
	clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t);
	return (double)t.tv_nsec*1.00E-9 + (double)t.tv_sec;
}

int main()
{ 
double result = get_time();
printf("%f \n",result);
return 0;
}
