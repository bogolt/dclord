#ifndef BUILDINGCLASS_H_
#define BUILDINGCLASS_H_

#include "factory.h"

namespace dnc
{

class BuildingClass : public dnc::Factory
{
public:
	BuildingClass();

	// set the attributes for the current set of objects
	virtual bool setAttributes(const AttributeMap& attributes);

	// create a new object with given attributes
	virtual bool create(const AttributeMap& attributes);
};

}

#endif /*BUILDINGCLASS_H_*/
