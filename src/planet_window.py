import wx.aui
import logging
import db
import util
import event
import config
import image
import unit_list

log = logging.getLogger('dclord')

class PlanetWindow(wx.Window):
	def __init__(self, parent, coord = None, turn = None):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.turn = turn if turn else db.getTurn()
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.set_coord(coord)
		
	def set_coord(self, coord):
		self.coord = coord
		self.sizer.DeleteWindows()
		
		if not self.coord:
			self.sizer.Layout()
			return
		
		owner_id = 0
		planet_name = ''
		for planet in db.planets(self.turn, ['x=%d'%(coord[0],), 'y=%d'%(coord[1],)], ('x','y','owner_id','o','e','m','t','s', 'name')):
			planet_name = planet.get('name', '')
			owner = planet['owner_id']
			if not owner:
				break
			owner_id = int(owner)
			
		
		owner_name = 'unknown'
		if owner_id > 0:
			for res in db.players(self.turn, ['player_id=%s'%(owner_id,)]):
				owner_name = res['name']
		else:
			owner_name = '<empty>'
		
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, '%s:%s %s'%(coord[0],coord[1], planet_name)))
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, owner_name))
		self.sizer.Layout()

class UnitStackWindow(wx.Window):
	def __init__(self, parent, owner_id, unit):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add( unit_list.UnitPrototypeWindow(self, unit) )
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		
		self.units = {}
		self.user_name = db.getUserName(owner_id)

		self.text = wx.StaticText(self, wx.ID_ANY, '%d units, [%s]'%(len(self.units), self.user_name))
		self.sizer.Add(self.text)
		self.sizer.Layout()
		
		self.add(unit)
	
	def add(self, unit):
		self.units[unit['id']] = unit
		self.update()
		
	def update(self):
		self.text.SetLabel('%d units, [%s]'%(len(self.units), self.user_name))
	

import  wx.lib.scrolledpanel as scrolled
class FleetWindow(scrolled.ScrolledPanel):
	def __init__(self, parent, coord = None, turn = None):
		scrolled.ScrolledPanel.__init__(self, parent, -1, size=(200,200))
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		
		self.setOwnedUnits(coord, turn)
		self.setAlienUnits(coord, turn)
		
		self.SetSizer( self.vbox )
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
		
		self.Bind(wx.EVT_SIZE, self.onSize, self)
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
	
	def setOwnedUnits(self, coord, turn):
		units = {}
		if not coord:
			return
		
		log.info('requesting fleet info at %s'%(coord,))
		for fleet,unit in db.all_ownedUnits(turn, coord):
			cl = int(fleet['owner_id']), int(unit['class'])
			if cl in units:
				units[cl].add(unit)
			else:
				uwindow = UnitStackWindow(self, cl[0], unit)
				self.vbox.Add( uwindow)
				units[cl] = uwindow
		for u in units.values():
			u.update()
	
	def setAlienUnits(self, coord, turn):
		units = {}
		if not coord:
			return
		
		#type of alien unit: (carapase, weight)
		#TODO: develop kind of alien Ship Unit Type, and evristicly fit ships into some of them
		# based on real unit id it's speed, transport capacity, invisibility ability and war attributes can be determined
		# it's name can be read when unit destroyed
		
		#  some values could be entered manually
		keys = {}
		for fleet,unit in db.all_alienUnits(turn, coord):
			key = int(fleet['owner_id']), int(unit['carapace']), int(unit['weight'])
			if key in keys:
				keys[key].add(unit)
			else:
				uwindow = UnitStackWindow(self, fleet['owner_id'], unit)
				keys[key] = uwindow
				uwindow.update()
				self.vbox.Add( uwindow)
		
class InfoPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
			
		self.sizer = wx.BoxSizer(wx.VERTICAL)	
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		self.pos = (0,0)
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		self.turn = db.getTurn()

	def selectObject(self, evt):
		self.pos = evt.attr1
		self.update()

	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
			
	def update(self, turn = None):
		if turn:
			self.turn = turn
		log.info('updating info panel, pos %s turn %d'%(self.pos, self.turn))
		self.sizer.DeleteWindows()
		self.sizer.Add( PlanetWindow(self, self.pos, self.turn) )
		self.sizer.Add( FleetWindow(self, self.pos, self.turn), 1, flag=wx.EXPAND | wx.ALL)
		self.sizer.Layout()
