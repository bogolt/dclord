#ifndef MESH_H
#define MESH_H

#include <map>
#include <vector>
#include <list>
#include "Coord.h"

Coord to_real_coord(const Coord& c);

//ugly but we have iterators now
template<class Value>
class Mesh// : public std::vector< std::map< CoordLocal, Value> >
{
public:
	typedef std::map< CoordLocal, Value> Map;
	typedef std::vector<Map> Row;
	//typedef std::vector< Map > Parent;
	typedef std::vector<Row> Column;

	Mesh(unsigned int width=4, unsigned int height=4, unsigned int cell_capacity = 250)
		:width_(width)
		,height_(height)
		,cell_capacity_(cell_capacity)
		,c_(width)
	{
		for(auto& row: c_)
			row.resize(height);
	}

	Value& value(const Coord& c )
	{
		auto rc = to_real_coord(c);
		auto area = get_local_mesh(rc);
		return c_[area.x()][area.y()][get_local_pos(rc)];
	}

	void remove(const Coord& c)
	{
		auto rc = to_real_coord(c);
		auto area = get_local_mesh(rc);
		c_[area.x()][area.y()].erase(get_local_pos(rc));
	}

	const Value& get_value(const Coord& c ) const
	{
		auto rc = to_real_coord(c);
		auto area = get_local_mesh(rc);
		auto it = c_[area.x()][area.y()].find(get_local_pos(rc));
		if(it==c_.end())
			return Value();
		return it->second;
	}

	typedef std::pair<Coord, Value> ItemPair;
	typedef std::list< ItemPair> ItemPairList;

	ItemPairList get_items() const
	{
		ItemPairList lst;
		for(auto i=0;i<width_;i++)
			for(auto j=0;j<height_;j++)
			{
				Coord c(i * cell_capacity_ + 1, j*cell_capacity_ + 1);
				for(auto item: c_[i][j])
				{
					Coord cc(c);
					cc+=item.first;
					lst.push_back( std::make_pair(cc, item.second));
				}
			}
			return lst;
	}

	size_t size() const
	{
		auto sz = 0;
		for(auto row: c_)
			for(auto col: row)
				sz += col.size();
		return sz;
	}

private:
	CoordLocal get_local_mesh(const Coord& c) const
	{
		return CoordLocal( c.x / cell_capacity_, c.y / cell_capacity_);
	}

//  unsigned int get_local_mesh_index(const Coord& c) const
//  {
//    return int(c.x / cell_capacity_) * height_ + c.y / cell_capacity_;
//  }

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
