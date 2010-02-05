import wx
#from math import atan,sin,cos
from dcevent import ObjectFocus
#from objects import Planet, Fleet

def diffPos(start, end):
	x0,y0 = start
	x1,y1=end
	return (x1-x0,y1-y0)
	
def realValue(visible):
	pos = int(visible) % 1000
	if pos == 0:
		return 1000
	return pos
	
def realPos(visible):
	return realValue(visible[0]), realValue(visible[1])
	
def intPos(pos):
	x,y=pos
	return int(x),int(y)
	
def add(c1, c2):
	return (c1[0]+c2[0], c1[1]+c2[1])
def sub(c1, c2):
	return (c1[0]-c2[0], c1[1]-c2[1])
def div(c1, d):
	return (c1[0]/d, c1[1]/d)
def mul(c1, d):
	return (c1[0]*d, c1[1]*d)

class Map(wx.Window):
	def __init__(self, parent, db, conf):
		wx.Window.__init__(self, parent, -1, size=(800,600), style=wx.NO_FULL_REPAINT_ON_RESIZE)
		
		self.conf= conf
	
		self.position = 1,1
		self.db = db
		self.anything = None
		self.update(False)
		
		x = int(self.conf.s['map']['last_pos_x'])
		y = int(self.conf.s['map']['last_pos_y'])
		if x!=-1 and y!=-1:
			self.position = (x,y)
		
		# is the map moving now ( right button pressed )		
		self.moving = False
		self.prevPos = (0,0)
		
		self.maxPlanetSize = 50
		self.minPlanetSize = 15
		
		self.planetSize = 30
		self.scrollStep = 1
		
		self.border=(15,15)
		self.coordShift = (0,0)
		self.selectedCell = None
		
		self.SetBackgroundColour(self.conf.s['map']['bg_color'])
		self.Bind(wx.EVT_PAINT, self.OnPaint)

		self.Bind(wx.EVT_RIGHT_DOWN, self.onRightDown)
		self.Bind(wx.EVT_RIGHT_UP, self.onRightUp)
		self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)		
		self.Bind(wx.EVT_MOTION, self.onMotion)
		self.Bind(wx.EVT_MOUSEWHEEL, self.onScroll)
		
	def update(self, shouldRefresh=True):		
		if not self.anything:
			self.anything = self.db.getNotEmptyCoord()
			if self.anything:
				self.position=sub(self.anything, (5,5))
		if shouldRefresh:
			self.Refresh()
	
	def OnPaint(self, event):
		dc = wx.PaintDC(self)
		size = self.GetClientSize()

		self.drawCoordinates(dc)

		dc.DestroyClippingRegion()
		dc.SetClippingRegion(self.coordShift[0], self.coordShift[1], size.width, size.height)		
		self.drawGrid(dc)
		dc.SetPen(wx.WHITE_PEN)
		
		xl = int(self.position[0])
		yl = int(self.position[1])
		
		#ask db to preload all items that we are looking for
		sz = div(size,self.planetSize)
		ps = (xl,yl)
		self.db.prepare(ps, sz)
		
		planets = self.db.getAreaPlanets((xl,yl), sz)
		for planet in planets.values():
			self.drawPlanet(dc, planet)
		
		fleets = self.db.getAreaFleets((xl,yl), sz)
		for flee in fleets.values():
			self.drawFleets(dc, flee)

	def onScroll(self, mouse):
		pos = mouse.GetPosition()
		logicPos = div(pos, float(self.planetSize))

		if mouse.GetWheelRotation() < 0:
			if(self.planetSize <= self.minPlanetSize):
				return
				
			self.planetSize-=self.scrollStep
		else:
			if(self.planetSize >= self.maxPlanetSize):
				return

			self.planetSize+=self.scrollStep

		#make sure mouse is pointing on the centre  of the scroll area ( just move the pos so that this _is_ the center )
		newScreenPos = mul(logicPos, self.planetSize)
		newScreenDiff = sub(newScreenPos, pos)
		newLogicDiff = div(newScreenDiff, self.planetSize)
		self.position=add(self.position, newLogicDiff)		
					
		self.Refresh()

	def onRightDown(self, mouse):
		self.moving = True
		self.prevPos = mouse.GetPosition()
		
	def onRightUp(self, mouse):
		self.moving = False

	def onLeftDown(self, mouse):
		diff = div(sub(mouse.GetPosition(), self.shift()), self.planetSize)		
		p=add(intPos(self.position), intPos(diff))

		objects = self.db.getObjects(p[0],p[1])
		wx.PostEvent(self.GetParent(), ObjectFocus(attr1=p, attr2=objects))
		
	def onMotion(self, mouse):
		if not self.moving:
			return

		curPos = mouse.GetPosition()
		diff = diffPos(curPos, self.prevPos)
		diff = div(diff, float(self.planetSize))
		
		dx,dy=diff

		if dx != 0 or dy != 0:
			x,y=self.position
			x+=dx
			y+=dy
			self.position=(x,y)
			self.Refresh()
			self.prevPos = curPos

	def drawFleets(self, dc, fleets):
		for f in fleets:
			self.drawFleet(dc, f)

	def drawFleet(self, dc, f):
		pos = f.coord
		
		if not f.turnsLeft or f.turnsLeft==0:
			if pos == f.posFrom and f.posFrom != f.coord: return
			x,y = mul(sub(pos, self.position), self.planetSize)
			dc.DrawCircle(x+3, y+3, 3)
			return

		sx,sy=f.posFrom
		dx,dy=f.coord
		
		sx,sy = mul(sub((sx,sy), self.position), self.planetSize)
		dx,dy = mul(sub((dx,dy), self.position), self.planetSize)
		
		width=self.planetSize/2

				
		# the fleet is flying, so draw it's route
		#dc.DrawLine(sx+self.planetSize/2,sy+self.planetSize/2, dx+self.planetSize/2, dy+self.planetSize/2)
		
		#get 2/3 of the line
		fx=(dx-sx)*2/3.0
		fy=(dy-sy)*2/3.0
		
		
		dc.SetPen(wx.Pen(self.conf.s['map']['fleet_route_color']))
		dc.DrawLine(sx+width,sy+width, sx+fx+width, sy+fy+width)
		
		dc.SetPen(wx.Pen(self.conf.s['map']['fleet_route_color'], 1, wx.DOT))		
		dc.DrawLine(dx+width,dy+width, sx+fx+width, sy+fy+width)
		
		dc.SetPen(wx.Pen(self.conf.s['map']['fleet_route_color']))
				
		# and place on the 2/3ds of this route
		cx,cy =  sx+fx+self.planetSize/2,sy+fy+self.planetSize/2
		dc.DrawCircle(cx,cy, 3);
		
		#o = 'unknown'
		#if f.owner:
		#	o = f.owner.name
		#text='%s/%s'%(o,f.name)
		#if f.turnsLeft!=0:
		#	text+='[%s]'%(f.turnsLeft,)
		#
		#dc.DrawText(text, cx+5, cy+4)
		
#		dc.DrawLine(sx+self.planetSize/2,sy+self.planetSize/2, ddx+self.planetSize/2, ddy+self.planetSize/2)

	def drawPlanet(self, dc, planet):
		#planet = self.planet[realPos(pos)]
		pos = planet.coord
		p = mul(sub(pos, self.position), self.planetSize)
	
		size = self.planetSize/2
		if 's' in planet.geo.keys():
			size = size * (planet.geo['s']/5+1) / 20.0
			if size < 1:
				size = 1

		x,y=p
		#TODO: Check why only one race will draw MAGENTA
		if planet.owner:
			if planet.owner.login in self.conf.users:
				dc.SetPen(wx.Pen(self.conf.s['map']['own_planet_color']))
				dc.SetBrush(wx.Brush(self.conf.s['map']['own_planet_color']))
				dc.DrawText(planet.owner.name,x+10,y)
			else:
				dc.SetPen(wx.Pen(self.conf.s['map']['inhabited_planet_color']))
				dc.SetBrush(wx.Brush(self.conf.s['map']['inhabited_planet_color']))
		else:
			dc.SetPen(wx.Pen(self.conf.s['map']['planet_color']))
			dc.SetBrush(wx.Brush(self.conf.s['map']['planet_color']))
		dc.DrawCircle(x+self.planetSize/2,y+self.planetSize/2, size)
		#if planet.owner:
		#	dc.DrawCircle(x+self.planetSize/2,y+self.planetSize/2, size - 4)
		#	for l in conf.users.items():
		#		text = l[0]
		#		if planet.owner.name == text:
		#			dc.DrawText(text, x+self.planetSize/2,y+self.planetSize/2)

#		if planet.owner:
#			dc.SetPen(wx.GREY_PEN)
#			dc.SetBrush(wx.Brush('GREY'))
		
#		if len(planet.geo)==5:
#			self.drawGeo(dc, p, planet.geo)

	def drawGeo(self, dc, pos, geo):
		if self.planetSize < 20:
			return
		x,y=pos

		maxRich = 2*self.planetSize/3
		y+=self.planetSize-maxRich
		x+=self.planetSize-20
		
		res = round(geo[1]/100.0 * maxRich)
		dc.SetBrush(wx.GREEN_BRUSH)
		dc.DrawRectangle(x,y+maxRich-res, 4, res)

		x+=5
		res = round(geo[2]/100.0 * maxRich)
		dc.SetBrush(wx.BLUE_BRUSH)
		dc.DrawRectangle(x,y+maxRich-res, 4, res)

		x+=5
		res = round(geo[3]/100.0 * maxRich)		
		dc.SetBrush(wx.RED_BRUSH)
		dc.DrawRectangle(x,y+maxRich-res, 4, res)

		x+=5
		res = round(geo[4]/100.0 * maxRich)		
		dc.SetBrush(wx.CYAN_BRUSH)
		dc.DrawRectangle(x,y+maxRich-res, 4, res)
		
		dc.SetBrush(wx.TRANSPARENT_BRUSH)

	def visiblePos(self, pos):
		return mul(pos, self.planetSize)

	def logicPos(self, pos):
		return div(pos, self.planetSize)
		
	def visibleGalaxySize(self):
		return self.GetClientSize() - self.border
		
#	def leftTopVisibleGalaxy(self):
#		return self.border

	def shift(self):
		xshift = self.position[0]-int(self.position[0])
		yshift = self.position[1]-int(self.position[1])
		
		dx=-self.planetSize*xshift
		dy=-self.planetSize*yshift
		return dx,dy

	def drawGrid(self, dc):
		size = self.visibleGalaxySize()

		dx,dy=self.shift()

		dc.SetPen(wx.Pen(self.conf.s['map']['grid_color']))
		y=0			
		for x in range(0, size.width/self.planetSize+2):			
			dc.DrawLine(dx + x*self.planetSize, dy+y*self.planetSize, dx+x*self.planetSize, y+size.height+self.planetSize)

		x=0
		for y in range(0, size.height/self.planetSize+2):			
			dc.DrawLine(dx + x*self.planetSize, dy+y*self.planetSize, y+size.width+self.planetSize, dy+self.planetSize*y)

	def drawCoordinates(self, dc):
		size = self.GetClientSize()
		f = dc.GetFont()
		f.SetPointSize(8)
		f.SetFamily(wx.FONTFAMILY_SCRIPT)
		dc.SetFont(f)
		
		dx,dy=self.shift()
		
		textSize=dc.GetTextExtent("9999")

		topCoordHeight = 0
		dc.DestroyClippingRegion()
		dc.SetPen(wx.Pen(self.conf.s['map']['coord_color']))
		#top(vertical) row of coordinates
		if self.planetSize < textSize[0]:
			i=1
			topCoordHeight = textSize[0]
			#rotated coordinates ( not enogth space for horizontal)
			dc.SetClippingRegion(textSize[0], 0, size.width, topCoordHeight)
			for x in range(1, size.width/self.planetSize+2):
				dc.DrawRotatedText(str(realValue(self.position[0]+i)), dx+x*self.planetSize+self.planetSize/2-textSize[1]/2,textSize[0], 90)
				i+=1
		else:
			topCoordHeight = textSize[1]
			#horizontal coordinates
			dc.SetClippingRegion(textSize[0], 0, size.width, topCoordHeight)
			i=1
			for x in range(1, size.width/self.planetSize+2):
				dc.DrawText(str(realValue(self.position[0]+i)), dx+x*self.planetSize,0)
				i+=1

		dc.DestroyClippingRegion()
		dc.SetClippingRegion(0, topCoordHeight, textSize[0], size.height)
		#left(horizontal) now of the coordiantes
		j=1
		for y in range(1, size.height/self.planetSize+2):
			dc.DrawText(str(realValue(self.position[1]+j)), 0, dy+y*self.planetSize)
			j+=1

		self.coordShift = (textSize[0], topCoordHeight)

