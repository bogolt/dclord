import wx
import math
import db
import logging

log = logging.getLogger('dclord')

class BufferedWindow(wx.Window):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(-1,-1), style=wx.NO_FULL_REPAINT_ON_RESIZE)

		self.bg_color = wx.Color(255,255,255)
		self.image = None
		self.resize()
		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_SIZE, self.resize)

	def update(self):
		dc = wx.MemoryDC()
		dc.SelectObject(self.image)

		dc.Clear()
		dc.SetBrush(wx.Brush(self.bg_color))
		w,h = self.image.GetSize()
		dc.DrawRectangle(0,0, w,h)
		
		self.paint(dc)

		del dc # need to get rid of the MemoryDC before Update() is called.
		self.Refresh()
		self.Update()
		
	def paint(self, dc):
		pass
	
	def resize(self, _ = None):
		w,h = self.GetClientSize()
		self.image = wx.EmptyBitmap(w,h)
		self.update()
		
	def onPaint(self, _):
		'paint prerendered image on screen'
		dc = wx.BufferedPaintDC(self, self.image)


def objPos(obj):
	return int(obj['x']),int(obj['y'])
	
def planeSize(planet):
	return int(planet['s'])

class Map(BufferedWindow):
	MaxSize = 1000
	def __init__(self, parent):
		self.offset_pos = 120,420
		self.cell_size = 8
		self.screen_size = 4,4
		
		self.planet_filter = []#['owner_id <> 0', 's>30', 't>20', 't<40']

		BufferedWindow.__init__(self, parent)		
		
	def resize(self, evt = None):
		BufferedWindow.resize(self, evt)
		self.calcScreenSize()
	
	def calcScreenSize(self):
		w,h = self.GetClientSize()
		width  = int(math.ceil(float(w) / self.cell_size))
		height = int(math.ceil(float(h) / self.cell_size))
		self.screen_size = width,height
	
	def relPos(self, pos):
		ox, oy = self.offset_pos
		x,y = pos
		rx = x - ox
		ry = y - oy
		if rx < 0:
			rx += self.MaxSize
		if ry < 0:
			ry += self.MaxSize
		return rx*self.cell_size,ry*self.cell_size
		
	def relSize(self, sz):
		s = int(self.cell_size * (sz / 100.0 ) / 2)
		if s < 1:
			s = 1
		return s
	
	def drawPlanet(self, dc, planet):
		pos = objPos(planet)
		rx,ry = self.relPos(pos)
		x,y = pos

		sz = 1
		if 's' in planet and planet['s']:
			sz = int(planet['s'])
		dc.DrawCircle(rx, ry, self.relSize(sz))
		#log.info('planet %d %d draw at %d %d'%(x,y,rx,ry))
	
	def drawPlanets(self, dc):
		self.planet_filter
		pf = []
		pf.append('x>=%d'%(self.offset_pos[0]))
		pf.append('y>=%d'%(self.offset_pos[1]))
		pf.append('x<%d'%(self.offset_pos[0]+self.screen_size[0]))
		pf.append('y<%d'%(self.offset_pos[1]+self.screen_size[1]))

		log.debug('get planets with %s'%(pf,))
		for p in db.planets(self.planet_filter + pf):
			self.drawPlanet(dc, p)
	
	def paint(self, dc):
		w,h = self.screen_size
		
		self.drawPlanets(dc)
				
