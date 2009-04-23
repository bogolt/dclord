#include "building_class_factory.h"
#include <object/unit_class.h>

#include <sstream>
#include <iostream>

namespace dnc
{

BuildingClassFactory::BuildingClassFactory()
:Factory("building-types", "building_class")
{
}

bool BuildingClassFactory::setAttributes(const AttributeMap&)
{
	// currently no attrubutes supported
	return true;
}

bool BuildingClassFactory::create(const AttributeMap& attr)
{
	UnitClass uc;

	LOAD_ATTR(attr, "building-id", uc.id);
		
	LOAD_ATTR(attr, "cost-main", uc.production.cost.main);
	LOAD_ATTR(attr, "cost-second", uc.production.cost.second);
	LOAD_ATTR(attr, "cost-money", uc.production.cost.money);
	LOAD_ATTR(attr, "cost-pepl", uc.production.cost.people);
	
	LOAD_ATTR(attr, "support-main", uc.support.main);
	LOAD_ATTR(attr, "support-second", uc.support.second);

	LOAD_ATTR(attr, "requires-pepl", uc.production.require.people);
	
	LOAD_ATTR(attr, "hit-points", uc.hit_points);
	
	LOAD_ATTR(attr, "bonus-o", uc.bonus.o);
	LOAD_ATTR(attr, "bonus-e", uc.bonus.e);
	LOAD_ATTR(attr, "bonus-m", uc.bonus.m);
	LOAD_ATTR(attr, "bonus-surface", uc.bonus.surface);
	LOAD_ATTR(attr, "bonus-production", uc.bonus.production);
	
	LOAD_ATTR(attr, "req-tehn-level", uc.production.require.tech_level);
	
	LOAD_ATTR(attr, "scan-strength", uc.detection.scan_strength);
	LOAD_ATTR(attr, "detect-range", uc.detection.detect_range);
	LOAD_ATTR(attr, "stealth-lvl", uc.detection.stealth_level);
	
	LOAD_ATTR(attr, "laser-damage", uc.war.attack.laser.damage);
	LOAD_ATTR(attr, "laser-number", uc.war.attack.laser.number);
	LOAD_ATTR(attr, "laser-ar", uc.war.attack.laser.targeting);
	LOAD_ATTR(attr, "laser-targets", uc.war.attack.laser.targets);
	
	LOAD_ATTR(attr, "bomb-damage", uc.war.attack.bomb.damage);
	LOAD_ATTR(attr, "bomb-number", uc.war.attack.bomb.number);
	LOAD_ATTR(attr, "bomb-ar", uc.war.attack.bomb.targeting);
	LOAD_ATTR(attr, "bomb-targets", uc.war.attack.bomb.targets);
	
	LOAD_ATTR(attr, "offensive", uc.war.offencive);
		
	LOAD_ATTR(attr, "laser-dr", uc.war.defence.laser);
	LOAD_ATTR(attr, "bomb-dr", uc.war.defence.bomb);
	
	LOAD_ATTR(attr, "is-war", uc.traits.is_war);
	LOAD_ATTR(attr, "is-building", uc.traits.is_building);
	LOAD_ATTR(attr, "is-ground-unit", uc.traits.is_ground_unit);
	LOAD_ATTR(attr, "is-space-ship", uc.traits.is_space_ship);
	LOAD_ATTR(attr, "is-transportable", uc.traits.is_transportable);
	
	LOAD_ATTR(attr, "carrier-capacity", uc.capacity.carrier);
	LOAD_ATTR(attr, "transport-capacity", uc.capacity.transport);
	
	LOAD_ATTR(attr, "fly-range", uc.flight.range);
	LOAD_ATTR(attr, "fly-speed", uc.flight.speed);
	
	LOAD_ATTR(attr, "maxcount", uc.max_units);
	LOAD_ATTR(attr, "weight", uc.weight);
	LOAD_ATTR(attr, "class", uc.class_);
	LOAD_ATTR(attr, "carapace", uc.carapace);
	LOAD_ATTR(attr, "color", uc.color);
	
	// finally load name and description, if they exist
	AttributeMap::const_iterator it = attr.find("name");
	if(it!=attr.end())
		uc.info.name = it->second;
	
	it = attr.find("description");
	if(it!=attr.end())
		uc.info.description = it->second;
		
	using namespace std;
	
	cout << uc << endl; 

	return true;
}

}
