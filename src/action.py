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

def tag(name, value):
	return '<%s>%s</%s>'%(name, value, name)

class Action:
	ACTION_GEO_EXPLORE = 1
	def __init__(self, action_type, user_id):
		self.user_id = user_id
		self.action_type = action_type
		self.act_id = None
		
	def perform(self):
		pass
		
	def revert(self):
		pass
		
	def create_xml_action(self, act_id):
		self.act_id = act_id
		
	def format_action(self, act_id, name, data):
		return '<act id="%s" name="%s">%s</act>'%(act_id, name, ''.join(data))

class ActionJump(Action):
	NAME = 'jump'
	def __init__(self, user_id, fleet_id, coord):
		Action.__init__(self, self.NAME, user_id)
		self.coord = coord
		self.fleet_id = fleet_id
		
	def perform(self):
		store.command_fleet_jump(self.fleet_id, self.coord)
		
	def revert(self):
		store.command_fleet_cancel_jump(self.fleet_id)

	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'move_fleet', [tag('move_to', '%d:%d'%self.coord), tag('fleet_id', self.fleet_id)])

class ActionUnitMove(Action):
	NAME = 'unit_move'
	def __init__(self, user_id, fleet_id, unit_id):
		Action.__init__(self, self.NAME, user_id)
		self.unit_id = unit_id
		self.fleet_id = fleet_id
		
		self.fleet_unit = store.get_object('fleet_unit', {'unit_id':unit_id})
		self.garrison_unit = store.get_object('garrison_unit', {'unit_id':unit_id})
		
	def perform(self):
		store.command_move_unit_to_fleet(self.unit_id, self.fleet_id)
		
	def revert(self):
		if self.fleet_unit:
			store.command_move_unit_to_fleet(self.unit_id, self.fleet_unit['fleet_id'])
		elif self.garrison_unit:
			store.command_move_unit_to_garrison(self.unit_id, (self.garrison_unit['x'],self.garrison_unit['y']) )

	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'move_unit_to_fleet', [tag('fleet_id', self.fleet_id), tag('unit_id', self.unit_id)])
		
class ActionGeoExplore(Action):
	NAME = 'explore'
	def __init__(self, user_id, unit_id, coord):
		Action.__init__(self, self.NAME, user_id)
		self.unit_id = unit_id
		self.coord = coord

	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'store_action', [tag('unit_id', self.unit_id), tag('action_id', self.ACTION_GEO_EXPLORE), tag('planetid', '%d:%d'%self.coord)])
		
class ActionCreateFleet(Action):
	NAME = 'fleet_create'
	def __init__(self, user_id, name, coord):
		Action.__init__(self, self.NAME, user_id)
		self.fleet_id = None
		self.coord = coord
		self.name = name
		
	def perform(self):
		self.fleet_id = store.command_create_fleet(self.user_id, self.coord, self.name)
		print 'created fleet %d from %s %s %s'%(self.fleet_id, self.user_id, self.coord, self.name)
		
	def revert(self):
		store.remove_object('fleet', {'fleet_id':self.fleet_id})
		#Do we need to remove all flying_fleets with this id as well?? and units which belong to them??
		# Anyway thir actions will not be performed as fleet-id will remain negative
		
	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'create_new_fleet', [tag('new_fleet_name', self.name), tag('planetid', '%d:%d'%self.coord)])

class ActionPanel(scrolled.ScrolledPanel):
	def __init__(self, parent):
		scrolled.ScrolledPanel.__init__(self, parent)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.button_perform = wx.Button(self, label='Perform')
		self.button_perform.Enable(False)
		sz.Add(self.button_perform)
		
		self.button_cancel = wx.Button(self, label='Cancel')
		self.button_cancel.Enable(False)
		sz.Add(self.button_cancel)
		self.sizer.Add(sz)
		
		self.actions = []
				
		self.SetSizer(self.sizer)
		self.sizer.Layout()
	
		self.Bind(wx.EVT_SIZE, self.onSize, self)	
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
		
		self.Bind(wx.EVT_BUTTON, self.on_perform_actions, self.button_perform)
		self.Bind(wx.EVT_BUTTON, self.on_cancel_actions, self.button_cancel)
		
	def on_perform_actions(self, evt):
		acts = []
		for act_id, act in enumerate(self.actions):
			acts.append(act.create_xml_action(act_id))
			
		print acts
		
	def on_cancel_actions(self, evt):
		for act in self.actions:
			act.revert()
			act.label.Destroy()
		self.actions = []
		self.button_perform.Enable(False)
		self.button_cancel.Enable(False)
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
		
	def add_action(self, action):
		
		self.actions.append(action)
		user_name = store.get_user_name(action.user_id)
		label = ''
		if ActionJump.NAME == action.action_type:
			fleet = store.get_object('fleet', {'fleet_id':action.fleet_id})
			fromx,fromy = fleet['x'],fleet['y']
			fleet_name = fleet['name']
			x,y = action.coord
			label = 'Fleet: "%s" [%s] %d:%d => %d:%d'%(fleet_name, user_name,  fromx, fromy, x, y)
		elif ActionGeoExplore.NAME == action.action_type:
			label = 'geo explore [%s] %d:%d'%(user_name, action.coord[0], action.coord[1])
		elif ActionUnitMove.NAME == action.action_type:
			unit_name = store.get_unit_name(action.unit_id)
			fleet_name = store.get_fleet_name(action.fleet_id)
			fleet = store.get_object('fleet', {'fleet_id':action.fleet_id})
			if not fleet:
				print 'oops, fleet %d not found in db, unit move failed'%(action.fleet_id,)
				return
			label = 'Unit %s move to fleet %s[%s] at %d:%d'%(unit_name, fleet_name, user_name, fleet['x'], fleet['y'])
		elif ActionCreateFleet.NAME == action.action_type:
			label='Create fleet %s[%s] %d:%d'%(action.name, user_name, action.coord[0], action.coord[1])
		else:
			print 'action unknown %s'%(action.action_type,)
			return

		action.perform()
		txt = wx.StaticText(self, label=label)
		txt.action = action
		action.label = txt			
		self.sizer.Add( txt )
		self.sizer.Layout()
			
		self.button_perform.Enable(True)
		self.button_cancel.Enable(True)
		
	def perform_all(self):
		pass
