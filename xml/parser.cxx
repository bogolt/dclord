#include "parser.h"

#include <factory/factory.h>

#include <algorithm>
#include <iostream>

namespace dnc{

Parser::Parser()
:is_processing_(false),
depth_(0),
current_depth_(0)
{}

bool Parser::registerFactory(Factory& factory)
{
	if(is_processing_)
		return false;
	
	// check for name duplication
	if(factory_.end() != factory_.find(factory.nodeName()))
		return false;
	
	factory_[factory.nodeName()] = &factory;
	return true;
}

void Parser::on_start_document()
{
	is_processing_ = true;
	current_ = factory_.end();
  std::cout << "on_start_document()" << std::endl;
}

void Parser::on_end_document()
{
	is_processing_ = false;
	current_ = factory_.end();
  std::cout << "on_end_document()" << std::endl;
}

template<class InIt>
void convert(const Parser::AttributeList& attributes, InIt it_)
{
	for(Parser::AttributeList::const_iterator it = attributes.begin(); it!=attributes.end(); ++it)
		*it_++ = std::make_pair(it->name, it->value);
}

void Parser::on_start_element(const Glib::ustring& name,
                                   const AttributeList& attributes)
{
	depth_++;
	
	if(current_ == factory_.end())
	{		
		current_ = factory_.find(name);
		
		// unknown tag found, just skip it
		if(current_ == factory_.end())
			return;
	
		// ok new factory is ready, load it's attributes
		// not really good as we are having depencency here ( Factory should know of xml++ )
		Factory::AttributeMap attr_map;
		convert(attributes, std::inserter(attr_map, attr_map.begin()));
		current_->second->setAttributes(attr_map);
		current_depth_ = depth_;
		return;
	}

	if(!current_->second->isObjectName(name))
		return;

	Factory::AttributeMap attr_map;
	convert(attributes, std::inserter(attr_map, attr_map.begin()));
	
	// now just create another object of current_ factory type
	//TODO: add return code validation, and log all failures
	current_->second->create(attr_map);
}

void Parser::on_end_element(const Glib::ustring& name)
{
	if((--depth_) < current_depth_)
		current_ = factory_.end();
}

void Parser::on_characters(const Glib::ustring& text)
{
 // std::cout << "on_characters(): " << text << std::endl;
}

void Parser::on_comment(const Glib::ustring& text)
{
  std::cout << "on_comment(): " << text << std::endl;
}

void Parser::on_warning(const Glib::ustring& text)
{
  std::cout << "on_warning(): " << text << std::endl;
}

void Parser::on_error(const Glib::ustring& text)
{
  std::cout << "on_error(): " << text << std::endl;
}

void Parser::on_fatal_error(const Glib::ustring& text)
{
  std::cout << "on_fatal_error(): " << text << std::endl;
}

};

