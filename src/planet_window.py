import wx.aui
import logging
import db
import util
import event
import config
import image
import unit_list

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

class StackedObject(wx.Window):
	def __init__(self, parent, unit):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.units = []
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.text = wx.StaticText(self, wx.ID_ANY, 'x%d'%(len(self.units),))
		sz.Add( self.text )
		sz.Add( unit_list.UnitPrototypeWindow(self, unit) )
		
		self.sizer.Add(sz)
		self.SetSizer(self.sizer)
		self.sizer.Layout()

		self.add(unit)
	
	def add(self, unit):
		self.units.append(unit)
		self.update()
		
	def update(self):
		self.text.SetLabel('x%d'%(len(self.units),))
		self.sizer.Layout()
	
class PlanetWindow(scrolled.ScrolledPanel):
	def __init__(self, parent, coord = None, turn = None, show_units = False):
		scrolled.ScrolledPanel.__init__(self, parent, wx.ID_ANY, size=(200,300))
		
		self.turn = turn if turn else db.getTurn()
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)

		self.coord = coord
		
		if not self.coord:
			self.sizer.Layout()
			return
		
		owner_id = 0
		planet_name = ''
		for planet in db.planets(self.turn, ['x=%d'%(coord[0],), 'y=%d'%(coord[1],)], ('x','y','owner_id','o','e','m','t','s', 'name')):
			planet_name = planet.get('name', '')
			owner = planet['owner_id']
			if not owner:
				break
			owner_id = int(owner)
			
		
		owner_name = 'unknown'
		if owner_id > 0:
			for res in db.players(['player_id=%s'%(owner_id,)]):
				owner_name = res['name']
		else:
			owner_name = '<empty>'
		
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, '%s:%s %s'%(coord[0],coord[1], planet_name)))
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, owner_name))
		
		if show_units:
			self.addUnits()
		#self.sizer.Layout()
		
		#self.SetSizer( self.vbox )
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
				
		self.Bind(wx.EVT_SIZE, self.onSize, self)
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()

		
	def addUnits(self):
		gunits = {}
		coord = self.coord
		for gu in db.garrison_units(self.turn, ['x=%d'%(coord[0],), 'y=%d'%(coord[1],)]):
			
			cl = int(gu['class'])
			if cl in gunits:
				gunits[cl].add(gu)
			else:
				uwindow = StackedObject(self, gu)
				gunits[cl] = uwindow
				self.sizer.Add( uwindow )
		
		

class UnitStackWindow(wx.Window):
	def __init__(self, parent, owner_id, unit):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add( unit_list.UnitPrototypeWindow(self, unit) )
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		
		self.units = {}
		self.user_name = db.getUserName(owner_id)

		self.text = wx.StaticText(self, wx.ID_ANY, '%d units, [%s]'%(len(self.units), self.user_name))
		self.sizer.Add(self.text)
		self.sizer.Layout()
		
		self.add(unit)
	
	def add(self, unit):
		self.units[unit['id']] = unit
		self.update()
		
	def update(self):
		self.text.SetLabel('%d units, [%s]'%(len(self.units), self.user_name))

class FleetWindow(scrolled.ScrolledPanel):
	def __init__(self, parent, coord = None, turn = None):
		scrolled.ScrolledPanel.__init__(self, parent, -1, size=(200,200))
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		
		self.tree = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_HAS_BUTTONS)
		#self.alien_fleets = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_HAS_BUTTONS)
		
		self.vbox.Add(self.tree, 1, wx.EXPAND)
		#self.vbox.Add(self.alien_fleets, 1, wx.EXPAND)

		self.setUnits(coord, turn)
		#self.setAlienUnits(coord, turn)
		
		self.SetSizer( self.vbox )
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
				
		self.Bind(wx.EVT_SIZE, self.onSize, self)
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
	
	def setUnits(self, coord, turn):
		units = {}
		if not coord:
			return
		
		self.tree.DeleteAllItems()
		image_list = wx.ImageList(40, 40)
		self.tree.AssignImageList(image_list)
		img_list_data = {}
		root = self.tree.AddRoot('Fleets')
		for user in db.users():
			user_id = user['id']
			tree_user = None
			for fleet in db.fleets(turn, util.filter_coord(coord) + ['owner_id=%s'%(user_id,)]):
				if not tree_user:
					tree_user = self.tree.AppendItem(root, user['name'])
				tree_fleet = self.tree.AppendItem(tree_user, fleet['name'])
				for unit in db.units(turn, ['fleet_id=%s'%(fleet['id'],)]):					
					proto = db.get_prototype(unit['class'], ('carapace', 'color', 'name'))
					obj_carp = int(unit['class']), int(proto['carapace']), int(proto['color'])
					img_item = None
					if obj_carp in img_list_data:
						img_item = img_list_data[obj_carp]
					else:
						img_item = image.add_image(image_list, obj_carp)
						img_list_data[obj_carp] = img_item
					name = proto['name']
					if not name:
						name = get_unit_name(int(proto['carapace']))
					if img_item:
						self.tree.AppendItem(tree_fleet, name, image=img_item)
					else:
						self.tree.AppendItem(tree_fleet, name)
					
		for user in db.alien_players():
			user_id = int(user['player_id'])
			tree_user = None
			for fleet in db.fleets(turn, util.filter_coord(coord) + ['owner_id=%s'%(user_id,)]):
				if not tree_user:
					tree_user = self.tree.AppendItem(root, user['name'])
				tree_fleet = self.tree.AppendItem(tree_user, fleet['name'])

				for unit in db.alienUnits(turn, ['fleet_id=%s'%(fleet['id'],)]):
					#print 'get alient unit %s'%(unit,)
					obj_carp = unit['class'], int(unit['carapace']), int(unit['color'])
					img_item = None
					if obj_carp in img_list_data:
						img_item = img_list_data[obj_carp]
					else:
						img_item = image.add_image(image_list, obj_carp)
						img_list_data[obj_carp] = img_item

					if img_item:
						self.tree.AppendItem(tree_fleet, get_unit_name(int(unit['carapace'])), image=img_item)
					else:
						self.tree.AppendItem(tree_fleet, get_unit_name(int(unit['carapace'])))
				
					
		self.tree.ExpandAll()
			
		
		#log.info('requesting fleet info at %s'%(coord,))
		#for fleet,unit in db.all_ownedUnits(turn, coord):
		#	cl = int(fleet['owner_id']), int(unit['class'])
		#	if cl in units:
		#		units[cl].add(unit)
		#	else:
		#		uwindow = UnitStackWindow(self, cl[0], unit)
		#		self.vbox.Add( uwindow)
		#		units[cl] = uwindow
		#for u in units.values():
		#	u.update()
	
	def setAlienUnits(self, coord, turn):
		units = {}
		if not coord:
			return
			
	
		#type of alien unit: (carapase, weight)
		#TODO: develop kind of alien Ship Unit Type, and evristicly fit ships into some of them
		# based on real unit id it's speed, transport capacity, invisibility ability and war attributes can be determined
		# it's name can be read when unit destroyed
		
		#  some values could be entered manually
		keys = {}
		for fleet,unit in db.all_alienUnits(turn, coord):
			key = int(fleet['owner_id']), int(unit['carapace']), int(unit['weight'])
			if key in keys:
				keys[key].add(unit)
			else:
				uwindow = UnitStackWindow(self, fleet['owner_id'], unit)
				keys[key] = uwindow
				uwindow.update()
				self.vbox.Add( uwindow)

class FleetPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		self.sizer = wx.BoxSizer(wx.VERTICAL)
				
		self.SetSizer(self.sizer)
		self.sizer.Layout()
	
	def set_fleets(self, evt):
		
		x,y = evt.attr1
		for fleet in db.db.iter_objects_list(db.Db.FLEET, {'=':{'x':x, 'y':y}}):
			self.add_fleet(fleet)

	def add_fleet(self, fleet):
		cp = wx.CollapsiblePane(self, label=fleet['name'], style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
		self.sizer.Add(cp)
		pane = cp.GetPane()
		
		owner_name = db.get_player_name(fleet['owner_id'])
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(pane, label='owner: %s'%(owner_name,)), 1, wx.EXPAND)

		border = wx.BoxSizer()
		border.Add(sizer, 1, wx.EXPAND|wx.ALL)
		pane.SetSizer(border)
		
		self.sizer.Layout()
		
		self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)
	
	def OnPaneChanged(self, evt=None):
		self.sizer.Layout()


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
		
	def set_coord(self, coord):
		
		self.sizer.DeleteWindows()
		
		dsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(dsizer)
		
		dups = {}
		protos = {}
		# buildings	if ours
		for building in db.garrison_units(db.getTurn(), db.filter_coord(coord)):
			bc = building['class']
			p = db.get_prototype(bc,('id', 'class', 'carapace', 'hp', 'name', 'is_building', 'max_count'))
			if int(p['is_building']) != 1:
				continue
				
			if int(p['max_count'])!=1:
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
			wsizer.Add(txt)
		self.sizer.Layout()

class PlanetPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1)
		self.sizer = wx.BoxSizer(wx.VERTICAL)

		self.SetSizer(self.sizer)
		self.sizer.Layout()

	def select_coord(self, evt):
		coord = evt.attr1
		self.sizer.DeleteWindows()
		
		self.sizer.Add( wx.StaticText(self, wx.ID_ANY, '%s:%s'%coord) )
		
		planet = db.get_planet(coord)
		owner = None
		name = None
		if not planet:
			self.sizer.Layout()
			return
		
		if 'o' in planet:
			self.sizer.Add( wx.StaticText(self, wx.ID_ANY, 'o: %s, e: %s, m: %s, t: %s, s: %s'%(planet['o'], planet['e'], planet['m'], planet['t'], planet['s'])) )
		
		if 'name' in planet and planet['name']:
			self.sizer.Add( wx.StaticText(self, wx.ID_ANY, planet['name']) )
		
		if 'owner_id' not in planet:
			self.sizer.Layout()
			return
		owner_id = planet['owner_id']
		if not owner_id:
			self.sizer.Layout()
			return
		owner_name = db.get_player_name(owner_id)
		self.sizer.Add( wx.StaticText(self, wx.ID_ANY, owner_name) )
		
		buildings = BuildingsWindows(self)
		buildings.set_coord(coord)
		self.sizer.Add(buildings)
		self.sizer.Layout()
		
class GarrisonPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		
	def select_coord(self, evt):
		coord = evt.attr1
		
		self.sizer.DeleteWindows()
		
		planet = db.get_planet(coord)
		if not planet or 'owner_id' not in planet:
			return
		
		item_windows = {}
		
		dups = {}
		protos = {}

		items = {}
		for unit in db.garrison_units(db.getTurn(), db.filter_coord(coord)):
			bc = unit['class']
			if bc in items:
				items[bc].append(unit)
				continue
				
			p = db.get_prototype(bc,('id', 'class', 'carapace', 'color', 'hp', 'name', 'is_building', 'transport_capacity', 'is_spaceship', 'is_serial', 'fly_speed', 'fly_range', 'support_main', 'support_second'))
			if int(p['is_building']) == 1:
				continue
			items[bc] = [unit]
			protos[bc] = p
			
		
		for bc, item_list in items.iteritems():
			p = protos[bc]
			sz = wx.BoxSizer(wx.HORIZONTAL)
			self.sizer.Add(sz)
			if 'carapace' in p and p['carapace']:
				img = image.getCarapaceImage(int(p['carapace']), int(p['color']))
			else:
				img = image.getBcImage(bc)
			bmp = wx.StaticBitmap(self)
			if img:
				bmp.SetBitmap(img)
			sz.Add(bmp)
			n_str = ''
			if len(item_list) > 1:
				n_str = 'x %s'%(len(item_list),)
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
			sz.Add(wx.StaticText(self, -1, '%s%s%s %s'%(fly, transport, n_str, name,)))

		self.sizer.Layout()
	
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
		self.sizer.Add( PlanetWindow(self, self.pos, self.turn, True) )
		self.sizer.Add( FleetWindow(self, self.pos, self.turn), 1, flag=wx.EXPAND | wx.ALL)
		self.sizer.Layout()
