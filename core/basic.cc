#include "widgets/main_widget.h"

#include <libglademm/xml.h>

#include <gtkmm/main.h>

#include <iostream>

int main (int argc, char **argv)
{
  Gtk::Main kit(argc, argv);

  //Load the Glade file and instantiate its widgets:
  Glib::RefPtr<Gnome::Glade::Xml> refXml;
  try
  {
    refXml = Gnome::Glade::Xml::create("res/widgets.glade");
  }
  catch(const Gnome::Glade::XmlError& ex)
  {
    std::cerr << ex.what() << std::endl;
    return 1;
  }

  //Get the Glade-instantiated dialog::
  MainWidget* pDialog = 0;

  refXml->get_widget_derived("main", pDialog);
  if(pDialog)
  {
    //Start:
    kit.run(*pDialog);
  }

  delete pDialog;

  return 0;
}
