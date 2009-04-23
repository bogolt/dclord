#include "building_class.h"

#include <iostream>

namespace dnc
{

BuildingClass::BuildingClass()
:Factory("building-types", "building_class")
{
}

bool BuildingClass::setAttributes(const AttributeMap&)
{
	return false;
}

bool BuildingClass::create(const AttributeMap&)
{
	static int i = 0;
	using namespace std;
	cout << "new class " << ++i << endl;
	return true;
}

}
