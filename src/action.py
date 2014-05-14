import wx
import wx.aui
import logging
import db
import util
import event
import config
import image
import unit_list
from store import store

import  wx.lib.scrolledpanel as scrolled

log = logging.getLogger('dclord')

class ActionPanel(scrolled.ScrolledPanel):
	def __init__(self, parent):
		scrolled.ScrolledPanel.__init__(self, parent)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.actions = {}
				
		self.SetSizer(self.sizer)
		self.sizer.Layout()
	
		self.Bind(wx.EVT_SIZE, self.onSize, self)	
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
				
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
		
	def add_action(self, action):
		action_type, action_opts = action
		if action_type == 'jump':
			fleet = action_opts
			self.sizer.Add( wx.StaticText(self, label='Jump %s[%s] to %d:%d from %d:%d'%(fleet['name'], store.user_name(fleet['user_id']), fleet['x'], fleet['y'], fleet['from_x'], fleet['from_x'])))
		self.actions[(action_type, fleet['fleet_id'])] = fleet
		
