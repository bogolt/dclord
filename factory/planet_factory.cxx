#include "planet_factory.h"
#include <sstream>

namespace dnc
{

bool loadPlanetData(const Factory::AttributeMap& attr, GeoData& data, Coordinate& coord, Glib::ustring& name)
{
	// as we deal with standard ascii symbols it is possible to convert them using std::istringstream
	LOAD_ATTR(attr, "o", data.o);
	LOAD_ATTR(attr, "e", data.e);
	LOAD_ATTR(attr, "m", data.m);
	LOAD_ATTR(attr, "temperature", data.t);
	LOAD_ATTR(attr, "surface", data.s);
	
	Coordinate::Coord x,y; 
	LOAD_ATTR(attr, "x", x);
	LOAD_ATTR(attr, "y", y);	

	coord = Coordinate(x, y);
	
	Factory::AttributeMap::const_iterator it = attr.find("name");
	if(it != attr.end())
		name = it->second;

	return true;
}

}
