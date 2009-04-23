#include "unit_class.h"

namespace dnc
{

UnitClass::UnitClass()
{
}

UnitClass::~UnitClass()
{
}

UnitClass::Bonus::Bonus()
:o(0.0), e(0.0), m(0.0), surface(0), production(0)
{}

UnitClass::Capacity::Capacity()
:carrier(0), transport(0)
{}

UnitClass::Cost::Cost()
:main(0.0), second(0.0), money(0.0), people(0)
{}

UnitClass::Defence::Defence()
:laser(0.0), bomb(0.0)
{}

UnitClass::Detection::Detection()
:scan_strength(0.0), detect_range(0.0), stealth_level(0.0)
{}

UnitClass::Flight::Flight()
:range(0.0), speed(0.0)
{}

UnitClass::Production::Production()
:build_speed(0)
{}

UnitClass::Require::Require()
:tech_level(0), people(0)
{}

UnitClass::Support::Support()
:main(0.0), second(0.0)
{}

UnitClass::Weapon::Weapon()
:damage(0.0), number(0), targeting(0.0), targets(0)
{}

std::ostream& operator<< (std::ostream& stream, const UnitClass& uc)
{
	return stream 
			<< "unit class id " << uc.id
			<< "production " << uc.production
			<< "support " << uc.support
			<< "hit points " << uc.hit_points << "\n"
			<< "bonus " << uc.bonus
			<< "detect " << uc.detection
			<< "war " << uc.war
			<< "capacity " << uc.capacity
			<< "traits " << uc.traits
			<< "flight " << uc.flight
			<< "max units " << uc.max_units
			<< "weight " << uc.weight
			<< "class " << uc.class_
			<< "carapace " << uc.carapace
			<< "colour " << uc.color;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Cost& cost)
{
	return stream << "main: " << cost.main << ", second: " << cost.second << ", money: "
					<< cost.money << ", people: " << cost.people;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Support& sup)
{
	return stream << "main: " << sup.main << ", second: " << sup.second;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Bonus& bon)
{
	return stream << "o: " << bon.o << ", e: " << bon.e << ", m: " << bon.m << 
					", surface: " << bon.surface << ", production: " << bon.production;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Weapon& w)
{
	return stream << "dmg: " << w.damage << ", number: " << w.number << ", targeting: " 
				<< w.targeting << ", targets: " << w.targets;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Attack& a)
{
	return stream << "laser attack\n" << a.laser << "\nbomb attack\n" << a.bomb;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Defence& d)
{
	return stream << "laser defence\n" << d.laser << "\nbomb defence\n" << d.bomb;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Flight& f)
{
	return stream << "flight range: " << f.range << ", speed: " << f.speed;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Capacity& c)
{
	return stream << "capacity career: " << c.carrier << ", trasp: " << c.transport;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Require& r)
{
	return stream << "require tech level: " << r.tech_level << ", people: " << r.people;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Traits& t)
{
	return stream << "traits is war" << t.is_war << ", is building " << t.is_building <<
			", is ground unit: " << t.is_ground_unit << ", is space ship: " << t.is_space_ship <<
			", is trasportable: " << t.is_transportable;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Detection& dt)
{
	return stream << "scan strength: " << dt.scan_strength << ", scan range: " << dt.detect_range << 
			", stealth level: " << dt.stealth_level;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::War& w)
{
	return stream << "war is offencive: " << w.offencive << "\nattack\n" << w.attack << 
				"\ndefence\n" << w.defence;
}

std::ostream& operator<< (std::ostream& stream, const UnitClass::Production& prod)
{
	return stream << "production cost\n" << prod.cost << "\nrequire\n" << prod.require <<
			"\nbuild speed: " << prod.build_speed;
}

}
