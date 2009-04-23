#include "widgets/main_widget.h"

#include "planet_list.h"
#include "galaxy_area.h"
#include "planet_properties.h"
#include "util.h"

#include <gtkmm/menuitem.h>
#include <gtkmm/checkmenuitem.h>
#include <gtkmm/window.h>
#include <gtkmm/aboutdialog.h>
#include <gtkmm/table.h>
#include <gtkmm/drawingarea.h>

#include <iostream>

using namespace std;

#define CONNECT_MENU_ITEM(menu_item, func) do { \
	Gtk::MenuItem* item = 0; \
	glade->get_widget(menu_item, item); \
	if(item) \
	item->signal_activate().connect( sigc::mem_fun(*this, func) ); \
	else \
		cerr << "menu item " menu_item " - not found"; \
}while(false)

#define CONNECT_MENU_CHECK_ITEM(menu_item, func) do { \
	Gtk::CheckMenuItem* item = 0; \
	glade->get_widget(menu_item, item); \
	if(item) \
	item->signal_activate().connect( sigc::mem_fun(*this, func) ); \
	else \
		cerr << "menu item " menu_item " - not found"; \
}while(false)


MainWidget::MainWidget(BaseObjectType* cobject, const Glib::RefPtr<Gnome::Glade::Xml>& ref_glade)
:	Gtk::Dialog(cobject),
	glade(ref_glade)
{
	CONNECT_MENU_ITEM("menu_about", &MainWidget::on_about);
	CONNECT_MENU_ITEM("menu_planet_list", &MainWidget::on_planet_list);
	CONNECT_MENU_CHECK_ITEM("menu_grid", &MainWidget::on_show_grid);
	
	GET_WIDGET(Gtk::AboutDialog, about_dialog, "about_dialog");
	about_dialog_.reset(about_dialog);
	
	GET_WIDGET_DERIVED(PlanetList, planets_window, "planets_window");
	planets_window_.reset(planets_window);

	GET_WIDGET(Gtk::DrawingArea, area, "galaxy_area");
	galaxy_area_.reset(new GalaxyArea(*area));
	galaxy_area_->on_planet.connect(  sigc::mem_fun(this, &MainWidget::show_planet_properties) );
}

void MainWidget::on_about(void)
{
	about_dialog_->run();
	about_dialog_->hide();
}

void MainWidget::on_planet_list()
{
	planets_window_->show();	
}

MainWidget::~MainWidget()
{}

void MainWidget::on_show_grid()
{
	GET_WIDGET(Gtk::CheckMenuItem, item, "menu_grid");
	galaxy_area_->showGrid(item->get_active());
}

void MainWidget::show_planet_properties(const dnc::Coordinate& c)
{
	GET_WIDGET_DERIVED(PlanetProperties, planet, "planet_properties");
	planet_properties.reset(planet);
	planet_properties->set(c);
	planet_properties->show();
}
