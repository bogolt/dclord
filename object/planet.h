#ifndef PLANET_H_
#define PLANET_H_

#include "coordinate.h"
#include "account.h"

#include <glibmm/ustring.h>

#include <ostream>
#include <set>
#include <map>

namespace dnc
{

struct GeoData
{
	enum {Unknown = -1};
	// set to unknown
	GeoData();
	
	int o,e,m,t,s;
};

struct Foreign
{
	Glib::ustring owner_;
};


// general planet data
struct PlanetData
{
	GeoData geo;
	Glib::ustring name;
	Account::Id owner;
};

// TODO: buildings and harrison
struct MyPlanet
{};

struct Planet
{
	PlanetData planet_data;
	MyPlanet my_planet;
};

/*
struct KnownPlanet : public PlanetData
{
	// is the planet inhabited ( owner still can be unknown and thus empty )
	// the check is performed by the length of can_fly set
	bool isInhabited() const;
	
	Glib::ustring owner;
	
	// the set of players that can fly throght this planet ( only if inhabited )
	typedef std::set<Glib::ustring> CanFlySet;
	CanFlySet can_fly;
};
*/
typedef std::map<Coordinate, PlanetData> KnownPlanetMap;

std::ostream& operator<<(std::ostream& stream, const GeoData& g);

}

#endif /*PLANET_H_*/
