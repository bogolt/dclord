#ifndef MESH_H
#define MESH_H

#include <map>
#include <vector>
#include "Coord.h"

Coord to_real_coord(const Coord& c);

template<class Value>
class Mesh
{
public:
	typedef std::map< CoordLocal, Value> Map;
	typedef std::vector<Map> Row;
	typedef std::vector<Row> Column;

	Mesh(unsigned int width=4, unsigned int height=4, unsigned int cell_capacity = 250)
		:width_(width)
		,height_(height)
		,cell_capacity_(cell_capacity)
		,c_(width)
	{
		for(auto i = 0U;i<width;i++)
			c_[i].resize(height);
	}

	Value& value(const Coord& c )
	{
		auto rc = to_real_coord(c);
		CoordLocal area(get_local_mesh(rc));
		return c_[area.x()][area.y()][get_local_pos(rc)];
	}

	void remove(const Coord& c)
	{
		auto rc = to_real_coord(c);
		CoordLocal area(get_local_mesh(rc));
		auto it = c_[area.x()][area.y()].find(get_local_pos(rc));
		if(it!=c_.end())
			c_.erase(it);
	}

	const Value& get_value(const Coord& c ) const
	{
		auto rc = to_real_coord(c);
		CoordLocal area(get_local_mesh(rc));
		return c_[area.x()][area.y()][get_local_pos(rc)];
	}

private:
	CoordLocal get_local_mesh(const Coord& c) const
	{
		return CoordLocal( c.x / cell_capacity_, c.y / cell_capacity_);
	}

	CoordLocal get_local_pos(const Coord& c) const
	{
		return CoordLocal( c.x % cell_capacity_, c.y % cell_capacity_);
	}

private:
	unsigned int width_;
	unsigned int height_;
	unsigned int cell_capacity_;
	Column c_;
};

#endif // MESH_H
