import wx
import logging
import db
import event
import config
import serialization

log = logging.getLogger('dclord')

class FilterPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)
		self.show_known = wx.CheckBox(self, -1, "Inhabited planets")
		self.show_known.SetValue( int(config.options['filter']['inhabited_planets']))
		self.sizer.Add(self.show_known)
		self.active_user = None
		self.accounts = {}
		self.update()
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		self.show_known.Bind(wx.EVT_CHECKBOX, self.onShowKnown)
		
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
				log.debug("%s => %s"%(acc['id'], name))
				login = wx.StaticText(self,wx.ID_ANY, '%s'%(name,))				
				self.accounts[acc['login']] = login
				self.sizer.Add(login)
				if not self.active_user:
					self.selectUser(acc['login'])
				login.Bind(wx.EVT_LEFT_DCLICK, self.onChangeUser)
		self.sizer.Layout()
	
	def onChangeUser(self, evt):
		for login, obj in self.accounts.iteritems():
			if obj == evt.GetEventObject():
				print 'choosing user %s'%(login,)
				self.selectUser(login)
				
	def selectUser(self, login):
		wx.PostEvent(self.GetParent(), event.UserSelect(attr1=login, attr2=None))
	
	def onShowKnown(self, evt):
		config.options['filter']['inhabited_planets'] = int(self.show_known.IsChecked())
		if not config.options['filter']['inhabited_planets']:
			serialization.loadGeoPlanets()
		wx.PostEvent(self.GetParent(), event.MapUpdate(attr1=None, attr2=None))
