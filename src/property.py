import wx

class PlanetProperty(wx.Window):
	def __init__(self, parent, planet):
		wx.Window.__init__(self, parent, size=(150,150))
		self.planet = planet
		l = wx.BoxSizer(wx.VERTICAL)
		
		t = wx.StaticText(self, wx.ID_ANY, '%s %s'%(planet.ownerName,planet.name,))
		l.Add(t, 1, wx.ALL)
		self.SetSizer(l)

class FleetProperty(wx.Window):
	def __init__(self, parent, fleet):
		wx.Window.__init__(self, parent, size=(150,150))
		self.fleet = fleet
		l = wx.BoxSizer(wx.VERTICAL)
		
		t = wx.StaticText(self, wx.ID_ANY, '%s/%s'%(fleet.ownerName, fleet.name))
		l.Add(t, 1, wx.ALL)
		self.SetSizer(l)

class Property(wx.ScrolledWindow):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, size=(250,300), style=wx.SUNKEN_BORDER)

		#self.SetBackgroundColour(wx.WHITE)
		self.sizer = wx.BoxSizer( wx.VERTICAL )
		
		#self.setData(objects)

		self.SetSizer(self.sizer)
		self.Layout()

	def setData(self, data):
		# delete all sizer-managed windows
		self.sizer.DeleteWindows()
		
		if data[0]:
			self.sizer.Add(PlanetProperty(self, data[0]), 0, wx.ALL)		
		
		for o in data[1]:
			self.sizer.Add(FleetProperty(self, o), 0, wx.ALL)
			
		self.Layout()	
