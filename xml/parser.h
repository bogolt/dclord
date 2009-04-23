#ifndef PARSER_H_
#define PARSER_H_

#include <libxml++/parsers/saxparser.h>

namespace dnc{

class Factory;

class Parser : public xmlpp::SaxParser
{
public:
	Parser();
	// register all requred factories before any xml processing
	// fails if the factory name already registered or processing already started
	bool registerFactory(Factory&);

protected:
  //overrides:
  virtual void on_start_document();
  virtual void on_end_document();
  virtual void on_start_element(const Glib::ustring& name,
                                const AttributeList& properties);
  virtual void on_end_element(const Glib::ustring& name);
  virtual void on_characters(const Glib::ustring& characters);
  virtual void on_comment(const Glib::ustring& text);
  virtual void on_warning(const Glib::ustring& text);
  virtual void on_error(const Glib::ustring& text);
  virtual void on_fatal_error(const Glib::ustring& text);
  
  typedef std::map<Glib::ustring, Factory*> FactoryMap;
  FactoryMap factory_;
  
  // to speed up the process store iterator as the current factory value
  // warning - no factory registration may be done after processing has started
  FactoryMap::iterator current_;
  bool is_processing_;
  int depth_;
  int current_depth_;
};

};

#endif /*PARSER_H_*/
