#ifndef PLANETFACTORY_H_
#define PLANETFACTORY_H_

#include "factory.h"
#include <object/coordinate.h>
#include <object/planet.h>

namespace dnc
{
	bool loadPlanetData(const Factory::AttributeMap& attr, GeoData& data, Coordinate& coord, Glib::ustring& name);
}

#endif /*PLANETFACTORY_H_*/
