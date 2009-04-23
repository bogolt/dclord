#ifndef UTIL_H_
#define UTIL_H_

#include <libglademm/xml.h>

#include <cassert>

#define GET_WIDGET(class_name, variable, object_name) \
	class_name* variable = 0; \
	glade->get_widget(object_name, variable); \
	assert(variable)

#define GET_WIDGET_DERIVED(class_name, variable, object_name) \
	class_name* variable = 0; \
	glade->get_widget_derived(object_name, variable); \
	assert(variable)

#endif /*UTIL_H_*/
