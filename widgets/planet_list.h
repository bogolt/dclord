#ifndef PLANETLIST_H_
#define PLANETLIST_H_

#include <gtkmm/window.h>

namespace Gnome
{
	namespace Glade
	{
		class Xml;
	};
};

class PlanetList : public Gtk::Window
{
public:
	PlanetList(BaseObjectType* cobject, const Glib::RefPtr<Gnome::Glade::Xml>& ref_glade);
	
};

#endif /*PLANETLIST_H_*/
