import wx
import math
import db
from store import store
import logging
import util
import config
import event
import serialization

log = logging.getLogger('dclord')

def vis_area_filter(ps, sz):
	return {'>=':{'x':ps[0], 'y':ps[1]}, '<=':{'x':ps[0]+sz[0], 'y':ps[1]+sz[1]}}


def bestFit(obj, length):
	if obj < length:
		return 1
	val = int(math.ceil(obj / float(length)))
	if val <= 3:
		return val
		
	if val % 5 != 0:
		return val + 5 - val % 5
	return val

def objPos(obj):
	return int(obj['x']),int(obj['y'])
	
def planeSize(planet):
	return int(planet['s'])
	
def is_owned(fleet_id):
	return False
#	for user in db.users(['id=%d'%(fleet_id,)])
#		if user['

def getOwnerColor(owner_id):
	if not owner_id or owner_id == 0:
		return config.options['map']['planet_uninhabited_color']

	key = 'custom_color_%s'%(owner_id,)
	if key in config.options['map']:
		return config.options['map'][key]
	
	if owner_id and int(owner_id) in config.user_id_dict:
		return config.options['map']['planet_owned_color']
		
	return config.options['map']['planet_inhabited_color']

class Map(util.BufferedWindow):
	MaxSize = 1000
	X = 0
	Y = 1
	def __init__(self, parent):
		self.offset_pos = float(config.options['map']['offset_pos_x']), float(config.options['map']['offset_pos_y'])
		self.cell_size = int(config.options['map']['cell_size'])
		self.screen_size = 1,1
		self.filterDrawFleets = bool(config.options['filter']['fleets'])
		self.turn = 0
		self.selected_user_id = 0
		self.user_race = None
		self.selected_user_governers_count = 0
		self.planet_filter_ptr = None
		self.selected_planet = None
		self.jump_fleets_routes = []
		#self.filterDrawAreas = bool(config.options['filter']['areas'])
		self.show_good_planets = None
		
		self.planet_filter = []#['owner_id <> 0', 's>30', 't>20', 't<40']
		self.pf = None
		self.draw_geo = 1==int(config.options['map']['draw_geo'])

		util.BufferedWindow.__init__(self, parent)

		self.moving = False
		
		self.click_timer = wx.Timer(self, wx.ID_ANY)
		self.motionEvent = []
		
		
		
		self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
		self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)		
		self.Bind(wx.EVT_MOTION, self.onMotion)
		self.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		self.Bind(wx.EVT_TIMER, self.onClickTimer, self.click_timer)
		
	def select_pos(self, coord):
		self.selected_planet = coord
		self.update()
		
	def resize(self, evt = None):
		util.BufferedWindow.resize(self, evt)
		self.calcScreenSize()

	def onLeftDown(self, evt):
		self.moving = True
		self.prevPos = evt.GetPosition()
		#self.click_pos = self.prevPos
		#self.moving_proved = False
		#self.click_timer.Start( milliseconds=60, oneShot = True)
		
	def onLeftUp(self, evt):
		self.moving = False
		self.update()
		
		#if self.moving_proved:
		#	return
			
		pos = util.add(self.offset_pos, util.div(evt.GetPosition(), float(self.cell_size)))
		wx.PostEvent(self.GetParent(), event.SelectObject(attr1=(int(round(pos[0])), int(round(pos[1]))), attr2=None))
		
	def onClickTimer(self, evt):
		if self.moving:
			self.moving_proved = True
			self.popMotionEvent()
		else:
			self.motionEvent = []

	def pushMotionEvent(self, evt):
		self.motionEvent.append( evt )

	def popMotionEvent(self):
		
		mt_evts, self.motionEvent = self.motionEvent, []
		for mt in mt_evts:
			self.onMotion(mt)

	def onMotion(self, evt):
		old_offset = self.offset_pos
		#fix for windows focus policy ( after treeCtrl grabs focus it wont let it back )
		self.SetFocus()
		if not self.moving:
			return
		
		#if not self.moving_proved:
		#	self.pushMotionEvent(evt)
		#	return

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
	
	def rel_coords(self, x, y):
		return (x - self.offset_pos[0]) * self.cell_size, (y - self.offset_pos[1]) * self.cell_size
	
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
		
	
	def draw_good_planet(self, dc, planet):
		if not 'o' in planet or not planet['o']:
			return []
		if not self.user_race:
			return []
		#if sz < 80:
		#	return

		try:
			B1 = float(self.user_race['population_growth'])
			B2 = float(self.user_race['temperature_optimal'])
			B3 = float(self.user_race['temperature_delta'])
			B4 = self.selected_user_governers_count
			A1 = float(planet['t'])

			nature_value = int(planet[self.user_race['resource_nature']])
			main_value = int(planet[self.user_race['resource_main']])
			second_value = int(planet[self.user_race['resource_secondary']])
			
			A2 = float(nature_value)
			A4 = float(planet['s'])
			
			A5 = 5000 #colony or use 30000 for ark
			
			planet_population_growth = min(1, 2-A5/A4/1000) * min(1, 2-math.fabs(B2-A1)/B3) * A2 * 0.5 * (1+B1/100) / (B4+3)
			
			col = 'black'
			if planet_population_growth >= 3.0:
				col = 'green'
			elif planet_population_growth >= 1.0:
				col = '#00dd00'
			elif planet_population_growth >= 0.0:
				col = 'yellow'
			else:
				return []
		except TypeError as e:
			print 'Error %s with planet %s'%(e, planet)
			return []

		return [col]

	def drawPlanet(self, dc, planet):
		planetPos = objPos(planet)
		rx,ry = self.relPos(planetPos)
		
		sz = 1
		if 's' in planet and planet['s']:
			sz = int(planet['s'])

		col = None
		owner_id = 0
		width = 1
		if 'user_id' in planet and planet['user_id']:
			owner_id = planet.get('user_id', 0)
		
		if not owner_id or owner_id == 0:
			color = 'black'
			brush_type = None
			
			if self.show_good_planets:
				li = self.draw_good_planet(dc, planet)
				if li:
					color = li[0]
					width = 2
		else:
			brush_type = 1
			
			u = store.get_user(owner_id)

			if self.selected_user_id == owner_id:
				color = 'orange'
			elif not u:
				color='black'
				brush_type=None
			elif 'login' in u and u['login']:# and len(u['login']>0):
				color = 'red'
			else:
				color = 'green'
		
		dc.SetPen(wx.Pen(color, width=width))
		
		brush = wx.Brush(color)
		if not brush_type:
			brush.SetStyle(wx.TRANSPARENT)
		dc.SetBrush(brush)

		dc.DrawCircle(rx, ry, self.relSize(sz))
		return
			
		dc.SetPen(wx.Pen(colour='black', width=1))
		if not owner_id :
			owner_id = 0
		else:
			owner_id = int(owner_id)
			
		if owner_id == self.selected_user_id:
			col = config.options['map']['planet_selected_user_color']
			dc.SetPen(wx.Pen(colour=col, width=1))
			dc.SetBrush(wx.Brush(col))
		else:
			user_open_planet = db.db.get_object(db.Db.OPEN_PLANET, {'=':{'x':planet['x'], 'y':planet['y'], 'user_id':self.selected_user_id}})
			if user_open_planet:
				col = 'blue' #open
			else:
				col = getOwnerColor(owner_id)
			brush = wx.Brush(col)
			dc.SetPen(wx.Pen(colour=col, width=1))
			if owner_id == 0:
				brush.SetStyle(wx.TRANSPARENT)
			dc.SetBrush(brush)

		if self.cell_size == 1:
			dc.DrawPoint(rx, ry)
		else:
			if self.planet_filter_ptr and self.planet_filter_ptr.is_planet_shown(planetPos):
				dc.SetBrush(wx.Brush('red'))
			
			dc.DrawCircle(rx, ry, self.relSize(sz))
			#dc.FloodFill(rx, ry, col)
			dc.SetBrush(wx.Brush('white'))
				#dc.SetPen(wx.Pen(colour=col, width=2))
				#dc.DrawCircle(rx, ry, self.relSize(sz))
				
	def draw_open_planet(self, dc, planet):
		planetPos = objPos(planet)
		rx,ry = self.relPos(planetPos)
		dc.SetPen(wx.Pen('blue', width=2))
		rx-=self.cell_size/2
		ry+=self.cell_size/2
		dc.DrawLine(rx, ry, rx + self.cell_size, ry)
		#dc.SetBrush(wx.Brush('white', style=wx.TRANSPARENT))
		#dc.DrawCircle(rx, ry, )
	
	def drawPlanetGeo(self, dc, planet):
		if not all(k in planet and k != unicode('') for k in('o','e','m','s')):
			return
			
		planetPos = objPos(planet)
		rx,ry = self.relPos(planetPos)

		try:
			sz = int(planet['s'])
		except:
			return
		
		br = {'o':'green', 'e':'blue', 'm':'red', 't':'yellow'}
		offset = 0
		for key in ['o', 'e', 'm', 't']:
			value = int(planet[key])
			dc.SetPen(wx.Pen(colour=br[key], width=1))
			dc.SetBrush(wx.Brush(br[key]))
			ln = int(self.cell_size*(value/100.0)/2)
			dc.DrawRectangle(rx-self.cell_size/2 + offset, ry+self.cell_size/2 - ln, 4, ln)
			offset += 6
			
		dc.SetBrush(wx.Brush('white'))
	
	def visibleAreaFilter(self, xname='x', yname='y'):
		f = []
		f.append('%s>=%d'%(xname, int(self.offset_pos[0])))
		f.append('%s>=%d'%(yname, int(self.offset_pos[1])))
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
		#cond = ['owner_id is not null'] 
		ax,bx = self.offset_pos[0], self.offset_pos[0]+self.screen_size[0]
		ay,by = self.offset_pos[1], self.offset_pos[1]+self.screen_size[1]

		inhabitedOnly = int(config.options['filter']['inhabited_planets'])==1
		ownedOnly = int(config.options['filter']['owned_planets'])==1

		if not inhabitedOnly and not ownedOnly:
			for p in store.iter_planets_size((ax,bx,ay,by)):
				self.drawPlanet(dc, p)
			
		for p in store.iter_planets((ax,bx,ay,by), inhabited = inhabitedOnly, owned = ownedOnly):
			self.drawPlanet(dc, p)
			#if self.draw_geo:
			#	self.drawPlanetGeo(dc, p)
			
		if self.selected_user_id:
			for p in store.iter_objects_list('open_planet', {'user_id':self.selected_user_id}):
				self.draw_open_planet(dc, p)
	
	def toggle_fleet_jump(self, fleet_id):
			
		self.update()
		
	def drawFleets(self, dc, rect):
		self.fleets = {}
		for p in store.iter_objects_list('fleet', {}, rect):
			self.drawFleet(dc, p)
		for p in store.iter_objects_list('flying_fleet', {}, rect):
			self.drawFlyingFleet(dc, p)
	
	def drawFleet(self, dc, fleet):
		pos = objPos(fleet)
		v = self.fleets.setdefault(pos, 0)
		self.fleets[pos] = v+1
		rx,ry = self.relPos(pos)
		diff = min(self.cell_size, 3)
		col_type = 'own_fleet_color' if is_owned(fleet['user_id']) else 'fleet_color'
		dc.SetPen(wx.Pen(colour=config.options['map'][col_type], width=1))
		dc.DrawLine(rx+v*2 - self.cell_size/2, ry-self.cell_size/2, rx+v*2 - self.cell_size/2, ry-self.cell_size/2+diff)
		
	def drawFlyingFleet(self, dc, fleet):
		pos = objPos(fleet)
		v = self.fleets.setdefault(pos, 0)
		self.fleets[pos] = v+1
		rx,ry = self.relPos(pos)
		diff = min(self.cell_size, 3)
		col_type = 'own_flying_fleet_color' if is_owned(fleet['user_id']) else 'flying_fleet_color'
		dc.SetPen(wx.Pen(colour=config.options['map'][col_type], width=1))
		dc.DrawLine(rx+v*2 - self.cell_size/2, ry-self.cell_size/2, rx+v*2 - self.cell_size/2, ry-self.cell_size/2+diff)

		fx,fy = fleet['from_x'],fleet['from_y']
		if fx and fy:
			col_type = 'own_fleet_route_color' if is_owned(fleet['user_id']) else 'fleet_route_color'
			dc.SetPen(wx.Pen(colour=config.options['map'][col_type], width=1, style=wx.SHORT_DASH))
			frx,fry = self.relPos((int(fx), int(fy)))
			dc.DrawLine(rx, ry, frx, fry)
	
	def paint(self, dc, rect=None):
		
		#if self.turn and self.turn > 0:
		self.drawPlanets(dc, rect)
		if self.filterDrawFleets:
			self.drawFleets(dc, rect)
		#else:
		#	print 'wrong turn %s'%(self.turn,)
		self.drawCoordinates(dc)
		
		#if self.pf:
		#	self.drawPathFind(dc)
			
		if self.jump_fleets_routes:
			self.draw_jump_fleets(dc)
		
		#if self.filterDrawAreas:
		#	self.drawAreas(dc, rect)

	def draw_jump_fleets(self, dc):
		if not self.jump_fleets_routes or not self.selected_planet:
			return
			
		for route in self.jump_fleets_routes:
			if not route or route==[]:
				continue
			prev_point = route[0]
			for next_point in route[1:]:
				self.draw_route(dc, prev_point, next_point, 'blue')
				prev_point = next_point
			
			#fleet = store.get_object('fleet', {'fleet_id':fleet_id})
			#start_pos = fleet['x'], fleet['y']
			#spd, rng = store.get_fleet_speed_range(fleet_id)
			#if rng >= util.distance(start_pos, self.selected_planet):
			#	self.draw_route(dc, start_pos, self.selected_planet, 'blue')
			#else:
			#	self.draw_route(dc, start_pos, self.selected_planet, 'red')
			#self.draw_path(fleet_id, self.selected_planet)
			
	#def draw_path(self, fleet_id, coord):
	#	fleet = store.get_object('fleet', {'fleet_id':fleet_id})
		
	def draw_route(self, dc, start_pos, end_pos, color):
		sx,sy = self.relPos(start_pos)
		dx,dy = self.relPos(end_pos)

		dc.SetPen(wx.Pen(colour=color, width=2))
		dc.DrawLine(sx, sy, dx, dy)
		
		dc.SetBrush(wx.Brush(colour='red'))
		dc.DrawCircle(dx, dy, 3)
		
	def drawPathFind(self, dc):
		
		routes = self.pf.routes
		color = config.options['map']['route_test_color']
		if self.pf.is_found():
			color = config.options['map']['route_found_color']
			routes = self.pf.best_route()
		
		for posA, route_info in routes.iteritems():
			posB = route_info[0]
			arx,ary = self.relPos(posA)
			brx,bry = self.relPos(posB)
			
			dc.SetPen(wx.Pen(colour=color, width=2))
			dc.DrawLine(arx, ary, brx, bry)
		ax,ay = self.relPos( self.pf.start_pos )
		bx,by = self.relPos( self.pf.end_pos )
		

		if not self.pf.is_found():
			dc.SetPen(wx.Pen(colour=config.options['map']['route_direct_color'], width=2))
			dc.DrawLine(ax, ay, bx, by)
			
	def drawAreas(self, dc, rect):
		ar = [(200,200), (200,300), (300,300), (300, 200)]
	
	def centerAt(self, logicPos):
		#print 'before centering offset is %s %s'%(self.offset_pos, logicPos)
		if logicPos == (0,0):
			print traceback.format_exc()
		self.offset_pos = util.sub(logicPos, util.div(self.screen_size, 2))
		#print 'after centering offset is %s'%(self.offset_pos,)
		self.update()
	
	def drawCoordinates(self, dc):
		size = self.GetClientSize()
		f = dc.GetFont()
		f.SetPointSize(8)
		f.SetFamily(wx.FONTFAMILY_SCRIPT)
		dc.SetFont(f)
		
		max_w,max_h = dc.GetTextExtent("9999")
		every_nth = bestFit(max_w, self.cell_size)
					
		dc.SetTextForeground(config.options['map']['coordinate_color'])
		startx = int(self.offset_pos[self.X])
		
		dc.SetClippingRect(wx.Rect(max_w, 0, size[0], size[1]))
		for x in range(startx, startx + self.screen_size[self.X], every_nth):
			rx,_ = self.relPos((x, 30))
			dc.DrawText(str(x), rx-dc.GetTextExtent(str(x))[0]/2, 0)
		dc.DestroyClippingRegion()

		starty = int(self.offset_pos[self.Y])+1
		
		dc.SetClippingRect(wx.Rect(0, max_h, size[0], size[1]))
		every_nth = bestFit(max_h, self.cell_size)
		for y in range(starty, starty + self.screen_size[self.Y], every_nth):
			_,ry = self.relPos((20, y))
			dc.DrawText(str(y), 0, ry-dc.GetTextExtent(str(x))[1]/2)
		dc.DestroyClippingRegion()

	def selectUser(self, user_id):
		hw_pos = store.get_object('hw', {'user_id': user_id})
		self.selected_user_governers_count = 0
		if not hw_pos:
			print 'cannot get hw of %s'%user_id
			return
		self.selected_user_id = user_id
		self.centerAt( (int(hw_pos['x']), int(hw_pos['y'])) )
		self.selected_user_id = user_id
		try:
			self.user_race = store.get_object('race', {'user_id': self.selected_user_id})
			self.selected_user_governers_count = len(store.get_governers(self.selected_user_id))
		except:
			pass
		self.update()
		
	def showGood(self, show_good):
		self.show_good_planets = show_good
		if self.show_good_planets:
			self.user_race = store.get_object('race', {'user_id':self.selected_user_id})
			self.selected_user_governers_count = len(store.get_governers(self.selected_user_id))

		self.update()

	def show_route(self, pf):
		self.pf = pf
	
	def set_planet_filter(self, pf):
		self.planet_filter_ptr = pf
