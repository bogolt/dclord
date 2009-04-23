#include "factory.h"

namespace dnc
{

Factory::Factory(const Glib::ustring& node_name, const Glib::ustring& element_name)
:node_name_(node_name),
element_name_(element_name)
{
}

Factory::~Factory()
{
}

bool Factory::isObjectName(const Glib::ustring& name) const
{
	return name == element_name_;
}

const Glib::ustring& Factory::nodeName() const
{
	return node_name_;
}

};
