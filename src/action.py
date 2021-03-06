# -*- coding: utf-8 -*-
import wx
import wx.aui
import logging
import os
import os.path
import loader
import util
import event
import config
import save_load
import image
import import_xml
import unit_list
from store import store

import  wx.lib.scrolledpanel as scrolled

log = logging.getLogger('dclord')

def tag(name, value):
	return '<%s>%s</%s>'%(name, value, name)
	
def get_colony_population(action):
	if action == Action.ARC_COLONISE:
		return 30000
	elif action == Action.COLONY_COLONISE:
		return 5000
	elif action==Action.OUTPOST_COLONISE:
		return 10
	return 0
# EUNALVW geo scout  ( W already scouted, known )
# E -EMPTY
# Unknown, Neutral, Lord, Vassal, knoWn, Empty
#WUNALV - kill peopple ( not empty ) 
class Action:
	GEO_EXPLORE = 1
	KILL_PEOPLE = 101
	OFFER_VASSALAGE = 102
	ARC_COLONISE=6
	COLONY_COLONISE=2
	OUTPOST_COLONISE = 5
	def __init__(self, user_id):
		self.user_id = user_id
		self.act_id = None
		
	def perform(self):
		pass
		
	def revert(self):
		pass
		
	def create_xml_action(self, act_id):
		self.act_id = act_id
		
	def format_action(self, act_id, name, data):
		return '<act id="%s" name="%s">%s</act>'%(act_id, name, ''.join(data))
		
	def get_action_string(self):
		pass

class ActionJump(Action):
	def __init__(self, user_id, fleet_id, coord):
		Action.__init__(self, user_id)
		self.coord = coord
		self.fleet_id = fleet_id
		
	def perform(self):
		log.debug('local perform action Jump [user %s, fleet %s, coord: %s]'%(self.user_id, self.fleet_id, self.coord))
		store.command_fleet_jump(self.fleet_id, self.coord)
		
	def revert(self):
		log.debug('local revert action Jump [user %s, fleet %s, coord: %s]'%(self.user_id, self.fleet_id, self.coord))
		store.command_fleet_cancel_jump(self.fleet_id)

	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'move_fleet', [tag('move_to', '%d:%d'%self.coord), tag('fleet_id', self.fleet_id)])

	def get_action_string(self):
		fleet = store.get_object('fleet', {'fleet_id':self.fleet_id})
		if not fleet:
			log.error('Jump failed - fleet not found in db [user %s, fleet %s, coord: %s]'%(self.user_id, self.fleet_id, self.coord))
			return 'Jump failed - fleet not found in db [user %s, fleet %s, coord: %s]'%(self.user_id, self.fleet_id, self.coord)
		fromx,fromy = fleet['x'],fleet['y']
		fleet_name = fleet['name']
		x,y = self.coord
		return 'Fleet: "%s" [%s] %d:%d => %d:%d'%(fleet_name, store.get_user_name(self.user_id),  fromx, fromy, x, y)

class ActionUnitMove(Action):
	def __init__(self, user_id, fleet_id, unit_id):
		Action.__init__(self, user_id)
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
		
	def get_action_string(self):
		unit_name = store.get_unit_name(self.unit_id)
		fleet_name = store.get_fleet_name(self.fleet_id)
		fleet = store.get_object('fleet', {'fleet_id':self.fleet_id})
		if not fleet:
			log.error('Unit move failed - fleet not found in db [user %s, fleet %s, unit: %s]'%(self.user_id, self.fleet_id, self.unit_id))
			return 'Fleet %s not found in db'%(self.fleet_id,)
		return 'Unit %s move to fleet %s[%s] at %d:%d'%(unit_name, fleet_name, store.get_user_name(self.user_id), fleet['x'], fleet['y'])

class ActionStore(Action):
	def __init__(self, user_id, unit_id, fleet_id, coord, action_type_id):
		Action.__init__(self, user_id)
		self.unit_id = unit_id
		self.coord = coord
		self.action_type_id = action_type_id
		self.fleet_id = fleet_id

	def perform(self):
		store.add_data('action', {'action_type':self.action_type_id, 'x':self.coord[0], 'y':self.coord[1], 'fleet_id':self.fleet_id, 'unit_id':self.unit_id, 'user_id':self.user_id})
		
	def revert(self):
		store.remove_object('action', {'unit_id':self.unit_id})
			
	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'store_action', [tag('unit_id', self.unit_id), tag('action_id', self.action_type_id), tag('planetid', '%d:%d'%self.coord)])
	
	def get_action_string(self):
		return 'action %s [%s] %d:%d'%(self.action_type_id, store.get_user_name(self.user_id), self.coord[0], self.coord[1])
	
class ActionCancel(Action):
	def __init__(self, user_id, action_id):
		Action.__init__(self, user_id)
		self.action_id = action_id
		self.action = store.get_object('action', {'cancel_id':self.action_id})

	def perform(self):
		store.remove_object('action', {'cancel_id':self.action_id})

	def revert(self):
		store.add_data('action', self.action)
			
	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'cancel_action', [tag('action_id', self.action_id)])
	
	def get_action_string(self):
		return 'cancel action %s [%s]'%(self.action_id, store.get_user_name(self.user_id))
		
class ActionCreateFleet(Action):
	NAME = 'fleet_create'
	def __init__(self, user_id, name, coord):
		Action.__init__(self, user_id)
		self.fleet_id = None
		self.coord = coord
		self.name = name
		
	def perform(self):
		self.fleet_id = store.command_create_fleet(self.user_id, self.coord, self.name)
		#print 'created fleet %d from %s %s %s'%(self.fleet_id, self.user_id, self.coord, self.name)
		
	def revert(self):
		store.remove_object('fleet', {'fleet_id':self.fleet_id})
		# maybe it already left the planet
		store.remove_object('flying_fleet', {'fleet_id':self.fleet_id})
		
	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'create_new_fleet', [tag('new_fleet_name', self.name), tag('planetid', '%d:%d'%self.coord)])
		
	def commit_result(self, success, new_id):
		if not success:
			return
			
		store.update_object('fleet', {'fleet_id':self.fleet_id}, {'fleet_id':new_id})
		store.update_object('flying_fleet', {'fleet_id':self.fleet_id}, {'fleet_id':new_id})
		store.update_object('fleet_unit', {'fleet_id':self.fleet_id}, {'fleet_id':new_id})
		self.fleet_id = new_id
		
	def get_action_string(self):
		return 'Create fleet %s[%s] %d:%d'%(self.name, store.get_user_name(self.user_id), self.coord[0], self.coord[1])
		
		unit_name = store.get_unit_name(self.unit_id)
		fleet_name = store.get_fleet_name(self.fleet_id)
		fleet = store.get_object('fleet', {'fleet_id':self.fleet_id})
		if not fleet:
			#print 'oops, fleet %d not found in db, unit move failed'%(action.fleet_id,)
			return 'bad action'
		return 'Unit %s move to fleet %s[%s] at %d:%d'%(unit_name, fleet_name, store.get_user_name(self.user_id), fleet['x'], fleet['y'])

class ActionCancelBuild(Action):
	NAME = "drop_building_from_que"
	
	def __init__(self, user_id, unit_id):
		Action.__init__(self, user_id)
		self.unit_id = unit_id
		self.queue_unit = store.get_object('garrison_queue_unit', {'unit_id':self.unit_id})
		
	def perform(self):
		store.remove_object('garrison_queue_unit', {'unit_id':self.unit_id})
		
	def revert(self):
		store.add_data('garrison_queue_unit', self.queue_unit)
		
	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'drop_building_from_que', [tag('building_id', self.unit_id)])
	
	def get_action_string(self):
		return 'Cancel build %s %s'%(self.unit_id, store.get_user_name(self.user_id))

class ActionBuild(Action):
	NAME = "add_building_to_que"
	
	def __init__(self, user_id, coord, proto_id):
		Action.__init__(self, user_id)
		self.coord = coord
		self.proto_id = proto_id
		self.fleet_id = None #it's actually building_id
		
	def perform(self):
		self.fleet_id = store.command_build(self.coord, self.proto_id)
		
	def revert(self):
		store.remove_object('garrison_queue_unit', {'unit_id':self.fleet_id})
		self.fleet_id = None
		
	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'add_building_to_que', [tag('building_id', self.proto_id), tag('planet_id', '%d:%d'%self.coord)])
		
	def commit_result(self, success, new_id):
		if not success:
			return
			
		store.update_object('garrison_queue_unit', {'unit_id':self.fleet_id}, {'unit_id':new_id})
		self.fleet_id = new_id
		
	def get_action_string(self):
		return 'Build %s %s on %s'%(self.proto_id, store.get_user_name(self.user_id), self.coord)

		
class ActionDestroy(Action):
	NAME = "demolish_building"
	
	def __init__(self, user_id, unit_id):
		Action.__init__(self, user_id)
		self.unit_id = unit_id
		self.unit = store.get_object('unit', {'unit_id':self.unit_id})
		self.garrison_unit = store.get_object('garrison_unit', {'unit_id':self.unit_id})
		
	def perform(self):
		store.command_destroy(self.unit_id)
		
	def revert(self):
		store.add_data('unit', self.unit)
		store.add_data('garrison_unit', self.garrison_unit)
		
	def create_xml_action(self, act_id):
		Action.create_xml_action(self, act_id)
		return self.format_action(act_id, 'garrison_queue_unit', [tag('building_id', self.proto_id), tag('planet_id', '%d:%d'%self.coord)])
		
	def commit_result(self, success, new_id):
		if not success:
			return
			
		store.update_object('garrison_queue_unit', {'unit_id':self.fleet_id}, {'unit_id':new_id})
		self.fleet_id = new_id

	def get_action_string(self):
		return 'Destroy %s %s'%(self.unit_id, store.get_user_name(self.user_id))
		
'''
cancel_cargo_load
change_fleet_name

cancel_jump
accept_nationality_offer

share_fleet_access
customise_container
hidefleet

cancel_dip_relation
create_new_unit_design

create_prototype_design_unit

change_planet_name

change_behaviour

save_interface_settings

store_planet_mark

building_to_top

change_dip_relation

pack_parts

cancel_action

change_planet_perms

unpack_container

renameacc

clear_queue
			<act name="drop_building_from_que" id="1">

<building_id>16982207</building_id>

</act>

<act name="demolish_building" id="1">

<building_id>8230919</building_id>

</act>
create_single_design_unit

save_player_settings

add_building_to_que

drop_prototype

customise_container

store_user_vote

save_diplomacy_settings

save_ankete

all_ext_planet_perms

create_new_unit_design

store_planet_fake_stats

hidefleet

cancel_dip_relation

recall_fleet_permission

new_script_weight

drop_building_from_que

gimmeelephant

move_fleet

unshare_me

subscribe_me_to

create_prototype_design_unit

kill_player

move_unit_to_fleet

store_action

change_planet_name

change_behaviour

save_interface_settings

store_planet_mark

building_to_top

activate_free_subscription

change_dip_relation

showpost

set_bid

cancel_percent_change

create_channel

pack_parts

archive_design

enable_fleet_script

drop_design

subscribe_player

drop_fleet_script

remove_ext_permission

add_to_digest

store_messages_cleanup_setup

add_player_to_dip_by_name

rename_channel

create_fleet_from_choosen

alter_channel_permissions

cancel_action

change_planet_perms

unpack_container

renameacc

clear_queue'''

			
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
		
		self.stored_actions = {} #user->[actions]
		self.delayed_actions = {} #user->[actions] -1 fleet-id
		self.pending_actions = {} #user->{act-id: action}
		
		self.actions_sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.actions_sizer)
				
		self.SetSizer(self.sizer)
		self.sizer.Layout()
	
		self.Bind(wx.EVT_SIZE, self.onSize, self)	
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
		
		self.Bind(wx.EVT_BUTTON, self.on_perform_actions, self.button_perform)
		self.Bind(wx.EVT_BUTTON, self.on_cancel_actions, self.button_cancel)
		self.Bind(event.EVT_DATA_DOWNLOAD, self.on_data_downloaded)
	
	def update_fleet_id(self, user_id, fleet_id, new_id):
		if not user_id in self.delayed_actions:
			return
		for act in self.delayed_actions[user_id]:
			if act.fleet_id == fleet_id:
				act.fleet_id = new_id
				self.stored_actions.setdefault(user_id, []).append( act )
	
	#replyes = {1:(True, 2), 2:(False,0), 3:(True, 99)}
	def on_reply_received(self, user_id, actions_reply):
		user_id = int(user_id)
		acts = self.pending_actions[user_id]
		del self.pending_actions[user_id]
		
		update_actions_required = False
		for act_id, act in acts.items():
			if not act_id in actions_reply:
				log.error('no reply for action %d'%(act_id,))
				continue
			is_ok, ret_id = actions_reply[act_id]
			if not is_ok:
				log.debug('action %d failed, reverting local change'%(act_id,))
				# revert action in the local-db ( and on the map )
				act.revert()
			elif is_ok and (isinstance(act, ActionCreateFleet) or isinstance(act, ActionBuild)):
				self.update_fleet_id(user_id, act.fleet_id, ret_id)
			elif is_ok and isinstance(act, ActionStore):
				update_actions_required = True
		
		if user_id in self.delayed_actions:
			del self.delayed_actions[user_id]
			
		if update_actions_required:
			self.GetParent().update_user(user_id)
			
	
	def on_perform_actions(self, evt):
		self.do_perform()
		
	def do_perform(self):
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		log.debug('preparing directory %s to load action result'%(out_dir,))

		l = loader.AsyncLoader()
		at_leat_one = False
		for user_id, acts in self.stored_actions.items():
			if len(acts) == 0:
				continue
			user = store.get_user(user_id)
			if 'login' in user and user['login']:
				log.debug('Storing actions for user %s'%(user_id,))
				l.sendActions(self, config.get_user_login(user['user_id']), self.prepare_actions_request(user_id), out_dir)
				at_leat_one = True
		
		# clear action list
		self.remove_action_items()
		self.stored_actions = {}
		
		if at_leat_one:
			l.start()
		
	def on_data_downloaded(self, evt):
		key = evt.attr1
		data = evt.attr2
		if not key:
			#all data downloaded
			if len(self.stored_actions) > 0:
				self.do_perform()
			else:
				# time to save all performed changes locally
				save_load.save_local_data()
				wx.PostEvent(self.GetParent(), event.MapUpdate())
			return
			
		if not data:
			#print 'failed to load info for user %s'%(key,)
			return
		
		user_info = import_xml.processRawData(data)
		if not user_info:
			log.error('Wrong data for login %s'%(key,))
			return

		user_id = user_info['user_id']
		if 'results' in user_info:
			actions_result = user_info['results']
			self.on_reply_received(user_id, actions_result)
		
	def prepare_actions_request(self, user_id):
		act_id = 0
		s = []
		
		# anyway need to clear it
		self.pending_actions[user_id] = {}
		for act in self.stored_actions[user_id]:
			# put all actions involing not yet created fleets ( except fleet-create ) into another dict, it will be processed later, when we have real fleet-id
			if (not isinstance(act, ActionCreateFleet) and not isinstance(act, ActionBuild )) and hasattr(act, 'fleet_id') and act.fleet_id < 0:
				self.delayed_actions.setdefault(user_id, []).append(act)
				continue
			act_id+=1
			s.append(act.create_xml_action(act_id))
			self.pending_actions[user_id][act_id] = act
		st = tag('x-dc-perform', ''.join(s))
		log.debug('User %s actions: %s'%(user_id, st))
		return st
				
	def on_cancel_actions(self, evt):
		self.remove_action_items(revert_actions = True)
		self.stored_actions = {}
		
	def remove_action_items(self, revert_actions = False):
		for acts in self.stored_actions.values():
			for act in acts:
				if revert_actions:
					act.revert()
		self.actions_sizer.Clear(delete_windows=True)
		self.button_perform.Enable(False)
		self.button_cancel.Enable(False)
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
		
	def add_action(self, action):
		
		self.stored_actions.setdefault(action.user_id,[]).append(action)

		# first get string, then perform ( moves fleets ect )
		txt = wx.StaticText(self, label=action.get_action_string())
		action.perform()

		txt.action = action
		action.label = txt			
		self.actions_sizer.Add( txt )
		self.sizer.Layout()
			
		self.button_perform.Enable(True)
		self.button_cancel.Enable(True)
