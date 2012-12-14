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
		log.info('setting coord %s'%(coord,))
		self.coord = coord
		self.sizer.Clear()
		
		if not self.coord:
			return
		
		owner = 'unknown'
		for planet in db.planets(db.getTurn(), ['x=%d'%(coord[0],), 'y=%d'%(coord[1],)]):
			owner = planet['owner_id']
			#self.sizer.Add(wx.StaticText(self, wx.ID_ANY, 'owner is %s'%(planet['owner_id'],)))
		
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, 'owner is "%s"'%(owner,)))
		self.sizer.Layout()


class InfoPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		
		#self.planet = PlanetWindow(self)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)	
		#self.sizer.Add(self.planet)
		self.SetSizer(self.sizer)
		self.sizer.Layout()

	def selectObject(self, evt):
		self.sizer.Clear()
		self.sizer.Add( PlanetWindow(self, evt.attr1) )
		self.sizer.Layout()
