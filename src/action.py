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
		print 'adding action %s %s %s'%(action.user_id, action.name, action.opts)
		ret_id = 0
		user_id = action.user_id
		if action.name == 'jump':
			fleet_id = action.opts['fleet_id']
			fleet = store.get_object('fleet', {'fleet_id':fleet_id})
			coord = action.opts['planet']
			store.command_jump_fleet(fleet_id, coord)
			self.sizer.Add( wx.StaticText(self, label='Jump %s[%s] to %d:%d from %d:%d'%(store.get_user_name(user_id), fleet['name'], coord[0], coord[1], fleet['x'], fleet['y'])))
			self.actions[(action.name, fleet_id)] = action
		elif action.name == 'exlopre':
			coord = action.opts['planet']
			self.sizer.Add( wx.StaticText(self, label='Geo explore %s %d:%d'%(store.get_user_name(user_id), coord[0], coord[1])))
			self.actions[(action.name, action.opts['unit_id'])] = action
		elif 'unit_move' == action.name:
			if 'fleet_id' in action.opts:
				fleet_id = action.opts['fleet_id']
				unit_id = action.opts['unit_id']
				store.command_move_unit_to_fleet(unit_id, fleet_id)
				
				unit_name = store.get_unit_name(unit_id)
				fleet_name = store.get_fleet_name(fleet_id)
				user_name = store.get_user_name(user_id)
				x,y = action.opts['planet']
				self.sizer.Add( wx.StaticText(self, label='Unit %s move to fleet %s[%s] at %d:%d'%(unit_name, fleet_name, user_name, x, y)))
				
		elif 'create_fleet' == action.name:
			coord = action.opts['planet']
			ret_id = store.command_create_fleet(action.user_id, coord, action.opts['name'])
			action.opts['fleet_id'] = ret_id
			self.sizer.Add( wx.StaticText(self, label='Create fleet %s %s %d:%d'%(action.opts['name'], store.get_user_name(action.user_id), coord[0], coord[1])))
			self.actions[(action.name, ret_id)] = action
			
			
		
		self.sizer.Layout()
		return ret_id
		
	def perform_all(self):
		pass
