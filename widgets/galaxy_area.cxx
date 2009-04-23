#include "galaxy_area.h"

#include <db/galaxy.h>

#include <object/coordinate.h>
#include <db/galaxy.h>

#include <iostream>
#include <cassert>
#include <map>

// saves the content state at the beginning and restores it at the end
class AutoContext
{
public:
	explicit AutoContext(Cairo::RefPtr<Cairo::Context>& cr):cr_(cr){cr_->save();}
	~AutoContext(){cr_->restore();}
private:
	Cairo::RefPtr<Cairo::Context>& cr_;
};

#define USE_SMART_CONTEXT(c) AutoContext use_smart_context_var_defined(c)

const int max_size = 50;
const int min_size = 5;
const int min_y = 30;
const int min_x = min_y;
const int can_draw_geodata = 25;

GalaxyArea::GalaxyArea(Gtk::DrawingArea& area)
:	area_(area),
	virtual_pos_(1100, 1100),
	pointer_pos_(-1,-1),
	selected_(5,5),
	cell_size_(20),
	show_grid_(true),
	is_grabbed_(false)
{
	area_.signal_expose_event().connect( sigc::mem_fun(*this, &GalaxyArea::on_expose));
	area_.signal_motion_notify_event().connect( sigc::mem_fun(*this, &GalaxyArea::on_mouse_move));
	area_.signal_button_press_event().connect( sigc::mem_fun(*this, &GalaxyArea::on_button_press));
	area_.signal_button_release_event().connect( sigc::mem_fun(*this, &GalaxyArea::on_button_release));
	area_.signal_scroll_event().connect( sigc::mem_fun(*this, &GalaxyArea::on_scroll));
}

using namespace std;
using namespace Glib;


// TODO: this ustring::format eats a lot of cpu time ( 40% ) when scrolling fast
bool GalaxyArea::drawCurrentIndexes(Cairo::RefPtr<Cairo::Context>& cr)
{
	USE_SMART_CONTEXT(cr);
	IntPoint vpos = virtual_pos_;
	cr->set_source_rgba(0.0, 0.8, 0.0, 0.9);

	if(pointer_pos_.y() >= 0)
	{
		cr->move_to(1, min_y + (pointer_pos_.y()+0.5) * cell_size_);
		cr->show_text(ustring::format(pointer_pos_.y() + vpos.x()));
	}

	cr->rotate(-M_PI*1/2);
	if(pointer_pos_.x() >= 0)
	{
		cr->move_to(-27, min_x + (pointer_pos_.x()+0.5) * cell_size_);
		cr->show_text(ustring::format(pointer_pos_.x() + vpos.y()));
	}

	return true;
}

bool GalaxyArea::drawIndexes(Cairo::RefPtr<Cairo::Context>& cr)
{
	USE_SMART_CONTEXT(cr);
	IntPoint vpos = virtual_pos_;

	Gtk::Allocation allocation = area_.get_allocation();
	const int w = allocation.get_width();
	const int h = allocation.get_height();
	const int width = w - min_x;
	const int height = h - min_y;

	for(int i = 0; i < (height / cell_size_) + 1; ++i)
	{
		if(i == pointer_pos_.y())
			continue;
		cr->move_to(1, min_y + (i+0.5) * cell_size_);
		cr->show_text(ustring::format(i + vpos.x()));
	}

	cr->rotate(-M_PI*1/2);
	for(int i = 0; i < (width / cell_size_) + 1; ++i)
	{
		if(i == pointer_pos_.x())
			continue;
		cr->move_to(-27, min_x + (i+0.5) * cell_size_);
		cr->show_text(ustring::format(i + vpos.y()));
	}

	return true;
}

bool GalaxyArea::drawGrid(Cairo::RefPtr<Cairo::Context>& cr)
{
	USE_SMART_CONTEXT(cr);

	Gtk::Allocation allocation = area_.get_allocation();
	const int w = allocation.get_width();
	const int h = allocation.get_height();
	const int width = w - min_x;
	const int height = h - min_y;

	cr->set_antialias(Cairo::ANTIALIAS_NONE);
	cr->set_line_width(1.0);
	cr->set_source_rgba(0.0, 0.0, 0.0, 0.2);

	for(int i = 0; i < (width / cell_size_) + 2; ++i)
	{
		cr->move_to(min_x + i*cell_size_, min_y);
		cr->line_to(min_x + i*cell_size_, height + cell_size_*2);
	}

	for(int i = 0; i < (height / cell_size_) + 2; ++i)
	{
		cr->move_to(min_x, min_y + i * cell_size_);
		cr->line_to(width+cell_size_*2, min_y + i * cell_size_);
	}
	cr->stroke();

	return true;
}

bool GalaxyArea::drawSelectedCell(Cairo::RefPtr<Cairo::Context>& cr)
{
	USE_SMART_CONTEXT(cr);

	cr->set_antialias(Cairo::ANTIALIAS_NONE);
	if(selected_.x() < 0 || selected_.y() < 0)
			return true;

	// draw currently selected planet
	cr->set_source_rgba(0.0, 0.0, 1.0, 0.9);
	cr->set_line_width(1.0);
	cr->rectangle(min_x +1 + selected_.x() * cell_size_, min_y + 1 + selected_.y() * cell_size_, cell_size_ - 2, cell_size_ - 2);
	cr->stroke();
	return true;
}

bool GalaxyArea::draw(Cairo::RefPtr<Cairo::Context>& cr, const dnc::Coordinate& coord)
{
	int cx = coord.x() - virtual_pos_.y();
	int cy = coord.y() - virtual_pos_.x();
	double rad = cell_size_/2.0 - 1.7;

	double x = min_x + 0.5 + (cx + 0.5) * cell_size_;
	double y = min_y + 0.5 + (cy + 0.5) * cell_size_;

	cr->set_source_rgba(0.0, 0.7, 0.0, 0.9);
	cr->move_to(x + rad, y);
	cr->arc(x, y, rad, 0.0, 2.0 * M_PI);
	cr->stroke();

	cr->set_source_rgb(0,0,0);
	cr->move_to(x-rad, y);
	cr->show_text(ustring::format(coord.x()) + ":" + ustring::format(coord.y()));

	return true;
}

// TODO: Known bug: the planet can be drawn outside the grid ( on the index )
bool GalaxyArea::drawPlanets(Cairo::RefPtr<Cairo::Context>& cr)
{
	USE_SMART_CONTEXT(cr);
	using namespace dnc;
	using namespace db;
	GalaxyData planets;
	Galaxy::instance().known_planets(planets);

	cr->set_line_width(1.0);
	for(GalaxyData::const_iterator it = planets.begin(); it!=planets.end();++it)
		draw(cr, it->first);
	cr->stroke();

	return true;
}

bool GalaxyArea::redrawArea(Cairo::RefPtr<Cairo::Context>& cr, const GdkRectangle& screen_redraw_rect)
{
	USE_SMART_CONTEXT(cr);

	cr->save();
	cr->set_source_rgb(0.5,0.5,0.5);
	cr->paint();
	cr->restore();

	//TODO: redraw only part the window which needs redrawing
	Gtk::Allocation allocation = area_.get_allocation();

	drawIndexes(cr);
	drawCurrentIndexes(cr);

	if(show_grid_)
		drawGrid(cr);
	drawSelectedCell(cr);

	drawPlanets(cr);

	cr->stroke();
	return true;
}

bool GalaxyArea::on_expose(GdkEventExpose* event)
{
  Glib::RefPtr<Gdk::Window> window = area_.get_window();
  if(!window)
	  return false;

  Cairo::RefPtr<Cairo::Context> cr = window->create_cairo_context();

  cr->rectangle(event->area.x, event->area.y,
          event->area.width, event->area.height);
  cr->clip();

  return redrawArea(cr, event->area);
}

bool GalaxyArea::on_button_press(GdkEventButton* event)
{
	is_grabbed_ = true;
	return true;
}

bool GalaxyArea::on_button_release(GdkEventButton* event)
{
	is_grabbed_ = false;

	// show planet properties if not left button pressed
	if(1 != event->button)
	{
		on_planet.emit(dnc::Coordinate(pointer_pos_.x() + virtual_pos_.y(), pointer_pos_.y() + virtual_pos_.x() ));
		return false;
	}

	// if the user clicks again on selected planet - move to the center of the screen
	if(pointer_pos_ == selected_)
	{
		Gtk::Allocation allocation = area_.get_allocation();
		const int width = allocation.get_width() - min_x;
		const int height = allocation.get_height() - min_y;

		// get the relative center point
		IntPoint center(width, height);
		center/=cell_size_;
		center/=2;

		IntPoint diff = selected_ - center;
		IntPoint d2(diff.y(), diff.x());
		virtual_pos_ += d2;
		selected_ = center;
	}
	else
		selected_ = pointer_pos_;

	redraw();

	return false;
}

bool GalaxyArea::on_mouse_move(GdkEventMotion* event)
{
	Point pos(event->x - min_x, event->y - min_y);
	pos /= cell_size_;
	IntPoint cpos = convert<int, double>(pos);
	if(cpos == pointer_pos_)
		return false;

	if(is_grabbed_)
	{
		IntPoint diff = pointer_pos_ - cpos;
		IntPoint d2(diff.y(), diff.x());
		virtual_pos_+=d2;
		selected_ = IntPoint(-1, -1);
	}

	pointer_pos_ = cpos;

	redraw();
	return true;
}

bool GalaxyArea::on_scroll(GdkEventScroll* event)
{
	const int step = 2;
	if(event->direction == GDK_SCROLL_UP)
		cell_size_ += step;
	else if(event->direction == GDK_SCROLL_DOWN)
		cell_size_ -= step;

	if(cell_size_ < min_size)
		cell_size_ = min_size;
	if(cell_size_ > max_size)
		cell_size_ = max_size;

	redraw();
	return false;
}

void GalaxyArea::showGrid(const bool show)
{
	show_grid_ = show;
	redraw();
}

void GalaxyArea::redraw()
{
	area_.queue_draw();
}
