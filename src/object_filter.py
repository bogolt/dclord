import wx
import logging
from store import store
import event
import config
import serialization
import planet_window
import wx.lib.agw.floatspin
import image

log = logging.getLogger('dclord')

def_color = wx.Colour(0, 0, 0)
sel_color = wx.Colour(245,3,3)

class RangeFilter(wx.Window):
	def __init__(self, parent, value_min=0, value_max=-1):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		self.value_min = value_min
		self.value_max = value_max
		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		#self.value_min_ctrl = wx.lib.agw.floatspin.FloatTextCtrl(self, wx.ID_ANY, '')
		#self.sizer.Add(self.value_min_ctrl)
		self.SetSizer(self.sizer)
		self.Layout()

class ProtoFilter(wx.Window):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		self.f = RangeFilter(self)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.f)
		self.SetSizer(sizer)
		self.Layout()


class PlayerFilter(wx.Window):
	def __init__(self, parent, only_my_users = True):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.users = {}
		for user in store.iter_objects_list('user'):
			if 'login' in user and user['login']:
				checkbox = wx.CheckBox(self, label=user['name'])
				checkbox.Bind(wx.EVT_CHECKBOX, self.userChanged)
				self.users[int(user['user_id'])] = checkbox
				checkbox.SetValue(False)
				sizer.Add(checkbox)
			
		self.SetSizer(sizer)
		
		self.Layout()
		
	def userChanged(self, evt):
		self.GetParent().updatePlanets()
		
	def player_ids(self):
		for uid, cb in self.users.iteritems():
			if cb.IsChecked():
				yield uid


import  wx.lib.scrolledpanel as scrolled
class PlanetList(scrolled.ScrolledPanel):
	def __init__(self, parent):
		scrolled.ScrolledPanel.__init__(self, parent, -1, size=(200,200))
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		#self.SetAutoLayout(True)
		self.SetupScrolling()
		self.planets = {}
		
	def has_planet(self, coord):
		if coord in self.planets:
			return True
		return False
		
	def addPlanets(self, players, buildings = None):
		self.sizer.DeleteWindows()
		
		for pl_id in players.player_ids():
			for planet in db.planets(db.getTurn(), ['owner_id=%d'%(pl_id,)] ):
				coord = (int(planet['x']), int(planet['y']))
				if buildings and not db.has_all_buildings(db.getTurn(), coord, buildings):
					continue
				p = planet_window.PlanetWindow(self, coord, db.getTurn())
				self.planets[coord] = p
				self.sizer.Add( p )
				
		self.sizer.Layout()
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
			

class BuildingCheckBox(wx.Window):
	def __init__(self, parent, uid):
		wx.Window.__init__(self, parent)
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		img = wx.StaticBitmap(self, wx.ID_ANY)
		bmp = image.getBcImage( uid, 20)
		if bmp:
			img.SetBitmap( bmp )
		sizer.Add( img )
		
		self.cb = wx.CheckBox(self, label='' )
		sizer.Add ( self.cb )
		
		self.cb.Bind(wx.EVT_CHECKBOX, self.building_filter)
		
		self.SetSizer(sizer)
		sizer.Layout()
		
	def building_filter(self, evt):
		self.GetParent().update_filters()
		
	def is_on(self):
		return self.cb.IsChecked()
			

class BuildingFilter(wx.Window):
	BARRACS = 4
	SHIPYARD = 5
	PALACE = 12
	GOVERN = 13
	FACTORY = 14
	CUSTOMS = 22
	CONSTRUCT=25
	PARTS_FACTORY=28
	LABORATORY=32
	SPECIALIST=34
	GODFATHER=36
	CAPITAL=42
	
	def __init__(self, parent):
		wx.Window.__init__(self, parent)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
	
		
		self.buildings = {}
		
		#buildings  = [4,5,12,13,14,22,25,28,30,32,34,36,41,42]
		buildings  = [self.BARRACS, self.SHIPYARD, self.PALACE, self.GOVERN, self.FACTORY, self.CUSTOMS, self.CONSTRUCT, self.PARTS_FACTORY, self.LABORATORY, self.SPECIALIST, self.GODFATHER, self.CAPITAL]
		grid = wx.GridSizer(len(buildings)/3, 3)
		blds = []
		for uid in buildings:
			b = BuildingCheckBox(self, uid)
			self.buildings[uid] = b
			blds.append((b, 0, wx.EXPAND))
			#self.sizer.Add( b )
		
		grid.AddMany( blds )
		
		self.sizer.Add(grid)
		
		self.SetSizer(self.sizer)
		self.sizer.Layout()
	
	def get_selected_buildings(self):
		buildings_id_ids_list = []
		
		for bid, bcb in self.buildings.iteritems():
			if bcb.is_on():
				buildings_id_ids_list.append( bid )
		return buildings_id_ids_list
	
	def update_filters(self):
		self.GetParent().updatePlanets()

class FilterFrame(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(90,40))

		self.players = PlayerFilter(self)
		self.buildings = BuildingFilter(self)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.players)
		self.sizer.Add(self.buildings)
		#self.pl = PlanetList(self)
		#self.sizer.Add(self.pl)
		self.SetSizer(self.sizer)
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		#self.pl.addPlanets(self.players)
	
	def updatePlanets(self):
		self.pl.Destroy()
		#self.pl = PlanetList(self)
		self.sizer.Add(self.pl)
		#self.pl.addPlanets(self.players, self.buildings.get_selected_buildings())
		self.sizer.Layout()
		
		wx.PostEvent(self.GetParent(), event.MapUpdate())
		
	def is_planet_shown(self, coord):
		return self.pl.has_planet(coord)
	
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()

class FilterPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(90,40))
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)
		self.show_known = wx.CheckBox(self, -1, "Inhabited planets")
		self.show_known.SetValue( int(config.options['filter']['inhabited_planets']))
		self.sizer.Add(self.show_known)
		self.active_user = None
		self.accounts = {}
		self.update()
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		self.show_known.Bind(wx.EVT_CHECKBOX, self.onShowKnown)
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
		
	def update(self):
		log.debug('update tasks %d'%(len(self.accounts),))
		for r in store.iter_objects_list('user'):
			user_id = int(r['user_id'])
			name = r['name']
			
			if not 'login' in r or not r['login']:
				continue

			if user_id in self.accounts:
				self.accounts[user_id].SetLabel('%s (%s)'%(name, r['turn']))
				continue

			log.debug("%s => %s"%(user_id, name))
			login = wx.StaticText(self,wx.ID_ANY, '%s (%s)'%(name, r['turn']))
			self.accounts[user_id] = login
			self.sizer.Add(login)
			if not self.active_user:
				self.selectUser(user_id)
			login.Bind(wx.EVT_LEFT_DCLICK, self.onChangeUser)
		self.sizer.Layout()
	
	def onChangeUser(self, evt):
		for login, obj in self.accounts.iteritems():
			if obj == evt.GetEventObject():
				#print 'choosing user %s'%(login,)
				self.selectUser(login)
				
	def selectUser(self, user_id):
		if self.active_user:
			self.accounts[self.active_user].SetForegroundColour(def_color)
		self.accounts[user_id].SetForegroundColour(sel_color)
		self.active_user = user_id
		
		wx.PostEvent(self.GetParent(), event.UserSelect(attr1=user_id, attr2=None))
	
	def onShowKnown(self, evt):
		config.options['filter']['inhabited_planets'] = int(self.show_known.IsChecked())
		wx.PostEvent(self.GetParent(), event.MapUpdate(attr1=None, attr2=None))
