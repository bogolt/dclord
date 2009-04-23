#include "planet.h"

namespace dnc{

GeoData::GeoData()
:o(Unknown), e(Unknown), m(Unknown), t(Unknown), s(Unknown)
{}

std::ostream& operator<<(std::ostream& stream, const GeoData& g)
{
	return stream << g.o << " " << g.e << " " << g.m << " " << g.t << " " << g.s;
}

//bool KnownPlanet::isInhabited() const
//{
//	return !can_fly.empty();
//}

}
