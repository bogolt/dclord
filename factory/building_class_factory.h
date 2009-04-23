#ifndef BUILDINGCLASSFACTORY_H_
#define BUILDINGCLASSFACTORY_H_

#include "factory.h"

namespace dnc
{

class BuildingClassFactory : public dnc::Factory
{
public:
	BuildingClassFactory();

	// set the attributes for the current set of objects
	virtual bool setAttributes(const AttributeMap& attributes);

	// create a new object with given attributes
	virtual bool create(const AttributeMap& attributes);
};

}

#endif /*BUILDINGCLASSFACTORY_H_*/
