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

class Action:
	def __init__(self, name, user_id, opts):
		self.user_id = user_id
		self.name = name
		self.opts = opts

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
		if action.name == 'jump':
			fleet_id = action.opts['fleet_id']
			fleet = store.get_object('fleet', {'fleet_id':fleet_id})
			coord = action.opts['planet']
			self.sizer.Add( wx.StaticText(self, label='Jump %s[%s] to %d:%d from %d:%d'%(store.get_user_name(action.user_id), fleet['name'], coord[0], coord[1], fleet['x'], fleet['y'])))
			self.actions[(action.name, fleet_id)] = action
		elif action.name = 'exlopre':
			coord = action.opts['planet']
			self.sizer.Add( wx.StaticText(self, label='Geo explore %s %d:%d'%(store.get_user_name(action.user_id), coord[0], coord[1])))
			self.actions[(action.name, action.opts['unit_id'])] = action
		
		self.sizer.Layout()
		
	def perform_all(self):
		
