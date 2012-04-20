import wx
import math
import db
import logging
import util
import config

log = logging.getLogger('dclord')

def objPos(obj):
	return int(obj['x']),int(obj['y'])
	
def planeSize(planet):
	return int(planet['s'])

class Map(util.BufferedWindow):
	MaxSize = 1000
	def __init__(self, parent):
		self.offset_pos = float(config.options['map']['offset_pos_x']), float(config.options['map']['offset_pos_y'])
		self.cell_size = int(config.options['map']['cell_size'])
		self.screen_size = 1,1
		
		self.planet_filter = []#['owner_id <> 0', 's>30', 't>20', 't<40']

		util.BufferedWindow.__init__(self, parent)
		
		self.moving = False
		
		self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
		self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)		
		self.Bind(wx.EVT_MOTION, self.onMotion)
		self.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		
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
		
	def onScroll(self, evt):

		pos = evt.GetPosition()
		logicPos = util.div(pos, float(self.cell_size))

		diff = 1 if evt.GetWheelRotation()>0 else -1
		self.cell_size += diff
		if self.cell_size < 1:
			self.cell_size = 1
		elif self.cell_size > 40:
			self.cell_size = 40

		self.calcScreenSize()
		
		#make sure mouse is pointing on the centre  of the scroll area ( just move the pos so that this _is_ the center )
		newScreenPos   = util.mul(logicPos, self.cell_size)
		newScreenDiff  = util.sub(newScreenPos, pos)
		newLogicDiff	 = util.div(newScreenDiff, self.cell_size)
		self.offset_pos= util.add(self.offset_pos, newLogicDiff)

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
		rx,ry = self.relPos(objPos(planet))

		sz = 1
		if 's' in planet and planet['s']:
			sz = int(planet['s'])
		if self.cell_size == 1:
			dc.DrawPoint(rx, ry)
		else:
			dc.DrawCircle(rx, ry, self.relSize(sz))
	
	def visibleAreaFilter(self, xname='x', yname='y'):
		f = []
		f.append('%s>=%d'%(xname, self.offset_pos[0]))
		f.append('%s>=%d'%(yname, self.offset_pos[1]))
		f.append('%s<%d'%(xname, self.offset_pos[0]+self.screen_size[0]))
		f.append('%s<%d'%(yname, self.offset_pos[1]+self.screen_size[1]))
		return f
	
	def drawPlanets(self, dc):
		for p in db.planets(self.planet_filter + self.visibleAreaFilter()):
			self.drawPlanet(dc, p)
			
	def drawFleets(self, dc):
		dc.SetPen(wx.Pen(colour=config.options['map']['fleet_color'], width=1))
	
		self.fleets = {}
		for p in db.fleets(self.visibleAreaFilter()):
			self.drawFleet(dc, p)
	
	def drawFleet(self, dc, fleet):
		pos = objPos(fleet)
		v = self.fleets.setdefault(pos, 0)
		self.fleets[pos] = v+1
		rx,ry = self.relPos(pos)
		rx-=self.cell_size/2
		diff = min(self.cell_size, 3)
		dc.DrawLine(rx+v*2, ry-self.cell_size/2, rx+v*2, ry-self.cell_size/2+diff)
	
	def paint(self, dc):
		self.drawPlanets(dc)
		self.drawFleets(dc)
				
