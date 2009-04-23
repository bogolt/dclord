#include "unit.h"

namespace dnc
{

Unit::Unit(UnitClass::Id class_id, Unit::Id unit_id)
: class_id_(class_id),
  unit_id_(unit_id)
{
}

Unit::~Unit()
{
}

}
