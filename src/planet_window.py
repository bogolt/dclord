import wx.aui
import logging
import db
import util
import event
import config
import image

log = logging.getLogger('dclord')

class PlanetWindow(wx.Window):
	def __init__(self, parent, coord = None):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.set_coord(coord)
		
	def set_coord(self, coord):
		self.coord = coord
		self.sizer.Clear()
		
		if not self.coord:
			return
		
		owner_id = 0
		for planet in db.planets(db.getTurn(), ['x=%d'%(coord[0],), 'y=%d'%(coord[1],)]):
			owner_id = int(planet['owner_id'])
		
		owner_name = 'unknown'
		for res in db.players(db.getTurn(), ['player_id=%s'%(owner_id,)]):
			owner_name = res['name']
		
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, '%s:%s'%coord))
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, owner_name))
		self.sizer.Layout()


class InfoPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
			
		self.sizer = wx.BoxSizer(wx.VERTICAL)	
		self.SetSizer(self.sizer)
		self.sizer.Layout()

	def selectObject(self, evt):
		self.sizer.Clear()
		self.sizer.Add( PlanetWindow(self, evt.attr1) )
		self.sizer.Layout()
