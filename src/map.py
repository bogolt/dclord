import wx
import math
import db
import logging
import util

log = logging.getLogger('dclord')

def objPos(obj):
	return int(obj['x']),int(obj['y'])
	
def planeSize(planet):
	return int(planet['s'])

class Map(util.BufferedWindow):
	MaxSize = 1000
	def __init__(self, parent):
		self.offset_pos = 200,400
		self.cell_size = 6
		self.screen_size = 4,4
		
		self.planet_filter = []#['owner_id <> 0', 's>30', 't>20', 't<40']

		util.BufferedWindow.__init__(self, parent)
		
		self.moving = False
		
		self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
		self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)		
		self.Bind(wx.EVT_MOTION, self.onMotion)
		#self.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		
	def resize(self, evt = None):
		util.BufferedWindow.resize(self, evt)
		self.calcScreenSize()

	def onLeftDown(self, evt):
		self.moving = True
		self.prevPos = evt.GetPosition()
		
	def onLeftUp(self, evt):
		self.moving = False
		self.update()

	def onMotion(self, evt):
		#fix for windows focus policy ( after treeCtrl grabs focus it wont let it back )
		self.SetFocus()
		if not self.moving:
			return

		curPos = evt.GetPosition()
		dx,dy = util.div(util.sub(self.prevPos, curPos), float(self.cell_size))

		if dx != 0 or dy != 0:
			x,y=self.offset_pos
			x+=dx
			y+=dy
			self.offset_pos=(x,y)
			#self.Refresh()
			self.prevPos = curPos
			
		self.update()
	
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
		if self.cell_size == 1:
			dc.DrawPoint(rx, ry)
		else:
			dc.DrawCircle(rx, ry, self.relSize(sz))
	
	def drawPlanets(self, dc):
		self.planet_filter
		pf = []
		pf.append('x>=%d'%(self.offset_pos[0]))
		pf.append('y>=%d'%(self.offset_pos[1]))
		pf.append('x<%d'%(self.offset_pos[0]+self.screen_size[0]))
		pf.append('y<%d'%(self.offset_pos[1]+self.screen_size[1]))

		#log.debug('get planets with %s'%(pf,))
		for p in db.planets(self.planet_filter + pf):
			self.drawPlanet(dc, p)
	
	def paint(self, dc):
		w,h = self.screen_size
		
		self.drawPlanets(dc)
				
