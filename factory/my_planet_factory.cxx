#include "my_planet_factory.h"

#include "planet_factory.h"

#include <sstream>
#include <iostream>

namespace dnc
{

MyPlanetFactory::MyPlanetFactory()
:Factory("user-planets", "planet")
{
}

bool MyPlanetFactory::setAttributes(const AttributeMap&)
{
	// currently no attrubutes supported
	return true;
}

bool MyPlanetFactory::create(const AttributeMap& attr)
{
	GeoData geo;
	Coordinate coord;
	Glib::ustring name;
	if(!loadPlanetData(attr, geo, coord, name))
		return false;
	
	bool is_hidden;
	LOAD_ATTR(attr, "hidden", is_hidden);
	
	int corruption;
	LOAD_ATTR(attr, "corruption", corruption);
	
	int population;
	LOAD_ATTR(attr, "population", population);
	
	using namespace std;
	cout << coord << " " << geo << " " << is_hidden << " " << corruption << " " << population << endl;
	return true;
}

}
