#ifndef MAINWIDGET_H_
#define MAINWIDGET_H_

#include "galaxy_area.h"

#include <gtkmm/dialog.h>

#include <memory>

namespace Gnome
{
	namespace Glade
	{
		class Xml;
	};
};

namespace Gtk
{
	class AboutDialog;
	class Window;
};

class PlanetList;
class GalaxyArea;
class PlanetProperties;

class MainWidget : public Gtk::Dialog
{
public:
	MainWidget(BaseObjectType* cobject, const Glib::RefPtr<Gnome::Glade::Xml>& refGlade);
	~MainWidget();

private:
	void on_about();
	void on_planet_list();
	void on_show_grid();
	
	void show_planet_properties(const dnc::Coordinate& c);
	
private:
	Glib::RefPtr<Gnome::Glade::Xml> glade;
	
	std::auto_ptr<Gtk::AboutDialog> about_dialog_;
	std::auto_ptr<PlanetList> planets_window_;
	std::auto_ptr<GalaxyArea> galaxy_area_;
	std::auto_ptr<PlanetProperties> planet_properties;
};

#endif /*MAINWIDGET_H_*/
