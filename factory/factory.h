#ifndef FACTORY_H_
#define FACTORY_H_

#include <glibmm/ustring.h>

#include <map>

namespace dnc
{

// use only for numeric values, no unicode strings allowed
#define LOAD_ATTR(_attr_, _val_, _res_) do { \
Factory::AttributeMap::const_iterator it = _attr_.find(_val_); \
if(it ==_attr_.end()) return false; \
std::istringstream str(it->second); \
str >> _res_; \
}while(false);

class Factory
{
public:
	typedef std::map<Glib::ustring, Glib::ustring> AttributeMap;
	
	Factory(const Glib::ustring& node_name, const Glib::ustring& element_name);
	virtual ~Factory();

	// set the attributes for the current set of objects
	virtual bool setAttributes(const AttributeMap& attributes) = 0;

	// create a new object with given attributes
	virtual bool create(const AttributeMap& attributes) = 0;

	bool isObjectName(const Glib::ustring& name) const;
	const Glib::ustring& nodeName() const;
		
protected:
	
	
	const Glib::ustring node_name_;
	const Glib::ustring element_name_;
};

};

#endif /*FACTORY_H_*/
