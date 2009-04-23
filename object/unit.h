#ifndef UNIT_H_
#define UNIT_H_

#include "unit_class.h"

namespace dnc
{

class Unit
{
public:
	typedef long int Id;

	Unit(UnitClass::Id class_id = 0, Id unit_id = 0);
	virtual ~Unit();
	
	
protected:
	UnitClass::Id class_id_;
	Id unit_id_;
	int hit_ponts_;
};

};

#endif /*UNIT_H_*/
