#include "point.h"
#include <cmath>

const double eps = 0.00001;

bool eq(int a, int b)
{
	return a == b;
}

bool eq(double a, double b)
{
	return fabs(a-b) < eps;  
}
