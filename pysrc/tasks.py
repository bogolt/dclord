import wx
import logging
import planet
import fleet
import unit
import dcevent
log = logging.getLogger('dclord')

class AccountTasks(wx.Window):
	def __init__(self, parent, acc, cb):
		wx.Window.__init__(self, parent, -1)
		self.account = acc
		self.callback = cb
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		log.debug("acc name %s"%(acc[1],))
		self.title = wx.StaticText(self,wx.ID_ANY, '%s'%(acc[1],))
		vbox.Add(self.title)
		
		#self.task_list = wx.ListView(self, wx.ID_ANY, style=wx.LC_NO_HEADER|wx.LC_REPORT)
		#vbox.Add(self.task_list)
		#self.task_list.InsertColumn(0,'task')
		#self.task_list.Append( ('Test',) )
		vbox.Layout()
		
		self.title.Bind(wx.EVT_LEFT_DCLICK, self.onActivated)
	
	def onActivated(self, evt):
		wx.PostEvent(self.callback, dcevent.SetMapPosEvent(attr1=self.account.hw_pos))


class TasksPanel(wx.Panel):
	def __init__(self, parent, conf, db):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		self.conf = conf
		self.db = db
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)
		self.accounts = {}
		self.update()
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
		
	def update(self):
		log.debug('update tasks %d'%(len(self.accounts),))
		for login,name,hw,id in self.db.accounts():
			if id in self.accounts:
				continue
			tasks = AccountTasks(self, (login,name,hw,id), self.GetParent())
			log.debug('add tasks %s'%(name,))
			self.accounts[id] = tasks
			self.sizer.Add(tasks)
		self.sizer.Layout()
	
