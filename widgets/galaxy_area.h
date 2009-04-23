#ifndef GALAXYAREA_H_
#define GALAXYAREA_H_

#include "core/point.h"
#include <object/coordinate.h>
#include <object/planet.h>

#include <gtkmm/drawingarea.h>


class GalaxyArea
{
public:
	GalaxyArea(Gtk::DrawingArea& area);

	bool on_expose(GdkEventExpose* event);
	void showGrid(bool);

protected:
	bool redrawArea(Cairo::RefPtr<Cairo::Context>& cr, const GdkRectangle& rect);
	bool draw(Cairo::RefPtr<Cairo::Context>& cr, const dnc::Coordinate& coord);

	bool drawIndexes(Cairo::RefPtr<Cairo::Context>& cr);
	bool drawCurrentIndexes(Cairo::RefPtr<Cairo::Context>& cr);
	bool drawGrid(Cairo::RefPtr<Cairo::Context>& cr);
	bool drawSelectedCell(Cairo::RefPtr<Cairo::Context>& cr);

	bool drawPlanets(Cairo::RefPtr<Cairo::Context>& cr);

	bool on_button_press(GdkEventButton* event);
	bool on_button_release(GdkEventButton* event);
	bool on_mouse_move(GdkEventMotion* event);

	bool on_scroll(GdkEventScroll* event);

	void redraw();

private:
	static const double scale_step;
	static const int facade_;

	// reference to a real drawing area object the galaxy will be painted on
	Gtk::DrawingArea& area_;

	// offset from the 1:1 coordinate
	IntPoint virtual_pos_;
	IntPoint pointer_pos_;

	// currently selected cell
	IntPoint selected_;

	// the current cell size
	int cell_size_;

	bool show_grid_;
	// the filed is grabbed and we're moving the position
	bool is_grabbed_;

public:
	// signals available
	sigc::signal<void, dnc::Coordinate> on_planet;
};

#endif /*GALAXYAREA_H_*/
