import logging
import unit
import wx
import wx.lib.scrolledpanel

log = logging.getLogger('dclord')

class UnitWindow(wx.Window):
	def __init__(self, parent, conf, u):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		self.unit = u
		self.conf = conf
		#self.SetBackgroundColour(wx.Color(0,0,0))
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		img = wx.StaticBitmap(self, wx.ID_ANY)
		img.SetBitmap( conf.imageList.imgList.GetBitmap(conf.imageList.getImageKey(u.bc, u.proto.carapace, u.proto.color)) )
		hbox.Add(img)


		vbox = wx.BoxSizer(wx.VERTICAL)
		self.add_support(vbox, self.unit.fleet.owner.race.main, self.unit.proto.support_main)
		self.add_support(vbox, self.unit.fleet.owner.race.second, self.unit.proto.support_second)
		hbox.Add(vbox)
		self.add_fly_spec(vbox, self.unit)

		self.SetSizer(hbox)
		hbox.Layout()
		
	def add_support(self, sizer, res_type, res_value):
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		img_res = wx.StaticBitmap(self, wx.ID_ANY)
		img_res.SetBitmap( self.conf.get_image('%s_ico.gif'%(res_type,) ))
		hbox.Add(img_res)
		hbox.Add( wx.StaticText(self,wx.ID_ANY, '%0.2f'%(res_value,)))
		sizer.Add(hbox)
	
	def add_fly_spec(self, sizer, u):
		hbox = wx.BoxSizer(wx.VERTICAL)
		if u.proto.fly.fly_speed > 0.000001:
			hbox.Add( wx.StaticText(self,wx.ID_ANY, 'Speed: %0.2f'%(self.unit.proto.fly.fly_speed,)))
			hbox.Add( wx.StaticText(self,wx.ID_ANY, 'Range: %0.2f'%(self.unit.proto.fly.fly_range,)))

		if u.proto.fly.transport_capacity >= 1:
			hbox.Add( wx.StaticText(self,wx.ID_ANY, 'Transport: %d'%(self.unit.proto.fly.transport_capacity,)))
			
		sizer.Add(hbox)


class ProtoWindow(wx.Window):
	def __init__(self, parent, conf, race, p, num):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		self.proto = p
		self.race = race
		self.conf = conf
		self.num = num
		#self.SetBackgroundColour(wx.Color(0,0,0))
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		img = wx.StaticBitmap(self, wx.ID_ANY)
		img.SetBitmap( conf.imageList.imgList.GetBitmap(conf.imageList.getImageKey(p.id, p.carapace, p.color)) )
		hbox.Add(img)		
		hbox.Add( wx.StaticText(self,wx.ID_ANY, 'x%d'%(self.num,)))
		
		vboxs = wx.BoxSizer(wx.VERTICAL)
		self.add_support(vboxs, self.race.main, self.proto.support_main)
		self.add_support(vboxs, self.race.second, self.proto.support_second)
		hbox.Add(vboxs)
		
		vbox.Add(hbox)
		
		self.add_fly_spec(vbox)

		self.SetSizer(vbox)
		vbox.Layout()
		
	def add_support(self, sizer, res_type, res_value):
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		img_res = wx.StaticBitmap(self, wx.ID_ANY)
		img_res.SetBitmap( self.conf.get_image('%s_ico.gif'%(res_type,) ))
		hbox.Add(img_res)
		hbox.Add( wx.StaticText(self,wx.ID_ANY, '%0.2f'%(res_value,)))
		sizer.Add(hbox)
	
	def add_fly_spec(self, sizer):
		hbox = wx.BoxSizer(wx.VERTICAL)
		if self.proto.fly.fly_speed > 0.000001:
			hbox.Add( wx.StaticText(self,wx.ID_ANY, 'Speed: %0.2f'%(self.proto.fly.fly_speed,)))
			hbox.Add( wx.StaticText(self,wx.ID_ANY, 'Range: %0.2f'%(self.proto.fly.fly_range,)))

		if self.proto.fly.transport_capacity >= 1:
			hbox.Add( wx.StaticText(self,wx.ID_ANY, 'Transport: %d'%(self.proto.fly.transport_capacity,)))
			
		sizer.Add(hbox)


class AccountUnitsPanel(wx.Window):
	def __init__(self, parent, conf, db):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		self.conf = conf
		self.db = db
		self.units = []
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)		
		#self.scrolled = wx.ScrolledWindow(self, wx.ID_ANY)
		#self.sz.Add(self.scrolled)
		self.SetSizer(self.sizer)
		
		#self.sizer = wx.BoxSizer(wx.VERTICAL)
		#self.scrolled.SetSizer(self.sizer)
		#self.SetAutoLayout(True)
		#self.accounts = {}
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
	
	def set_filter(self, acc, can_fly = True, existing_units = True, transportable = False, min_transport_cells = 0 ):
		self.units = []
		self.sizer.DeleteWindows()

		self.sizer.Add( wx.StaticText(self, wx.ID_ANY, '%s'%(acc.name,)) )
		for u in acc.filter_protos(can_fly, transportable, min_transport_cells):
			type_units = acc.get_type_units(u.id)
			if not type_units and existing_units:
				log.debug('no units of proto %d exist on account %s'%(u.id, acc.name))
				continue
			un = ProtoWindow( self, self.conf, acc.race, u, len(type_units))
			self.units.append( un)
			self.sizer.Add(un)
		self.Layout()
	
	def set_unit(self, u):		
		self.units = []
		self.sizer.DeleteWindows()
		un = UnitWindow( self, self.conf, u)
		self.units.append( un)
		self.sizer.Add(un)
		self.Layout()

class UnitsPanel(wx.lib.scrolledpanel.ScrolledPanel):
	def __init__(self, parent, conf, db):
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, size=(120,200))
		self.conf = conf
		self.db = db
		self.accounts = []
			
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)
		self.accounts = {}
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
	
	def set_filter(self, can_fly = True, transportable = False, min_transport_cells = 0 ):
		return
		
		self.accounts = []
		self.sizer.DeleteWindows()
		
		for acc in self.db.accounts.values():
			print 'adding acc %s on unit panel'%(acc.name,)
			acc_panel = AccountUnitsPanel(self, self.conf, self.db)
			acc_panel.set_filter(acc)
			self.accounts.append(acc_panel)
			self.sizer.Add(acc_panel)
		self.sizer.Layout()
		self.SetupScrolling(scroll_x=False)
	
