#ifndef ACCOUNT_H_
#define ACCOUNT_H_

#include "coordinate.h"

#include <glibmm/ustring.h>

#include <boost/smart_ptr.hpp>

#include <ostream>
#include <map>

namespace dnc
{

class Planet;

class Account
{
public:
	Account(const Glib::ustring& n = "");
	typedef unsigned int Id;
	
	Glib::ustring name;
	
	typedef boost::weak_ptr<Planet> OwnedPlanet;
	typedef std::map<Coordinate, OwnedPlanet> OwnedPlanetMap;
	
	OwnedPlanetMap owned_planets;
	Coordinate homeworld;
};

}

#endif /*ACCOUT_H_*/
