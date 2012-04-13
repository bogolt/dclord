#include "Coord.h"

using namespace std;

CoordLocal::CoordLocal(CoordLocal::Pos x, CoordLocal::Pos y)
    :pos_( (x << 8) | y)
{
}

bool CoordLocal::operator < (const CoordLocal& c) const
{
    return pos_ < c.pos_;
}

unsigned short int CoordLocal::x() const
{
    // remove lower bits
    return pos_ >> 8;
}

unsigned short int CoordLocal::y() const
{
    // throw away higher bits
    return pos_ & 0x00ff;
}


Coord to_real_coord(const Coord& c)
{
    Coord cc(c);
    cc.x-=1;
    cc.y-=1;
    return cc;
}



ostream& operator<<(ostream& ostr, const CoordLocal& cl)
{
  return ostr << cl.x() << ";" <<cl.y();
}
