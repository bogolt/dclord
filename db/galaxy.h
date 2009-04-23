#ifndef GALAXY_H_
#define GALAXY_H_

#include <object/cell.h>

#include <boost/thread/detail/singleton.hpp>

#include <map>

namespace db
{

typedef std::map<dnc::Coordinate, dnc::Cell> GalaxyData;
typedef std::map<dnc::Account::Id, dnc::Account> AccountMap;

class GalaxyCl
{
public:
	void known_planets(GalaxyData& known_planets);
	dnc::Cell planet(const dnc::Coordinate& c) const;
	dnc::Account account(dnc::Account::Id id) const;
protected:
	GalaxyCl();
	
	GalaxyData data;
	AccountMap accounts;
};

typedef boost::detail::thread::singleton<GalaxyCl> Galaxy;

}

#endif /*GALAXY_H_*/
