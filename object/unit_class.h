#ifndef UNITCLASS_H_
#define UNITCLASS_H_

#include <ostream>
#include <glibmm/ustring.h>

namespace dnc
{

struct UnitClass
{
	UnitClass();
	virtual ~UnitClass();

	typedef long int Id;
	
	struct Cost
	{
		Cost();
		
		double main;
		double second;
		double money;
		int people;
	};
	
	struct Support
	{
		Support();
		double main;
		double second;
	};
	
	struct Bonus
	{
		Bonus();
		
		double o;
		double e;
		double m;
		int surface;
		int production;
	};
	
	struct Weapon
	{
		Weapon();
		
		double damage;
		int number;
		double targeting;
		int targets;
	};
	
	struct Attack
	{
		Weapon laser;
		Weapon bomb;
	};
	
	struct Defence
	{
		Defence();
		
		double laser;
		double bomb;
	};
	
	struct Flight
	{
		Flight();
		
		double range;
		double speed;
	};
	
	struct Capacity
	{
		Capacity();
		
		int carrier;
		int transport;
	};
	
	struct Require
	{
		Require();
		
		int tech_level;
		int people;
	};
	
	struct Traits
	{
		bool is_war;
		bool is_building;
		bool is_ground_unit;
		bool is_space_ship;
		bool is_transportable;
	};
	
	struct Detection
	{
		Detection();
		
		double scan_strength;
		double detect_range;
		
		double stealth_level;
	};
	
	struct War
	{
		bool offencive;
		Attack attack;
		Defence defence;		
	};
	
	struct Production
	{
		Production();
		
		Cost cost;
		Require require;
		double build_speed;
	};
	
	struct Info
	{
		Glib::ustring name;
		Glib::ustring description;
	};
	
	// unit type unique id
	Id id;
	// name and description
	Info info;
	// unit production related matters ( cost, time, requirements )
	Production production;
	// unit support costs
	Support support;
	// unit hit points
	int hit_points;
	// unit related bonus
	Bonus bonus;
	// unit detection and stealth
	Detection detection;
	// unit fighting capabilities
	War war;
	// unit capacity ( max trasport and career cells ) 
	Capacity capacity;
	// unit specific trais ( is it fighting, is it building, etc.. ) 
	Traits traits;
	// unit flight charateristics
	Flight flight;
	// max units of this type allowed
	int max_units;
	// unit weight
	double weight;
	// ???
	int class_;
	// ???
	int carapace;
	// unit color
	int color;
};

std::ostream& operator<< (std::ostream& stream, const UnitClass& uc);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Cost& cost);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Support& cost);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Bonus& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Weapon& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Attack& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Defence& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Flight& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Capacity& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Require& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Traits& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Detection& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::War& sup);
std::ostream& operator<< (std::ostream& stream, const UnitClass::Production& sup);

}

#endif /*UNITCLASS_H_*/
