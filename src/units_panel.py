import logging
import unit
import wx

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
		
		#vbox = wx.BoxSizer(wx.VERTICAL)
		#self.title = wx.StaticText(self,wx.ID_ANY, acc.name)
		#vbox.Add(self.title)
		
		#self.task_list = wx.ListView(self, wx.ID_ANY, style=wx.LC_NO_HEADER|wx.LC_REPORT)
		#vbox.Add(self.task_list)
		#self.task_list.InsertColumn(0,'task')
		#self.task_list.Append( ('Test',) )
		self.SetSizer(hbox)
		hbox.Layout()
		
	def add_support(self, sizer, res_type, res_value):
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		img_res = wx.StaticBitmap(self, wx.ID_ANY)
		img_res.SetBitmap( self.conf.get_image('%s_ico.gif'%(res_type,) ))
		hbox.Add(img_res)
		hbox.Add( wx.StaticText(self,wx.ID_ANY, '%0.2f'%(res_value,)))
		sizer.Add(hbox)
			
		
		#self.title.Bind(wx.EVT_LEFT_DCLICK, self.onActivated)
	
class UnitsPanel(wx.Panel):
	def __init__(self, parent, conf, db):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		self.conf = conf
		self.db = db
		self.units = []
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)
		self.accounts = {}
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
	
	def set_unit(self, u):		
		self.units = []
		self.sizer.DeleteWindows()
		un = UnitWindow( self, self.conf, u)
		self.units.append( un)
		self.sizer.Add(un)
		self.Layout()
