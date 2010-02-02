import wx
from wx import xrc

class AccountsFrame(wx.Frame):
	def __init__(self):
		f=wx.PreFrame()
		self.PostCreate(f)
		self.Bind( wx.EVT_WINDOW_CREATE , self.OnCreate)
		
		self.users = None
		self.conf = None
		
	def setConf(self, cf):
		self.conf = cf
	
	def OnCreate(self,evt):
		self.Unbind ( wx.EVT_WINDOW_CREATE )
		wx.CallAfter(self.__PostInit)
		evt.Skip()
		return True

	def __PostInit(self):
		self.users = xrc.XRCCTRL(self, 'users')
		self.users.InsertColumn(0,'login', width=160)
		self.users.InsertColumn(1,'password', width=120)
		
		cancel = xrc.XRCCTRL(self, 'cancel')
		self.Bind(wx.EVT_BUTTON, self.close, cancel)
		
		ok = xrc.XRCCTRL(self, 'ok')
		self.Bind(wx.EVT_BUTTON, self.save, ok)
		
		add = xrc.XRCCTRL(self, 'add')
		self.Bind(wx.EVT_BUTTON, self.add, add)
		
		self.users.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.playersMenu)
		
		for user,pasw in self.conf.users.items():
			self.users.Append((user,pasw))
	

	def close(self, evt):
		self.Close()

	def add(self, evt):
		unameCtrl = xrc.XRCCTRL(self, 'userName')
		uname = unameCtrl.GetValue()
		if not uname:
			return
		paswCtrl = xrc.XRCCTRL(self, 'password')
		pwd = paswCtrl.GetValue()
		if not pwd:
			return
		
		self.users.Append((uname, pwd))
		
		unameCtrl.Clear()
		paswCtrl.Clear()	
	
	def save(self, evt):
		self.conf.users = {}
		for i in range(0, self.users.GetItemCount()):
			log,pas = self.users.GetItem(i,0).GetText(),self.users.GetItem(i,1).GetText()
			self.conf.users[log] = pas
			
		self.conf.saveUsers()
			
		self.Close()
		
	def removeItem(self, evt):
		item = self.users.GetFocusedItem()
		self.users.DeleteItem(item)
		
	def playersMenu(self, evt):
		id = self.users.GetFocusedItem()
		if id==-1:
			return
		item = self.users.GetItem(id)
		menu = wx.Menu()
		rem = menu.Append(wx.ID_ANY, 'remo&ve %s'%(item.GetText()))
		self.Bind(wx.EVT_MENU, self.removeItem, rem)
		self.users.PopupMenu(menu, evt.GetPoint())
		menu.Destroy()