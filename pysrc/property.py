import wx
import logging
import planet
import fleet
import dcevent
import unit
log = logging.getLogger('dclord')

class PlanetView(wx.Window):
	def __init__(self, parent, db, planet = None):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.planet = planet
		self.db = db
		self.name = wx.StaticText(self,wx.ID_ANY, "")

	def set(self, planet=None):
		self.planet = planet

		text=u''
		if self.planet:
			if self.planet.owner_id > 0:
				text += self.db.get_player_name(self.planet.owner_id);
			if self.planet.name:
				text += ' ' + self.planet.name
		self.name.SetLabel(text)
		
class PlanetProperty(wx.Panel):
	def __init__(self, parent, conf, db):
		wx.Window.__init__(self, parent, size=(150,150))
		self.planet = None
		self.conf = conf
		self.db = db
		l = wx.BoxSizer(wx.VERTICAL)
		self.planetView = PlanetView(self, self.db)
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
	def __init__(self, parent, conf, db):
		wx.Window.__init__(self, parent, size=(150,150))
		self.fleet = []
		l = wx.BoxSizer(wx.VERTICAL)
		self.tree = wx.TreeCtrl(self, style = wx.TR_HIDE_ROOT)
		self.conf = conf
		self.db = db
		self.tree.AssignImageList(self.conf.imageList.imgList)
		
		l.Add(self.tree, 2, wx.EXPAND)
		self.SetSizer(l)
		self.SetAutoLayout(True)
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onChanged, self.tree)
		
	def onChanged(self, evt):
		selected = evt.GetItem()
		if selected:
			item = self.tree.GetPyData(selected)
			if isinstance(item, unit.Unit):
				log.debug('item selected %s of bc %s has %d actions'%(item.id,item.bc, len(item.proto.actions)))
				wx.PostEvent(self.GetParent(), dcevent.SelectUnit(attr1=item))
				
				#perform action
				#for action_id in item.proto.actions.keys():
				#	log.debug('request action %d perform for item %d '%(action_id, item.id))
				#	wx.PostEvent(self.GetParent(), dcevent.RequestActionPerform(attr1=(self.db.get_fleet_owner_id(item.fleet_id), item.id, action_id)))
				#	break
		
		
	
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()

	def append_unit(self, item, fl):
		bc = {}
		for u in fl.units:
			bc.setdefault(u.bc, []).append(u)
		for units in bc.values():
			u = units[0]
			carapase,color=None,None
			
			if isinstance(u, unit.Unit):
				carapace = u.proto.carapace
				color = u.proto.color
			else:
				carapace = u.carapace
				color = u.color
			
			item = self.tree.AppendItem(item, '%d x%d'%(u.bc, len(units)), self.conf.imageList.getImageKey(u.bc, carapace, color))
			self.tree.SetPyData(item, u)

	def set(self, fleets):
		self.tree.DeleteAllItems()
		if not fleets:
			return

		root = self.tree.AddRoot('rt')
		users = {}
		for fl in fleets:			
			if fl.owner_id:
				users.setdefault(fl.owner_id,[]).append(fl)
			else:
				users.setdefault(-1,[]).append(fl)
				
		for player_id, fleets in users.items():
			player_fleets = self.tree.AppendItem(root, self.db.get_player_name(player_id))
			for fl in fleets:
				#( hm, or there is ) no need to show empty fleets
				#if not fleet.units:
				#	continue

				tta = 0
				s = ''
				if fl.flying:
					if isinstance(fl, fleet.Fleet):
						s = '[%s tta: %d]'%(fl.name, fl.tta)
					else:
						s = '[unknown tta: %d]'%(fl.tta,)
				else:
					s = fl.name

				fl_item = self.tree.AppendItem(player_fleets, s)
				self.append_unit(fl_item, fl)
			
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
