import wx
import logging
import db
import config

log = logging.getLogger('dclord')

class FilterPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		
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
		for acc in config.accounts():
			if acc['login'] in self.accounts:
				continue
			if 'id' in acc:
				name = db.getUserName(acc['id'])
				log.debug("got user name %s for user id %s"%(name, acc['id']))
				login = wx.StaticText(self,wx.ID_ANY, '%s'%(name,))
				self.accounts[acc['login']] = login
				self.sizer.Add(login)
		self.sizer.Layout()
	
