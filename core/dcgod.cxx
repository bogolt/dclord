
/*
#include <iostream>
#include <algorithm>

// game objects
#include "xml/Parser.h"
#include "factory/MyPlanetFactory.h"
#include "factory/BuildingClassFactory.h"

using namespace dnc;

int main()
{
	MyPlanetFactory my_planet_factory;
	BuildingClassFactory building_class_factory;
	  // Parse the entire document in one go:
	  try
	  {
	    Parser parser;
	    parser.registerFactory(my_planet_factory);
	    parser.registerFactory(building_class_factory);
	    
	    parser.set_substitute_entities(true); //
	    parser.parse_file("/home/bogolt/dev/dclord/all.xml");
	  }
	  catch(const xmlpp::exception& ex)
	  {
	    std::cout << "libxml++ exception: " << ex.what() << std::endl;
	  }	
	
	return 0;
}
*/
