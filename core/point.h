#ifndef POINT_H_
#define POINT_H_

bool eq(double a, double b);
bool eq(int a, int b);

template<class T>
class point_t
{
public:
	point_t(const T& x, const T& y)
		:x_(x), y_(y){};
	
	T x() const { return x_; };
	T y() const { return y_; };
	
	point_t<T>& operator += (const point_t<T>& pt)
	{
		x_+=pt.x();
		y_+=pt.y();
		return *this;
	}

	point_t<T>& operator -= (const point_t<T>& pt)
	{
		x_-=pt.x();
		y_-=pt.y();
		return *this;
	}
	
	point_t<T>& operator *=(int sc)
	{
		x_*=sc;
		y_*=sc;
		return *this;
	}

	point_t<T>& operator /=(int sc)
	{
		x_/=sc;
		y_/=sc;
		return *this;
	}
	
	bool operator == (const point_t<T>& pt) const
	{
		return eq(x_, pt.x()) && eq(y_, pt.y());
	}
	
private:
	T x_,y_;
};

template<class T>
point_t<T> operator + (const point_t<T>& p1, const point_t<T>& p2)
{
	point_t<T> p(p1);
	p+=p2;
	return p;
}

template<class T>
point_t<T> operator - (const point_t<T>& p1, const point_t<T>& p2)
{
	point_t<T> p(p1);
	p-=p2;
	return p;
}

template<class T>
point_t<T> operator * (const point_t<T>& p1, int sc)
{
	point_t<T> p(p1);
	p*=sc;
	return p;
}

template<class T>
point_t<T> operator / (const point_t<T>& p1, int sc)
{
	point_t<T> p(p1);
	p/=sc;
	return p;
}

typedef point_t<double> Point;
typedef point_t<int> IntPoint;

template<class T1, class T2>
point_t<T1> convert(const point_t<T2>& point)
{
	return point_t<T1>(point.x(), point.y());
}

#endif /*POINT_H_*/
