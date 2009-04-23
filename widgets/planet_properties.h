#ifndef PLANET_PROPERTIES_H_
#define PLANET_PROPERTIES_H_

#include <object/coordinate.h>

#include <gtkmm/window.h>

namespace Gnome
{
	namespace Glade
	{
		class Xml;
	};
};

class PlanetProperties : public Gtk::Window
{
public:
	PlanetProperties(BaseObjectType* cobject, const Glib::RefPtr<Gnome::Glade::Xml>& ref_glade);
	
	// set current cell coordinate
	void set(const dnc::Coordinate& c);
	
private:
	Glib::RefPtr<Gnome::Glade::Xml> glade;
	
	dnc::Coordinate coordinate;
};

#endif /*PLANET_PROPERTIES_H_*/
