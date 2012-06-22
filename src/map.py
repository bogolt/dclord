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
	
def is_owned(fleet_id):
	return False
#	for user in db.users(['id=%d'%(fleet_id,)])
#		if user['

def getOwnerColor(owner_id):
	if not owner_id:
		return config.options['map']['planet_uninhabited_color']

	key = 'custom_color_%s'%(owner_id,)
	if key in config.options['map']:
		return config.options['map'][key]
	
	if int(owner_id) in config.user_id_dict:
		return config.options['map']['planet_owned_color']
		
	return config.options['map']['planet_inhabited_color']

class Map(util.BufferedWindow):
	MaxSize = 1000
	def __init__(self, parent):
		self.offset_pos = float(config.options['map']['offset_pos_x']), float(config.options['map']['offset_pos_y'])
		self.cell_size = int(config.options['map']['cell_size'])
		self.screen_size = 1,1
		self.filterDrawFleets = bool(config.options['filter']['fleets'])
		
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
		old_offset = self.offset_pos
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
		
		self.shift(util.mul(util.sub(old_offset, self.offset_pos), self.cell_size))
		#self.update()
		self.Refresh()
		self.Update()
		#print 'motion %s'%(self.offset_pos,)
		
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
		newScreenPos = util.mul(logicPos, self.cell_size)
		newScreenDiff = util.sub(newScreenPos, pos)
		newLogicDiff = util.div(newScreenDiff, self.cell_size)
		self.offset_pos = util.add(self.offset_pos, newLogicDiff)

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
		#if rx < 0:
		#	rx += self.MaxSize
		#if ry < 0:
		#	ry += self.MaxSize
		return rx*self.cell_size,ry*self.cell_size
		
	def relSize(self, sz):
		s = int(self.cell_size * (sz / 100.0 ) / 2)
		if s < 1:
			s = 1
		return s
	
	def screenPosToLogic(self, pos):
		return util.add(self.offset_pos, util.div(pos, self.cell_size))
		
	def drawPlanet(self, dc, planet):

		rx,ry = self.relPos(objPos(planet))
		
		sz = 1
		if 's' in planet and planet['s']:
			sz = int(planet['s'])

		col = None
		if 'owner_id' in planet:
			col = getOwnerColor(int(planet['owner_id']))
		else:
			col = getOwnerColor(None)
		dc.SetPen(wx.Pen(colour=col, width=1))
		
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
		
	def rectFilter(self, rect):
		ps = self.screenPosToLogic(rect.GetPosition().Get())
		ps = util.sub(ps, (1,1))
		sz = util.div(rect.GetSize().Get(), self.cell_size)
		sz = util.add(sz, (1,1))
		return ['x>=%d AND y>=%d AND x<=%d AND y<=%d'%(ps[0], ps[1], ps[0]+sz[0], ps[1]+sz[1])]
	
	def drawPlanets(self, dc, rect):
		flt = self.rectFilter(rect) if rect else self.visibleAreaFilter()
		cond = ['owner_id is not null'] if int(config.options['filter']['inhabited_planets'])==1 else []
		for p in db.planets(self.planet_filter + flt + cond):
			self.drawPlanet(dc, p)
			
	def drawFleets(self, dc, rect):
		self.fleets = {}
		for p in db.fleets(self.visibleAreaFilter()):
			self.drawFleet(dc, p)
		for p in db.flyingFleets(self.visibleAreaFilter()):
			self.drawFlyingFleet(dc, p)
	
	def drawFleet(self, dc, fleet):
		pos = objPos(fleet)
		v = self.fleets.setdefault(pos, 0)
		self.fleets[pos] = v+1
		rx,ry = self.relPos(pos)
		diff = min(self.cell_size, 3)
		col_type = 'own_fleet_color' if is_owned(fleet['owner_id']) else 'fleet_color'
		dc.SetPen(wx.Pen(colour=config.options['map'][col_type], width=1))
		dc.DrawLine(rx+v*2 - self.cell_size/2, ry-self.cell_size/2, rx+v*2 - self.cell_size/2, ry-self.cell_size/2+diff)
		
	def drawFlyingFleet(self, dc, fleet):
		pos = objPos(fleet)
		v = self.fleets.setdefault(pos, 0)
		self.fleets[pos] = v+1
		rx,ry = self.relPos(pos)
		diff = min(self.cell_size, 3)
		col_type = 'own_flying_fleet_color' if is_owned(fleet['owner_id']) else 'flying_fleet_color'
		dc.SetPen(wx.Pen(colour=config.options['map'][col_type], width=1))
		dc.DrawLine(rx+v*2 - self.cell_size/2, ry-self.cell_size/2, rx+v*2 - self.cell_size/2, ry-self.cell_size/2+diff)

		fx,fy = fleet['from_x'],fleet['from_y']
		if fx and fy:
			col_type = 'own_fleet_route_color' if is_owned(fleet['owner_id']) else 'fleet_route_color'
			dc.SetPen(wx.Pen(colour=config.options['map'][col_type], width=1, style=wx.SHORT_DASH))
			frx,fry = self.relPos((int(fx), int(fy)))
			dc.DrawLine(rx, ry, frx, fry)
			
	def paint(self, dc, rect=None):
		self.drawPlanets(dc, rect)
		if self.filterDrawFleets:
			self.drawFleets(dc, rect)
	
	def centerAt(self, logicPos):
		self.offset_pos = util.sub(logicPos, util.div(self.screen_size, 2))
		self.update()
