import wx
import logging
import planet
import fleet
import unit
log = logging.getLogger('dclord')

class AccountTasks(wx.Window):
	def __init__(self, parent, acc):
		wx.Window.__init__(self, parent, -1)
		self.account = acc
		self.title = wx.StaticText(self,wx.ID_ANY, acc.name)

class TasksPanel(wx.Panel):
	def __init__(self, parent, conf, db):
		wx.Window.__init__(self, parent, -1)
		self.conf = conf
		self.db = db
		
		l = wx.BoxSizer(wx.VERTICAL)
		for acc in self.db.accounts.values():
			l.Add( AccountTasks(self, acc))
		self.SetAutoLayout(True)
	
