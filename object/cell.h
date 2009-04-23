#ifndef CELL_H_
#define CELL_H_

#include "planet.h"

namespace dnc
{

struct FleetSet
{};

// the cell of the space
// it can contain planet info and fleets
struct Cell
{
	Planet planet;
	FleetSet fleets;
};

}

#endif /*CELL_H_*/
