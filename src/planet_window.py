import wx.aui
import logging
import db
import util
import event
import config
import image
import unit_list
import action
from store import store

import  wx.lib.scrolledpanel as scrolled

log = logging.getLogger('dclord')

def get_unit_name(carapace):
    return {
        1: 'shuttle',
        2: 'comm shuttle',
        6: 'shuttle',
        7: 'colony',
        11: 'probe',
        13: 'governer',
        21: 'transport',
        40: 'ark'
        }.get(carapace, '')

class FleetPanel(scrolled.ScrolledPanel):
	def __init__(self, parent):
		scrolled.ScrolledPanel.__init__(self, parent)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.fleets = {}
		self.coord = None
				
		self.SetSizer(self.sizer)
		self.sizer.Layout()
	
		self.Bind(wx.EVT_SIZE, self.onSize, self)	
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
				
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
			
	def set_fleets(self, evt):
		self.sizer.DeleteWindows()
		self.fleets = {}
		
		self.coord = evt.attr1
		x,y = evt.attr1
		for fleet in store.iter_objects_list('fleet', {'x':x, 'y':y}):
			self.add_fleet(fleet)

		for fleet in store.iter_objects_list('flying_fleet', {'x':x, 'y':y}):
			self.add_fleet(fleet)

		for fleet in store.iter_objects_list('alien_fleet', {'x':x, 'y':y}):
			self.add_alien_fleet(fleet)
			

	def add_alien_fleet(self, fleet):
		cp = wx.CollapsiblePane(self, label='%s'%fleet['name'], style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
		self.sizer.Add(cp)
		pane = cp.GetPane()
		
		u = store.get_user(fleet['user_id'])
		if u:
			owner_name = u['name']
		else:
			owner_name = '<unknown>'
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(pane, label='owner: %s'%(owner_name,)), 1, wx.EXPAND)		

		for unit in store.iter_objects_list('alien_unit', {'fleet_id':fleet['fleet_id']}):
			hbox = wx.BoxSizer(wx.HORIZONTAL)
			sizer.Add(hbox, 1, wx.EXPAND)
		
			img = image.getCarapaceImage(int(unit['carapace']), int(unit['color']) )
			
			if img:
				bitmap = wx.StaticBitmap(pane)
				bitmap.SetBitmap(img)
				hbox.Add(bitmap, 1, wx.EXPAND)
			else:
				print 'image not found for unit %s, carp %s, color %s'%(unit['unit_id'],  int(unit['carapace']), int(unit['color']) )

			name = get_unit_name(int(unit['carapace']))
			hbox.Add(wx.StaticText(pane, label=name), 1, wx.EXPAND)

		border = wx.BoxSizer()
		border.Add(sizer, 1, wx.EXPAND|wx.ALL)
		pane.SetSizer(border)
		
		self.sizer.Layout()
		
		self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)
		cp.Expand()
		
		cp.Bind(wx.EVT_LEFT_DOWN, self.onFleetSelect)
		self.fleets[cp] = fleet
		
	def add_fleet(self, fleet):
		nm = ''
		if 'arrival_turn' in fleet:
			nm = '[%d] '%(fleet['arrival_turn'] - store.max_turn(),)
		nm += fleet['name']
		cp = wx.CollapsiblePane(self, label=nm, style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
		self.sizer.Add(cp)
		pane = cp.GetPane()
		
		u = store.get_user(fleet['user_id'])
		if u:
			owner_name = u['name']
		else:
			owner_name = '<unknown>'
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(pane, label='owner: %s'%(owner_name,)), 1, wx.EXPAND)

		speed, rng = store.get_fleet_speed_range(fleet['fleet_id'])
		if speed and rng:
			sizer.Add(wx.StaticText(pane, label='%0.2f / %0.2f'%(speed, rng)), 1, wx.EXPAND)

		#can we contrl the fleet?
		is_controlled = 'login' in u and u['login'] in config.users and rng >= 1 and (not 'in_transit' in fleet or fleet['in_transit']==0)
		if is_controlled:
			jump_button = wx.ToggleButton(pane, label='jump')
			jump_button.fleet_id = fleet['fleet_id']
			sizer.Add(jump_button, 1, wx.EXPAND)
			
			self.Bind(wx.EVT_TOGGLEBUTTON, self.on_jump, jump_button)
		else:
			print 'user %s not controllable'%(u,)
		
		for unit in store.get_fleet_units(fleet['fleet_id']):
			hbox = wx.BoxSizer(wx.HORIZONTAL)
			sizer.Add(hbox, 1, wx.EXPAND)
			
			proto = store.get_object('proto', {'proto_id':unit['proto_id']})
			if not proto:
				print 'Prototype not found for %s'%(unit,)
				continue
			obj_carp = int(unit['proto_id']), int(proto['carapace']), int(proto['color'])
			
			if is_controlled:
				planet = store.get_object('planet', {'x':self.coord[0], 'y':self.coord[1]})
				inhabited = False
				if planet and planet['user_id'] and int(planet['user_id']) > 0:
					inhabited = True
					
				# get unit actions ( colony, kill-people )
				if not inhabited:
					for action_type in [action.Action.COLONY_COLONISE, action.Action.ARC_COLONISE, action.Action.OUTPOST_COLONISE]:
						action_colonize = store.get_object('proto_action', {'proto_id':proto['proto_id'], 'proto_action_id':action_type})
						if action_colonize:
							colonize_button = wx.Button(pane, label='Colonize %s'%(action.get_colony_population(action_type)))
							colonize_button.action =action_type, unit['unit_id'], fleet['fleet_id'], self.coord, u['user_id']
							self.Bind(wx.EVT_BUTTON, self.on_store_action, colonize_button)
							sizer.Add( colonize_button , 1, wx.EXPAND )

				if inhabited and planet['user_id'] != u['user_id']:
					#TODO: check if our mult, or ally, and notify user about it
					action_kill_people = store.get_object('proto_action', {'proto_id':proto['proto_id'], 'proto_action_id':action.Action.KILL_PEOPLE})
					if action_kill_people:
						colonize_button = wx.Button(pane, label='Kill people')
						colonize_button.action = action.Action.KILL_PEOPLE, unit['unit_id'], fleet['fleet_id'], self.coord, u['user_id']
						self.Bind(wx.EVT_BUTTON, self.on_store_action, colonize_button)
						sizer.Add( colonize_button , 1, wx.EXPAND )

			img = image.get_image( int(unit['proto_id']), int(proto['carapace']), int(proto['color']) )
			
			if img:
				bitmap = wx.StaticBitmap(pane)
				bitmap.SetBitmap(img)
				hbox.Add(bitmap, 1, wx.EXPAND)
			else:
				print 'image not found for unit %s, bc %s, carp %s, color %s'%(unit['unit_id'], int(unit['proto_id']), int(proto['carapace']), int(proto['color']) )

			name = proto['name']
			if not name:
				name = get_unit_name(int(proto['carapace']))
			hbox.Add(wx.StaticText(pane, label=name), 1, wx.EXPAND)

		border = wx.BoxSizer()
		border.Add(sizer, 1, wx.EXPAND|wx.ALL)
		pane.SetSizer(border)
		
		self.sizer.Layout()
		
		self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)
		cp.Expand()
		
		cp.Bind(wx.EVT_LEFT_DOWN, self.onFleetSelect)
		self.fleets[cp] = fleet
	
	def on_store_action(self, evt):
		obj = evt.GetEventObject()
		wx.PostEvent(self.GetParent(), event.StoreAction(attr1=obj.action))
		
	def on_jump(self, evt):
		self.GetParent().on_fleet_jump_prepare(evt.GetEventObject().fleet_id)
	
	def OnPaneChanged(self, evt=None):
		self.sizer.Layout()
	
	def onFleetSelect(self, evt):
		obj = evt.GetEventObject()
		fleet = self.fleets[obj]
		print fleet


class PlanetGeoWindow(wx.Window):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.text = wx.StaticText(self, wx.ID_ANY)
		sizer.Add(self.text)
		self.SetSizer(sizer)
		sizer.Layout()
	
	def set_planet(self, planet_info):
		self.text.SetText('%s'%(planet_info,))


class BuildingsWindows(wx.Frame):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		self.coord = None
		
	def set_coord(self, coord):
		
		self.coord = coord
		self.sizer.DeleteWindows()
		
		dsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(dsizer)
		
		dups = {}
		protos = {}
		# buildings	if ours
		for building in store.get_garrison_units(coord):
			bc = building['proto_id']
			p = store.get_object('proto', {'proto_id':bc})
			if not p:
				print 'proto not found for %s'%(building,)
				continue
				
			if int(p['is_building']) != 1:
				continue
				
			if 'max_count' in p and int(p['max_count'])!=1:
				dups.setdefault(bc, []).append(building)
				continue
				
			img = image.getBcImage(bc, 20)
			if not img:
				wnd = wx.StaticText(self, -1, 'Unknown building %s'%(bc,))
			else:
				wnd = wx.StaticBitmap(self, wx.ID_ANY)
				wnd.SetBitmap(img)
			dsizer.Add(wnd)

		for bc, builds in dups.iteritems():
			img = image.getBcImage(bc, 20)
			
			wsizer = wx.BoxSizer(wx.HORIZONTAL)
			self.sizer.Add(wsizer)
			
			wnd = wx.StaticBitmap(self, wx.ID_ANY)
			if img:
				wnd.SetBitmap(img)
			wsizer.Add(wnd)
			
			txt = wx.StaticText(self, -1, 'x %s'%(len(builds),))
			build_more = wx.Button(self, label="+", size=(20,20))
			build_more.proto_id = bc
			wsizer.Add(txt)
			wsizer.Add(build_more)
			
			build_more.Bind(wx.EVT_LEFT_DOWN, self.on_build)
		
		has_bq = None
		prev_units = []
		for unit in store.get_building_queue(coord):
			if not has_bq:
				self.sizer.Add(wx.StaticText(self, label='build queue:'))
				has_bq = True
				
			if unit['done'] > 0:
				self.draw_build_stack(prev_units)
				prev_units = []
				
				proto = store.get_object('proto', {'proto_id':unit['proto_id']})
				
				img = image.getBcImage(unit['proto_id'], 20)
				if not img:
					img = image.getCarapaceImage(proto['carapace'], proto['color'], 20)
				wsizer = wx.BoxSizer(wx.HORIZONTAL)
				self.sizer.Add(wsizer)
				
				wnd = wx.StaticBitmap(self, wx.ID_ANY)
				if img:
					wnd.SetBitmap(img)
				wsizer.Add(wnd)
				
				name = proto['name']
				if not name:
					name = get_unit_name(int(proto['carapace']))
				
				txt = wx.StaticText(self, -1, ' %d%% %s'%(unit['done']*100/proto['build_speed'],name))
				wsizer.Add(txt)
				if 'max_count' in proto and int(proto['max_count'])!=1:
					build_more = wx.Button(self, label="+", size=(20,20))
					build_more.proto_id = proto['proto_id']
					build_more.Bind(wx.EVT_LEFT_DOWN, self.on_build)
					wsizer.Add(build_more)
					
				continue
			
			
			if prev_units == [] or unit['proto_id'] == prev_units[0]['proto_id']:
				prev_units.append(unit)
				continue
			
			# draw prev_units
			self.draw_build_stack(prev_units)
			prev_units = [unit]
		self.draw_build_stack(prev_units)
			
		self.sizer.Layout()
	
	def on_build(self, evt):
		wnd = evt.GetEventObject()
		wx.PostEvent(self.GetParent(), event.BuildUnit(attr1=wnd.proto_id, attr2=self.coord))
		
	def on_cancel_build(self, evt):
		wx.PostEvent(self.GetParent(), event.CancelBuildUnits(attr1=evt.GetEventObject().units, attr2=self.coord))
		
	def draw_build_stack(self, units):
		if len(units) == 0:
			return
		wsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(wsizer)
		
		proto = store.get_object('proto', {'proto_id':units[0]['proto_id']})
		img = image.getBcImage(units[0]['proto_id'], 20)
		if not img:
			img = image.getCarapaceImage(proto['carapace'], proto['color'], 20)

		wnd = wx.StaticBitmap(self, wx.ID_ANY)
		if img:
			wnd.SetBitmap(img)
		wsizer.Add(wnd)
		
		name = proto['name']
		if not name:
			name = get_unit_name(int(proto['carapace']))
		
		count_text = ''
		if len(units)>1:
			count_text = 'x%s '%(len(units),)
		txt = wx.StaticText(self, -1, '%s%s'%(count_text, name))
		wsizer.Add(txt)
		
		if 'max_count' in proto:
			if int(proto['max_count'])!=1:
				build_more = wx.Button(self, label="+", size=(20,20))
				build_more.proto_id = proto['proto_id']
				build_more.Bind(wx.EVT_LEFT_DOWN, self.on_build)
				wsizer.Add(build_more)

			build_less = wx.Button(self, label="-", size=(20,20))
			build_less.units = units
			build_less.Bind(wx.EVT_LEFT_DOWN, self.on_cancel_build)
			wsizer.Add(build_less)


class PlanetPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.coord = None

		self.SetSizer(self.sizer)
		self.sizer.Layout()

	def select_coord(self, evt):
		coord = evt.attr1
		self.coord = coord
		self.update()

	def update(self):
		coord = self.coord
		
		self.sizer.DeleteWindows()
		
		self.sizer.Add( wx.StaticText(self, wx.ID_ANY, '%s:%s'%coord) )
		
		planet = store.get_object('planet', {'x':coord[0], 'y':coord[1]})
		owner = None
		name = None
		if not planet:
			self.sizer.Layout()
			return

		if 'o' in planet and planet['o']:
			self.sizer.Add( wx.StaticText(self, wx.ID_ANY, 'o: %s, e: %s, m: %s, t: %s, s: %s'%(planet['o'], planet['e'], planet['m'], planet['t'], planet['s'])) )
		else:
			pl_sz = store.get_object('planet_size', {'x':coord[0], 'y':coord[1]})
			if pl_sz:
				self.sizer.Add( wx.StaticText(self, wx.ID_ANY, 's: %s'%(pl_sz['s'],)) )
		
		if 'name' in planet and planet['name']:
			self.sizer.Add( wx.StaticText(self, wx.ID_ANY, planet['name']) )
		
		if 'user_id' not in planet:
			self.sizer.Layout()
			return
		owner_id = planet['user_id']
		if not owner_id:
			self.sizer.Layout()
			return
		u = store.get_user(owner_id)
		if u:
			owner_name = u['name']
			self.sizer.Add( wx.StaticText(self, wx.ID_ANY, owner_name) )
		
		buildings = BuildingsWindows(self)
		buildings.set_coord(coord)
		self.sizer.Add(buildings)
		self.sizer.Layout()
		
		self.Bind(event.EVT_BUILD_UNIT, self.on_build_unit)
		self.Bind(event.EVT_BUILD_CANCEL, self.on_build_cancel)
		
	def on_build_unit(self, evt):
		wx.PostEvent(self.GetParent(), evt)

	def on_build_cancel(self, evt):
		wx.PostEvent(self.GetParent(), evt)

		
class GarrisonPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.units_sizer = wx.BoxSizer(wx.VERTICAL)
		self.coord = None
		self.selected_units = {}
		
		self.button_fleet = wx.Button(self, label='to fleet')
		self.sizer.Add(self.button_fleet)
		self.button_fleet.Disable()
		self.SetSizer(self.sizer)
		self.sizer.Add(self.units_sizer)
		self.sizer.Layout()
		self.button_fleet.Bind(wx.EVT_BUTTON, self.on_fleet_create)
		
	def on_fleet_create(self, evt):
		main_frame = self.GetParent()

		user_planet = store.get_object('user_planet', {'x':self.coord[0], 'y':self.coord[1]})
		if not user_planet:
			return
			
		user_id = user_planet['user_id']

		# get fleet name
		
		# create new fleet
		create_fleet_action = action.ActionCreateFleet(user_id, 'Fleet', self.coord)
		main_frame.actions.add_action(create_fleet_action)

		# move units there
		for proto_id, units in self.selected_units.iteritems():
			for unit in units:
				main_frame.actions.add_action(action.ActionUnitMove(user_id, create_fleet_action.fleet_id, unit['unit_id']))
		
		wx.PostEvent(self.GetParent(), event.SelectObject(attr1=self.coord))
		
	def select_coord(self, evt):
		coord = evt.attr1
		self.set_coord(coord)
		
	def set_coord(self, coord):
		self.coord = coord
		
		self.button_fleet.Disable()
		
		self.selected_units = {}
		self.units_sizer.DeleteWindows()
		
		user_planet = store.get_object('user_planet', {'x':coord[0], 'y':coord[1]})
		if not user_planet:
			self.sizer.Layout()
			return
		
		item_windows = {}
		
		dups = {}
		protos = {}

		items = {}
		
		gu = store.get_garrison_units(coord)
		for unit in gu:
			bc = unit['proto_id']
			if bc in items:
				items[bc].append(unit)
				continue
				
			p = store.get_object('proto', {'proto_id':bc})
			if int(p['is_building']) == 1:
				continue
			items[bc] = [unit]
			protos[bc] = p
			
		
		for bc, item_list in items.iteritems():
			p = protos[bc]
			wnd = wx.Window(self, style=wx.SUNKEN_BORDER)
			wnd.proto_id = bc
			wnd.units = item_list
			sz = wx.BoxSizer(wx.HORIZONTAL)
			wnd.SetSizer(sz)
			self.units_sizer.Add(wnd)
			if 'carapace' in p and p['carapace']:
				img = image.getCarapaceImage(int(p['carapace']), int(p['color']))
			else:
				img = image.getBcImage(bc)
			bmp = wx.StaticBitmap(wnd)
			if img:
				bmp.SetBitmap(img)
			sz.Add(bmp)
			n_str = ''
			if len(item_list) > 1:
				n_str = ' x%s'%(len(item_list),)
			name = get_unit_name(bc)
			if not name:
				name = p['name']
			fly=''
			transport = ''
			if int(p['is_spaceship'])==1:
				fly = '%.2f/%.2f'%(p['fly_speed'], p['fly_range'])
				tc = int(p['transport_capacity'])
				if tc > 0:
					transport = '[%s]'%(tc,)
			text = wx.StaticText(wnd, -1, '%s%s%s %s'%(fly, transport, n_str, name,))
			sz.Add(text)
			sz.Layout()
			
			wnd.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
			bmp.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
			text.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)

		self.sizer.Layout()
		
	def onLeftDown(self, evt):
		wnd = evt.GetEventObject()
		if 'wxStaticText' == wnd.GetClassName() or 'wxStaticBitmap' == wnd.GetClassName():
			wnd = wnd.GetParent()
		
		if wnd.proto_id in self.selected_units:
			wnd.SetBackgroundColour(wx.NullColor)
			del self.selected_units[wnd.proto_id]
		else:
			self.selected_units[wnd.proto_id] = wnd.units
			selected_unit_color = '#008800'
			wnd.SetBackgroundColour(selected_unit_color)
		
		if len(self.selected_units)>0:
			self.button_fleet.Enable()
		else:
			self.button_fleet.Disable()
	
class InfoPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))			
		self.sizer = wx.BoxSizer(wx.VERTICAL)	
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		self.pos = (0,0)
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		self.turn = db.getTurn()

	def selectObject(self, evt):
		self.pos = evt.attr1
		log.info('object select %s, updating'%(self.pos,))
		self.update()

	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
			
	def update(self, turn = None):
		if turn:
			self.turn = turn
		log.info('updating info panel, pos %s turn %d'%(self.pos, self.turn))
		self.sizer.DeleteWindows()
		#self.sizer.Add( PlanetWindow(self, self.pos, self.turn, True) )
		#self.sizer.Add( FleetWindow(self, self.pos, self.turn), 1, flag=wx.EXPAND | wx.ALL)
		self.sizer.Layout()
