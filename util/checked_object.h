#ifndef CHECKEDT_H_
#define CHECKED_H_

#include <cassert>

namespace utils {

// allows checked object creation
// usage: 

//Point pt = a.getPoint();
//
//Checked<Point> pt = a.getPoint();
//if(pt)
//	Point p = pt;

template<class T>
class Checked
{
public:
	// success constructor - the object is properly initialized
	Checked(const T& object);
	
	// fail constructor - the object is not initialized
	Checked();

	// return the object created. should be only called when object was initalized
	const T& object() const;
	
	bool failed() const;
	bool succeeded() const;
	
	bool operator!() const;
	
	operator const T& () const;
	
private:
	const T object_;
	const bool result_;
};

template<class T>
Checked<T>::Checked(const T& object)
:object_(object), result_(true)
{}

template<class T>
Checked<T>::Checked()
:result_(false)
{}

template<class T>
const T& Checked<T>::object() const
{
	assert(result_);
	return object_;
}

template<class T>
bool Checked<T>::failed() const
{
	return result_ == false;
}

template<class T>
Checked<T>::succeeded() const
{
	return !failed();
}

template<class T>
bool Checked<T>::operator!() const
{
	return failed();
}

template<class T>
Checked<T>::operator const T& () const
{
	return object();
}

}  // namespace utils

#endif /*CHECKED_H_*/
