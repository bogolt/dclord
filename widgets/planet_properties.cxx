#include "planet_properties.h"
#include "util.h"

#include <db/galaxy.h>

#include <gtkmm/entry.h>
#include <gtkmm/expander.h>
#include <gtkmm/drawingarea.h>

#include <iostream>

PlanetProperties::PlanetProperties(BaseObjectType* cobject, const Glib::RefPtr<Gnome::Glade::Xml>& ref_glade)
:Gtk::Window(cobject),
glade(ref_glade)
{
	GET_WIDGET(Gtk::Button, close, "close");
	close->signal_clicked().connect(sigc::mem_fun(*this, &PlanetProperties::hide));
}

void PlanetProperties::set(const dnc::Coordinate& c)
{
	using namespace dnc;
	using namespace Glib;
	coordinate = c;
	Cell cell = db::Galaxy::instance().planet(c);

	GET_WIDGET(Gtk::Entry, name, "name");
	name->set_text(cell.planet.planet_data.name);
	
	GET_WIDGET(Gtk::Entry, owner, "owner");
	dnc::Account acc = db::Galaxy::instance().account(cell.planet.planet_data.owner);
	owner->set_text(acc.name);

//	GET_WIDGET(Gtk::Entry, coord_x, "coord_x");
//	coord_x->set_text(ustring::format(c.x()));
//
//	GET_WIDGET(Gtk::Entry, coord_y, "coord_y");
//	coord_y->set_text(ustring::format(c.y()));
}
