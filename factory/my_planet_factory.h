#ifndef MYPLANETFACTORY_H_
#define MYPLANETFACTORY_H_

#include "factory.h"
//#include <object/Planet.h>

namespace dnc
{

class MyPlanetFactory : public Factory
{
public:
	MyPlanetFactory();

	// set the attributes for the current set of objects
	virtual bool setAttributes(const AttributeMap& attributes);

	// create a new object with given attributes
	virtual bool create(const AttributeMap& attributes);
	
private:
//	MyPlanetList planet_list_;
};

}

#endif /*MYPLANETFACTORY_H_*/
