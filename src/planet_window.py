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
		self.sizer.DeleteWindows()
		
		if not self.coord:
			self.sizer.Layout()
			return
		
		owner_id = 0
		planet_name = ''
		for planet in db.planets(db.getTurn(), ['x=%d'%(coord[0],), 'y=%d'%(coord[1],)], ('x','y','owner_id','o','e','m','t','s', 'name')):
			owner_id = int(planet['owner_id'])
			planet_name = planet['name']
		
		owner_name = 'unknown'
		if owner_id > 0:
			for res in db.players(db.getTurn(), ['player_id=%s'%(owner_id,)]):
				owner_name = res['name']
		else:
			owner_name = '<empty>'
		
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, '%s:%s %s'%(coord[0],coord[1], planet_name)))
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, owner_name))
		self.sizer.Layout()


class InfoPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
			
		self.sizer = wx.BoxSizer(wx.VERTICAL)	
		self.SetSizer(self.sizer)
		self.sizer.Layout()

	def selectObject(self, evt):
		self.sizer.DeleteWindows()
		self.sizer.Add( PlanetWindow(self, evt.attr1) )
		self.sizer.Layout()
