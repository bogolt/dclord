#include "galaxy.h"

namespace db
{

using namespace dnc;


GalaxyCl::GalaxyCl()
{

	GalaxyData map;
	{
		const Coordinate c(1102,1103);
		map[c].planet.planet_data.name = "Houme";
		map[c].planet.planet_data.owner = 1;
	}
	{
		const Coordinate c(1112,1113);
		map[c].planet.planet_data.name = "warg";
	}
	{
		const Coordinate c(1107,1113);
		map[c].planet.planet_data.name = "русский терк";
	}
	{
		const Coordinate c(1102,1107);
		map[c].planet.planet_data.name = "Houme смесь";
	}
	
	data.swap(map);
	
	AccountMap acc;
	acc[1] = Account("user");
	
	accounts.swap(acc);
}

void GalaxyCl::known_planets(GalaxyData& known_planets)
{
	GalaxyData temp(data);
	known_planets.swap(temp);
}

Cell GalaxyCl::planet(const dnc::Coordinate& c) const
{
	GalaxyData::const_iterator it = data.find(c);
	return it != data.end() ? it->second : Cell();
}

Account GalaxyCl::account(Account::Id id) const
{
	AccountMap::const_iterator it = accounts.find(id);
	return it != accounts.end() ? it->second : dnc::Account();
}

}
