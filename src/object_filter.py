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
		self.sizer.Layout()
	
	def onShowKnown(self, evt):
		config.options['filter']['inhabited_planets'] = int(self.show_known.IsChecked())
		if not config.options['filter']['inhabited_planets']:
			serialization.loadGeoPlanets()
		wx.PostEvent(self.GetParent(), event.MapUpdate(attr1=None, attr2=None))
