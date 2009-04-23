#include "planet_list.h"

#include <libglademm/xml.h>

#include <gtkmm/treeview.h>

PlanetList::PlanetList(BaseObjectType* cobject, const Glib::RefPtr<Gnome::Glade::Xml>& ref_glade)
:Gtk::Window(cobject)
{
}
