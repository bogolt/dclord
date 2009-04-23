#ifndef COORDINATE_H_
#define COORDINATE_H_

#include <glibmm/ustring.h>

#include <ostream>

namespace dnc
{

class Coordinate
{
public:
	typedef int Coord; 
	
	Coordinate(Coord x = 0, Coord y = 0);
	
	Coord x() const;
	Coord y() const;
	
	// x belived to be bigger the y when comparing/sorting objects
	bool operator < (const Coordinate&) const;
	bool operator ==(const Coordinate&) const;
	bool operator > (const Coordinate&) const;
	bool operator !=(const Coordinate&) const;
	
	double distance(const Coordinate&) const;
	
	Glib::ustring to_string() const;
	
private:
	Coord x_, y_;
};

std::ostream& operator<<(std::ostream& stream, const Coordinate& c);

}

#endif /*COORDINATE_H_*/
