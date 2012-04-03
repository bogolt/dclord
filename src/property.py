import wx
import logging
import planet
log = logging.getLogger('dclord')

class PlanetView(wx.Window):
	def __init__(self, parent, planet = None):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.planet = planet
		text=''
		if self.planet:
			text = '%s %s'%(self.planet.owner_id,self.planet.name)
		self.name = wx.StaticText(self,wx.ID_ANY, text)

	def set(self, planet=None):
		self.planet = planet

		text=u''
		if self.planet:
			text = u'%s %s'%(self.planet.owner_id,self.planet.name)
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
		self.tree.SetImageList(self.conf.imageList.imgList)
		
		l.Add(self.tree, 2, wx.EXPAND)
		self.SetSizer(l)
		self.SetAutoLayout(True)
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		self.SetAutoLayout(True)
	
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()

	def set(self, pl):
		self.tree.DeleteAllItems()
		self.planetView.set(pl)
		if not pl:
			return
			
		root = self.tree.AddRoot('rt')

		if isinstance(pl, planet.OwnedPlanet):
			bc = {}
			for unit in pl.garrison:
				bc.setdefault(unit.bc, []).append(unit)
			
			for ulist in bc.values():
				unit = ulist[0]
				self.tree.AppendItem(root, 'x%d'%(len(ulist),), self.conf.imageList.getImageKey(unit.bc, unit.proto.carapace, unit.proto.color))
		self.tree.ExpandAll()
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

		return
		
		root = self.tree.AddRoot('rt')
		users = {}
		for fleet in fleets:
			name = '? unknown'
			if fleet.owner_id:
				name = fleet.owner.name
			
			if not (name in users.keys()):
				users[name] = self.tree.AppendItem(root, name)
			fn = 'unknown'
			if fleet.name:
				fn = fleet.name
			fobj = self.tree.AppendItem(users[name], fn)
			log.debug('append fleet %s of %s'%(fn, name))
			for unit in fleet.units:
				imgKey = self.conf.imageList.getImageKey(unit.proto)
				self.tree.AppendItem(fobj, str(unit.proto.weight), imgKey)
				log.debug('unit tree: append item wg %s, img %s'%(unit.proto.weight, imgKey))

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
