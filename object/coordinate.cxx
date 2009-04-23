#include "coordinate.h"
#include <cmath>

namespace dnc
{

Coordinate::Coordinate(const Coord x, const Coord y)
:x_(x), y_(y)
{}

Coordinate::Coord Coordinate::x() const
{
	return x_;
}

Coordinate::Coord Coordinate::y() const
{
	return y_;
}

bool Coordinate::operator < (const Coordinate& coord) const
{
	return x_ < coord.x_ || (x_ == coord.x_ && y_ < coord.y_);
}

bool Coordinate::operator ==(const Coordinate& coord) const
{
	return x_ == coord.x_ && y_ == coord.y_;
}

bool Coordinate::operator > (const Coordinate& coord) const
{
	return coord < *this;
}

bool Coordinate::operator !=(const Coordinate& coord) const
{
	return !(*this == coord); 
}

double Coordinate::distance(const Coordinate& coord) const
{
	Coord dx = x_ - coord.x_;
	Coord dy = y_ - coord.y_;
	return sqrt(dx * dx + dy * dy);
}

Glib::ustring Coordinate::to_string() const
{
	using namespace Glib;
	return ustring::format(x_) + ":" + ustring::format(y_); 
}

std::ostream& operator<<(std::ostream& stream, const Coordinate& c)
{
	return stream << c.x() << ":" << c.y();
}

}
