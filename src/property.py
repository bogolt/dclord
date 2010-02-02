import wx

class PlanetView(wx.Window):
	def __init__(self, parent, planet = None):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.planet = planet
		text=''
		if self.planet:
			text = '%s %s'%(self.planet.owner,self.planet.name)
		self.name = wx.StaticText(self,wx.ID_ANY, text)

	def set(self, planet=None):
		self.planet = planet

		text=u''
		if self.planet:
			text = u'%s %s'%(self.planet.owner,self.planet.name)
		self.name.SetLabel(text)
		
class PlanetProperty(wx.Panel):
	def __init__(self, parent, conf):
		wx.Window.__init__(self, parent, size=(150,150))
		self.planet = None
		self.conf = conf
		l = wx.BoxSizer(wx.VERTICAL)
		self.planetView = PlanetView(self)
		l.Add(self.planetView)
		self.tree = wx.TreeCtrl(self, style = wx.TR_HIDE_ROOT)
		self.conf = conf
		self.tree.AssignImageList(self.conf.imageList.imgList)
		
		l.Add(self.tree, 2, wx.EXPAND)
		self.SetSizer(l)
		self.SetAutoLayout(True)
		self.Bind(wx.EVT_SIZE, self.onSize, self)
	
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()

	def set(self, planet):
		self.tree.DeleteAllItems()
		self.planetView.set(planet)
		if not planet:
			return

		root = self.tree.AddRoot('rt')

		for u in planet.garrison():
			text = ''
			if u.quantity > 1:
				text = str(u.quantity)
			self.tree.AppendItem(root, text, self.conf.imageList.getImageKey(u.proto))

		self.tree.ExpandAll()
		self.SetAutoLayout(True)
		self.Layout()

class FleetProperty(wx.Panel):
	def __init__(self, parent, conf):
		wx.Window.__init__(self, parent, size=(150,150))
		self.fleet = []
		l = wx.BoxSizer(wx.VERTICAL)
		self.tree = wx.TreeCtrl(self, style = wx.TR_HIDE_ROOT)
		self.conf = conf
		self.tree.AssignImageList(self.conf.imageList.imgList)
		
		l.Add(self.tree, 2, wx.EXPAND)
		self.SetSizer(l)
		self.SetAutoLayout(True)
		self.Bind(wx.EVT_SIZE, self.onSize, self)
	
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()

	def set(self, fleets):
		self.tree.DeleteAllItems()
		if not fleets:
			return

		root = self.tree.AddRoot('rt')
		users = {}
		for f in fleets:
			name = '? unknown'
			if f.owner:
				name = f.owner.name
			
			if not (name in users.keys()):
				users[name] = self.tree.AppendItem(root, name)
			fn = 'unknown'
			if f.name:
				fn = f.name
			fobj = self.tree.AppendItem(users[name], fn)
			for u in f.units:
				imgKey = self.conf.imageList.getImageKey(u.proto)
				self.tree.AppendItem(fobj, str(u.proto.weight), imgKey)

		self.tree.ExpandAll()
		self.SetAutoLayout(True)
		self.Layout()

class Messages(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, size=(850,50), style=wx.SUNKEN_BORDER)
		sz = wx.BoxSizer(wx.VERTICAL)
		self.ctrl = wx.ListView(self, wx.ID_ANY, style=wx.LC_NO_HEADER|wx.LC_REPORT)
		self.ctrl.InsertColumn(0,'message', width=859)
		
		sz.Add(self.ctrl,1,wx.EXPAND)
		
		self.SetSizer(sz)
		self.SetAutoLayout(True)
		self.Layout()
		
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()

	def addEvent(self, msg):
		self.ctrl.Append((msg,))