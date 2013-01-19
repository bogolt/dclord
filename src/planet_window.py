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
	def __init__(self, parent, coord = None):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
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
		for planet in db.planets(db.getTurn(), ['x=%d'%(coord[0],), 'y=%d'%(coord[1],)], ('x','y','owner_id','o','e','m','t','s', 'name')):
			planet_name = planet.get('name', '')
			owner = planet['owner_id']
			if not owner:
				break
			owner_id = int(owner)
			
		
		owner_name = 'unknown'
		if owner_id > 0:
			for res in db.players(db.getTurn(), ['player_id=%s'%(owner_id,)]):
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
		
		self.add(unit)
	
	def add(self, unit):
		self.units[unit['id']] = unit
		
	def update(self):
		self.sizer.Add( wx.StaticText(self, wx.ID_ANY, '%d units, [%s]'%(len(self.units), self.user_name)))
		self.sizer.Layout()
	

import  wx.lib.scrolledpanel as scrolled
class FleetWindow(scrolled.ScrolledPanel):
	def __init__(self, parent, coord = None):
		scrolled.ScrolledPanel.__init__(self, parent, -1, size=(200,200))
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		
		self.setOwnedUnits(coord)
		self.setAlienUnits(coord)
		
		self.SetSizer( self.vbox )
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
		
		self.Bind(wx.EVT_SIZE, self.onSize, self)
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
	
	def setOwnedUnits(self, coord):
		units = {}
		if not coord:
			return
		
		log.info('requesting fleet info at %s'%(coord,))
		for fleet,unit in db.all_ownedUnits(db.getTurn(), coord):
			cl = int(fleet['owner_id']), int(unit['class'])
			if cl in units:
				units[cl].add(unit)
			else:
				uwindow = UnitStackWindow(self, cl[0], unit)
				self.vbox.Add( uwindow)
				units[cl] = uwindow
		for u in units.values():
			u.update()
	
	def setAlienUnits(self, coord):
		units = {}
		if not coord:
			return
		
		for fleet,unit in db.all_alienUnits(db.getTurn(), coord):
			uwindow = UnitStackWindow(self, fleet['owner_id'], unit)
			uwindow.update()
			self.vbox.Add( uwindow)
		
class InfoPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
			
		self.sizer = wx.BoxSizer(wx.VERTICAL)	
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		self.Bind(wx.EVT_SIZE, self.onSize, self)

	def selectObject(self, evt):
		self.sizer.DeleteWindows()
		self.sizer.Add( PlanetWindow(self, evt.attr1) )
		self.sizer.Add( FleetWindow(self, evt.attr1), 1, flag=wx.EXPAND | wx.ALL)
		self.sizer.Layout()
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
			
