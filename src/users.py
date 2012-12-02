import wx
import logging
import config

log = logging.getLogger('dclord')

class UserLoginInfo(wx.Frame):
	def __init__(self, parent, t, cb, size=(120, 100)):
		self.cb = cb
		wx.Frame.__init__(self, parent, title=t)
		sz = wx.BoxSizer(wx.VERTICAL)
		
		lname = wx.StaticText(self, label='login')
		sz.Add(lname)
		
		self.ename = wx.TextCtrl(self, size=(90, -1))
		sz.Add(self.ename)

		lpass = wx.StaticText(self, label='password')
		sz.Add(lpass)

		self.epass = wx.TextCtrl(self)
		sz.Add(self.epass)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		sz.Add(hb)
		
		ok = wx.Button(self, label='&Ok')
		hb.Add(ok)
		self.Bind(wx.EVT_BUTTON, self.onOk, ok)
		
		cancel = wx.Button(self, label='&Cancel')
		hb.Add(cancel)
		self.Bind(wx.EVT_BUTTON, self.onCancel, cancel)

		self.Bind(wx.EVT_SIZE, self.onSize, self)

		self.SetSizer(sz)
		self.Layout()	
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()	
		
	def onOk(self, evt):
		self.cb.addUserInfo(self.ename.GetValue(), self.epass.GetValue())
		self.Close()
		
	def onCancel(self, evt):
		self.Close()

class UsersPanel(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, -1, title="Accounts", size=(320,200))
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.user_list = wx.ListCtrl(self, size=(555,100), style=wx.LC_REPORT|wx.BORDER_SUNKEN)

		sizer.Add(self.user_list, wx.ALL|wx.EXPAND)
		
		buttonAdd = wx.Button(self, label='&Add')
		buttonClose = wx.Button(self, label='&Close')
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.Add(buttonAdd)
		sz.Add(buttonClose)
		sizer.Add(sz)
		
		self.Bind(wx.EVT_BUTTON, self.add, buttonAdd)
		self.Bind(wx.EVT_BUTTON, self.close, buttonClose)
				
		self.user_list.InsertColumn(0,'login', width=160)
		self.user_list.InsertColumn(1,'password', width=120)
		self.loadUsers()
		
		self.user_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.userMenu)
		
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		
		self.SetSizer(sizer)
		self.Layout()
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()		
		
	def close(self, evt):
		self.Close()
		
	def removeItem(self, evt):
		item = self.user_list.GetFocusedItem()
		
		config.removeAccount( self.user_list.GetItem(item, 0).GetText() )
		self.user_list.DeleteItem(item)
		
	def userMenu(self, evt):
		id = self.user_list.GetFocusedItem()
		if id==-1:
			return
		item = self.user_list.GetItem(id)
		menu = wx.Menu()
		rem = menu.Append(wx.ID_ANY, 'remo&ve %s'%(item.GetText()))
		self.Bind(wx.EVT_MENU, self.removeItem, rem)
		self.user_list.PopupMenu(menu, evt.GetPoint())
		menu.Destroy()
		
	def addUserInfo(self, l, p):
		config.addAccount(l, p)
		self.user_list.Append((l, p))
		
	def add(self, evt):
		ul = UserLoginInfo(self, 'Add account', self)
		ul.Show()
				
	def loadUsers(self):
		self.user_list.DeleteAllItems()		
		for acc in config.accounts():
			if 'password' in acc and 'login' in acc:
				self.user_list.Append((acc['login'], acc['password']))
					
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
