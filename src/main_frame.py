import wx.aui
import logging
import os.path
import db
import version
import util
import map
import event
import config
import import_raw
import serialization
import object_filter
import unit_list
import users
import area_panel
import request
import planet_window
import history
import algorithm
import math
import loader
import action
import shutil
from store import store

from datetime import datetime

import save_load
import import_xml

def get_coord(obj):
	x = obj['x']
	y = obj['y']
	if type(x) is int:
		return x,y
	return int(x), int(y)
	
def filter_coord(coord):
	return ['x=%s'%(coord[0],), 'y=%s'%(coord[1],)]
	
def planet_area_filter(lt, size):
	return ['x>=%s'%(lt[0],), 'y>=%s'%(lt[1],), 'x<=%s'%(lt[0]+size[0],) ,'y<=%s'%(lt[1]+size[1],)]
	
CARAPACE_PROBE = 11

log = logging.getLogger('dclord')

h = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
h.setFormatter(formatter)
log.addHandler(h)
log.setLevel(logging.DEBUG)

def value_in(values, value):
	for v in values:
		if v in value:
			return True
	return False

class DcFrame(wx.Frame):
	def __init__(self, parent):
		sz = int(config.options['window']['width']), int(config.options['window']['height'])
		wx.Frame.__init__(self, parent, -1, "dcLord (%s): Divide & Conquer client (www.the-game.ru)"%(version.getVersion(),), style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE, size=sz)
		
		if int(config.options['window']['is_maximized'])==1:
			self.Maximize()
			
		self.makeMenu()
					
		#import_raw.processAllUnpacked()
		#self.map.turn = db.db.max_turn

		self.log_dlg = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE)
		self.log_dlg.Disable()
		self.log_dlg.SetBackgroundColour('WHITE')
		save_load.load_local_data()
		#serialization.load(ev_cb = self)
		
		#self.info_panel = planet_window.InfoPanel(self)
		self.planet_panel = planet_window.PlanetPanel(self)
		self.garrison_panel = planet_window.GarrisonPanel(self)
		self.object_filter = object_filter.FilterPanel(self)
		#self.planet_filter = object_filter.FilterFrame(self)
		#self.unit_list = unit_list.UnitPrototypeListWindow(self, 0)
		#self.history = history.HistoryPanel(self)
		#self.area_list = area_panel.AreaListWindow(self)

		self.sync_path = config.options['data']['sync_path']
		#self.info_panel.turn = db.getTurn()
		self.jump_fleets = set()
		
		self.map = map.Map(self)
		self.map.turn = db.getTurn()
		if 1 == int(config.options['map']['show_good']):
			self.onShowGood(None)
		#self.map.set_planet_filter(self.planet_filter)
		print 'map turn is set to %s'%(self.map.turn,)
		self.map.update()

		self.started = False
		self.actions_queue = []
		
		self.pf = None
		
		if self.map.turn != 0:
			self.log('loaded data for turn %d'%(self.map.turn,))
		
		self.pending_actions = request.RequestMaker()
		
		self._mgr = wx.aui.AuiManager(self)
		
		self.command_selected_user = False
		
		info = wx.aui.AuiPaneInfo()
		info.CenterPane()
		info.Fixed()
		info.DefaultPane()
		info.Resizable(True)
		info.CaptionVisible(False)
		
		self.fleets = planet_window.FleetPanel(self)
		self.actions = action.ActionPanel(self)
		
		self._mgr.AddPane(self.map, info)
		#self._mgr.AddPane(self.history, wx.RIGHT, "Turn")
		self._mgr.AddPane(self.fleets, wx.RIGHT, "Fleets")
		#self._mgr.AddPane(self.info_panel, wx.RIGHT, "Info")
		self._mgr.AddPane(self.planet_panel, wx.RIGHT, "Planet")
		self._mgr.AddPane(self.garrison_panel, wx.RIGHT, "Garrison")
		#self._mgr.AddPane(self.planet_filter, wx.LEFT, "Planets")
		self._mgr.AddPane(self.actions, wx.LEFT, "Actions")
		self._mgr.AddPane(self.object_filter, wx.LEFT, "Filter")
		#self._mgr.AddPane(self.unit_list, wx.RIGHT, "Units")
		self._mgr.AddPane(self.log_dlg, wx.BOTTOM, "Log")
		#self._mgr.AddPane(self.area_list, wx.RIGHT, "Areas")
		
		#self.map.set_planet_fileter(self.planet_filter)
		self._mgr.Update()
		
		
		#TODO: load from data
		self.manual_control_units = set()
		
		#unit id
		self.manual_control_units.add( 7906 )
		self.manual_control_units.add( 7291 ) # probes over Othes planets
		
		#TODO: load from file
		self.exclude_fleet_names = [] #busy, taken, etc...

		#p = config.options['window']['pane-info']
		#if p:
		#	print 'load p %s'%(p,)
		#	self._mgr.LoadPerspective( p )
		
		self.recv_data_callback = {}
		
		self.Bind(event.EVT_BUILD_UNIT, self.on_build_unit)
		self.Bind(event.EVT_DATA_DOWNLOAD, self.onDownloadRawData)
		self.Bind(event.EVT_MAP_UPDATE, self.onMapUpdate)
		self.Bind(event.EVT_USER_SELECT, self.onSelectUser)
		self.Bind(event.EVT_ACTIONS_REPLY, self.onActionsReply)
		self.Bind(event.EVT_SELECT_OBJECT, self.onObjectSelect)
		#self.info_panel.selectObject)
		#self.Bind(event.EVT_SELECT_OBJECT, self.planet_panel.select_coord)
		#self.Bind(event.EVT_SELECT_OBJECT, self.garrison_panel.select_coord)
		self.Bind(event.EVT_LOG_APPEND, self.onLog)
		#self.Bind(event.EVT_FLEET_JUMP, self.on_fleet_jump_prepare)
	
		#import_raw.processAllUnpacked()
		#serialization.save()
		
		#todo - restore previous state
		#self.Maximize()
		
		#self.history.updateTurns(self.map.turn)
		
	def onObjectSelect(self, evt):
		self.planet_panel.select_coord(evt)
		self.garrison_panel.select_coord(evt)
		#self.info_panel.selectObject(evt)
		self.fleets.set_fleets(evt)
		self.map.select_pos( evt.attr1 )
		
		routes = []
		for fleet_id in self.jump_fleets:
			fleet = store.get_object('fleet', {'fleet_id':fleet_id})
			if not fleet:
				continue
			route = self.calculate_route( fleet, evt.attr1 )
			if route:
				routes.append( route )
				fleet = store.get_object('fleet', {'fleet_id':fleet_id})
				
				self.actions.add_action( action.ActionJump(fleet['user_id'], fleet_id, evt.attr1))
			
		self.map.jump_fleets_routes = routes
		self.map.update()
		#self.map.set_fleet_routes(routes)
		
		
	def makeMenu(self):
		fileMenu = wx.Menu()
		exit_action = fileMenu.Append(wx.ID_ANY, "E&xit")
		self.Bind(wx.EVT_MENU, self.onClose, exit_action)
		self.Bind(wx.EVT_MENU, self.onAbout, fileMenu.Append(wx.ID_ANY, "&About dcLord"))
		self.Bind(wx.EVT_MENU, self.onExport, fileMenu.Append(wx.ID_ANY, "Export planets"))
		
		gameMenu = wx.Menu()
		self.updateMenu = gameMenu.Append(wx.ID_ANY, "&Download from sever")
		self.updateGeo = gameMenu.Append(wx.ID_ANY, "Download known planets from sever")
		
		self.geo_explore_menu = gameMenu.Append(wx.ID_ANY, "&Geo Explore all")
		self.fly_home_menu = gameMenu.Append(wx.ID_ANY, "Scouts fly home")
		self.make_fleets_menu = gameMenu.Append(wx.ID_ANY, "Make scout fleets")
		self.send_scouts = gameMenu.Append(wx.ID_ANY, "Send scout fleets")
		self.cancel_jump_menu = gameMenu.Append(wx.ID_ANY, "Cancel jump") 
		
		#cmd_sel_user = gameMenu.Append(wx.ID_ANY, "Command selected user", kind=wx.ITEM_CHECK)
		#gameMenu.Check(self.view_show_geo.GetId(), 1==int(config.options['map']['draw_geo']))
		#self.command_selected_user
		
		usersMenu = gameMenu.Append(wx.ID_ANY, "U&sers")
		routesMenu = gameMenu.Append(wx.ID_ANY, "&Routes")
		
		syncMenu = wx.Menu()
		set_sync_dir = syncMenu.Append(wx.ID_ANY, "Set sync path")
		
		self.view = wx.Menu()
		self.view_show_geo = self.view.Append(wx.ID_ANY, "Show geo", kind=wx.ITEM_CHECK)
		self.view.Check(self.view_show_geo.GetId(), 1==int(config.options['map']['draw_geo']))

		self.view_show_good_planets = self.view.Append(wx.ID_ANY, "Show good planets", kind=wx.ITEM_CHECK)
		self.view.Check(self.view_show_good_planets.GetId(), 1==int(config.options['map']['show_good']))
		
		#actionMenu = wx.Menu()
		#actionDefineArea = actionMenu.Append(
		
		panel = wx.MenuBar()
		panel.Append(fileMenu, "&File")
		panel.Append(gameMenu, "G&ame")
		panel.Append(self.view, "Vie&w")
		panel.Append(syncMenu, "Sync")
		self.SetMenuBar(panel)
		
		self.Bind(wx.EVT_MENU, self.onShowGeo, self.view_show_geo)
		self.Bind(wx.EVT_MENU, self.onShowGood, self.view_show_good_planets)
		self.Bind(wx.EVT_MENU, self.onShowUsers, usersMenu)
		self.Bind(wx.EVT_MENU, self.onUpdate, self.updateMenu)
		self.Bind(wx.EVT_MENU, self.onUpdateGeo, self.updateGeo)
		
		self.Bind(wx.EVT_MENU, self.onExploreGeoAll, self.geo_explore_menu)
		self.Bind(wx.EVT_MENU, self.cancel_jump, self.cancel_jump_menu)
		self.Bind(wx.EVT_MENU, self.onSendScouts, self.send_scouts)
		self.Bind(wx.EVT_MENU, self.onFlyHomeScouts, self.fly_home_menu)
		self.Bind(wx.EVT_MENU, self.onMakeScoutFleets, self.make_fleets_menu)
		#self.Bind(wx.EVT_MENU, self.onCalculateRoutes, routesMenu)
		self.Bind(wx.EVT_MENU, self.onSetSyncPath, set_sync_dir)
	
		self.Bind(wx.EVT_CLOSE, self.onClose, self)

	def onExport(self, evt):
		
		dlg = wx.DirDialog(self, 'Set export csv file')
		if dlg.ShowModal() == wx.ID_OK:
			serialization.export_planets_csv(dlg.GetPath())
		
		str_export = ''
		for planet in db.db.iter_objects_list(db.Db.PLANET):
			str_export += '%s'
	
	def onSetSyncPath(self, evt):
		dlg = wx.DirDialog(self, 'Set sync directory path', os.path.join('/home/xar/Dropbox', 'the-game-sync'))
		if dlg.ShowModal() == wx.ID_OK:
			self.sync_path = dlg.GetPath()
			config.options['data']['sync_path'] = self.sync_path
			self.sync_data()
			
	def sync_data(self):
		save_load.load_local_data()
		save_load.save_local_data()
		
	def on_fleet_jump_prepare(self, fleet_id):

		#if fleet_id in self.jump_fleets:
		#	self.jump_fleets.remove(fleet_id)
		#else:
		#self.jump_fleets.add(fleet_id)
		self.jump_fleets.clear()
		self.jump_fleets.add(fleet_id)

		#self.calculate_route(store.get_object('fleet', {'fleet_id':fleet_id}), self.map
		#self.map.toggle_fleet_jump(fleet_id)
		
	def calculate_route(self, fleet, dest_point):
		
		open_planets = store.get_objects_list('open_planet', {'user_id':fleet['user_id']})
		start_point = int(fleet['x']), int(fleet['y'])
		
		spd,rng = store.get_fleet_speed_range(fleet['fleet_id'])
		return algorithm.route_find(fleet, rng, dest_point)
		#self.pf = algorithm.PathFinder(start_point, dest_point, spd,rng , [(int(p['x']),int(p['y'])) for p in open_planets])
		#self.map.show_route(self.pf)
		#self.map.update()
		
		
	def findRoute(self):
		
		isdone = False
		while not isdone:
			isdone = self.pf.step()
			self.map.update()
			wx.Yield()
	
	def onShowGeo(self, evt):
		
		show_geo = self.view.IsChecked( self.view_show_geo.GetId() )
		config.options['map']['draw_geo'] = show_geo
		self.map.draw_geo = show_geo
		
		#self.view.Check(self.view_show_geo.GetId(), bool())
		self.map.update()

	def onShowGood(self, evt):
		show_good = self.view.IsChecked( self.view_show_good_planets.GetId() )
		config.options['map']['show_good'] = show_good
		self.map.showGood(show_good)
				
	def showHidePane(self, paneObject):
		pane = self._mgr.GetPane(paneObject)
		if pane.IsShown():
			self._mgr.ClosePane(pane)
		else:
			self._mgr.RestorePane(pane)
		self._mgr.Update()
	
	def onShowUsers(self, evt):
		p = users.UsersPanel(self)
		p.Show()
		#p.init()
	
	def onMapUpdate(self, evt):
		self.map.update()
		
	def onClose(self, event):
		#config.options['window']['pane-info'] = self._mgr.SavePerspective()
		self.updateConfig()
		#print '%s'%(self._mgr.SavePerspective(),)
		#self.conf.panes = 

		#print 'saving "%s"'%(self.conf.panes,)
		#self.conf.save()
		self.Destroy()
		
	def closeApp(self, event):
		self.Close()
		
	def updateConfig(self):
		w,h = self.GetClientSize()
		config.options['window']['height'] = h
		config.options['window']['width'] = w
		config.options['window']['is_maximized'] = int(self.IsMaximized())		

		config.options['map']['offset_pos_y'] = self.map.offset_pos[1]
		config.options['map']['offset_pos_x'] = self.map.offset_pos[0]
		
		config.options['map']['cell_size'] = self.map.cell_size

		config.saveOptions()
		
	def onAbout(self, event):
		info = wx.AboutDialogInfo()
		info.AddDeveloper('bogolt (bogolt@gmail.com)')
		info.SetName('dcLord')
		info.SetWebSite('https://github.com/bogolt/dclord')
		info.SetVersion(version.getVersion())
		info.SetDescription('Divide and Conquer\ngame client\nsee at: http://www.the-game.ru')
		wx.AboutBox(info)
	
	def showPlayersView(self, event):
		if self.players:
			self.players.Show(True)
			return

		self.players = self.res.LoadFrame(None, 'PlayersView')
		self.players.setConf(self.conf)
		self.players.Show(True)

	def onUpdateGeo(self, event):
		'download and process info from server'
		import loader
		l = loader.AsyncLoader()
		
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		for acc in config.accounts():
			log.info('requesting user %s info'%(acc['login'],))
			d = os.path.join(util.getTempDir(), 'raw_data') if not out_dir else out_dir
			l.getKnownPlanets( self, acc['login'], d)
		l.start()

	def onUpdate(self, event):
		'download and process info from server'
		import loader
		l = loader.AsyncLoader()
		
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		for acc in config.accounts():
			if self.command_selected_user and int(acc['id']) != self.map.selected_user_id:
				continue
			log.info('requesting user %s info'%(acc['login'],))
			for msg_type in ['all', 'known_planets', 'fleetsmessages']:
				l.getDcData(self, acc['login'], msg_type, out_dir)
		l.start()

	def onUpload(self, event):
		'upload pending events on server'
		
		# epxlore, send back
		#self.cancel_jump()
		#self.explore_all()
		#self.send_back()
		pass
	
	def perform_actions(self):
		if self.pending_actions.is_empty():
			return
					
		login = config.user_id_dict[self.pending_actions.user_id]['login']
		self.actions_queue.append( (login, str(self.pending_actions) ) )
		self.pending_actions.clear()
		
		if not self.started:
			self.perform_next_action()
			
	def perform_next_action(self):
		if self.actions_queue==[]:
			return
		login, acts = self.actions_queue[0]
		del self.actions_queue[0]
		
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)

		l = loader.AsyncLoader()
		l.sendActions(self, login, acts, out_dir)
		l.start()
		
	def create_fleet(self, user_id, fleet_name, planet_coord, count = 1):
		
		self.pending_actions.user_id = user_id
		
		for _ in range(0, count):
			self.pending_actions.createNewFleet(coord, fleet_name)
		
		self.perform_actions()
	
	def is_geo_scout(self, unit):
		for act in store.iter_objects_list('proto_action', {'proto_id':unit['proto_id']}):
			print 'proto action %s'%(act,)
			if act['proto_action_id']== request.RequestMaker.GEO_EXPLORE:
				return True
		return False
	
	def is_geo_scout_fleet(self, fleet_id):
		for u in store.get_fleet_units(fleet_id):
			if self.is_geo_scout(u):
				return True
		return False

	def onSendScouts(self, _):
		min_size = 70
		max_size = 99
		
		#helps avoid flying on the same planet with different accounts
		friend_geo_scout_ids = []
		for user in db.users():
			friend_geo_scout_ids.append(str(user['id']))
		
		for acc in config.accounts():
			user_id = int(acc['id'])

			if self.command_selected_user and user_id != self.map.selected_user_id:
				continue

			self.pending_actions.user_id = user_id
			log.info('send scouts %s size %s'%(acc['login'], min_size))
					
			# find units that can geo-explore
			# find the ones that are already in fleets in one of our planets
			
			fly_range = 0.0
			ready_scout_fleets = {}
			# get all fleets over our planets
			for planet in store.iter_objects_list('open_planet', {'user_id':user_id}):
				print 'open planet %s'%(planet,)
				coord = get_coord(planet)
				for fleet in store.iter_objects_list('fleet', {'user_id':user_id, 'x':coord[0], 'y':coord[1]}):
					if value_in(self.exclude_fleet_names, fleet['name']):
						continue
					units = store.get_fleet_units(fleet['fleet_id'])
					if len(units) != 1:
						print 'fleet %s has wrong units count ( != 1 ) %s, skipping it'%(fleet, units)						
						continue
					unit = units[0]
					if int(unit['unit_id']) in self.manual_control_units:
						print 'unit %s reserved for manual control, skipping it'%(unit,)
						continue

					if not self.is_geo_scout(unit):
						print 'unit %s is not geo-scout, skipping it'%(unit,)
						continue
					#fly_range = max(fly_range, )
					print 'unit %s on planet %s for fleet %s is geo-scout'%(unit, coord, fleet)
					# ok, this is geo-scout, single unit in fleet, on our planet
					#ready_scout_fleets.append((coord, fleet))
					_,r = store.get_fleet_speed_range(fleet['fleet_id'])
					fly_range = max(fly_range, r)
					ready_scout_fleets.setdefault(coord, []).append((fleet, r))
					
			
			# get possible planets to explore in nearest distance
			for coord in ready_scout_fleets.keys():
				print 'load geo size centered at %s with range %s'%(coord, int(fly_range))
				save_load.load_geo_size_center(coord, int(fly_range))
			
			# jump to nearest/biggest unexplored planet
			exclude = set()
			for coord, fleets in ready_scout_fleets.iteritems():
				max_fly_range = 0
				for f,r in fleets:
					max_fly_range = max(max_fly_range, r)
				
				possible_planets = []
				#s<=99 - skip stars
				#dx = lt[0]-fly_range, lt[0]+fly_range
				#dy = lt[1]-fly_range, lt[1]+fly_range
				for p in store.iter_planets_size(pos=coord, fly_range=max_fly_range, size_min=min_size, bigger_first = True):
					if not (p['s']>=min_size and p['s']<=max_size):
						print 'planet %s not fit the size'%(p,)
						continue
					dest = get_coord(p)
					if dest in exclude:
						continue
					dist = util.distance(dest, coord)
					if dist > fly_range:
						print 'planet %s is too far away'%(p,)
						continue
						
					planet = db.get_planet(dest)
					if planet and 'o' in planet and planet['o']:
						print 'planet %s already explored'%(p,)
						continue
					
					has_flying_geo_scouts = False
					
					# check if currently there is some explore fleet on planet, or explore fleet already fly there
					already_has_scout = False
					for fleet in store.iter_objects_list('fleet', {'x':dest[0], 'y':dest[1]}, controlled = True):
						if self.is_geo_scout_fleet(fleet['fleet_id']):
							already_has_scout = True
							break
					if already_has_scout:
						print 'planet %s has scount fleet on it'%(p,)
						continue
						
					already_fly_geo_scouts = False
					for fleet in store.iter_objects_list('flying_fleet', {'x':dest[0], 'y':dest[1]}, controlled = True):
						if self.is_geo_scout_fleet(fleet['fleet_id']):
							already_fly_geo_scouts = True
							#self.actions.add_action( action.ActionGeoExplore(user_id, ':dest, 'fleet_id':fleet['fleet_id']}))
							break
					if already_fly_geo_scouts:
						print 'planet %s has flying scount fleet'%(p,)
						continue

					possible_planets.append( (dist, dest) )
					print 'add possible planet %s'%(dest,)

				for fleet, fleet_range in fleets:
					print 'check planets for fleet %s'%(fleet,)
					for dist, planet in sorted(possible_planets):
						if dist > fleet_range:
							print 'planet %s too scary'%(p,)
							continue
						# ok fly to it
						self.actions.add_action( action.ActionJump(user_id, fleet['fleet_id'], planet ))
						#self.pending_actions.fleetMove(fleet['id'], planet)
						exclude.add( planet )
						print 'jump %s from %s to %s'%(fleet, coord, planet)
						possible_planets.remove( (dist, planet ) )
						break
							
			#self.perform_actions()

	def perform_commands(self, acc, cmds):
		cmds = {'move':[(fleet_id, (x,y))], 'create_fleet':[('name', (x,y))], 'unit_to_fleet':[(unit_id, fleet_id)], 'geo_explore':[unit_id], 'colonize':[unit_id], 'arc_colonize':[unit_id], 'build':[], 'cancel_colonize':[colonize_action], 'cancel_jump':[fleet_id]}
	
	def onMakeScoutFleets(self, _):		
		# get all planets
		# get harrison units able to scout
		# create fleets
		# put units to fleets
		
		# get all scouting fleets ( available to jump ( on my planets ) )
		# get unexplored planets
		# send nearest fleets to these planets
		
		# load size-map, use it to scout biggest first ( N > 70, descending )
		
		# get all scouting fleets ( on other planets )
		# geo-explore
		# send them back to nearest home planet
		
		#command_type, 
		#move_command = ('move_to', 
		
		#move_commands = [((x,y), fleet_id)]
	
		carapace = 11 # probe/zond
		fleet_name = 'scout:geo'
		turn = db.getTurn()
		
		for acc in config.accounts():
			if not 'id' in acc:
				continue
			user_id = int(acc['id'])
			
			#if user_id < 601140:
			#	continue

			probes_types = store.get_objects_list('proto', {'carapace':carapace, 'user_id':user_id})
			#any_class = 'class in (%s)'%(','.join([str(cls) for cls in units_classes]),)
			#print 'testing user %s with class %s'%(user_id, any_class)
			probe_ids = [str(proto['proto_id']) for proto in probes_types]
			
			self.pending_actions.user_id = user_id
			pending_units = []
			
			for planet in store.iter_objects_list('user_planet', {'user_id':user_id}):
				coord = get_coord(planet)
				#print 'checking harrison for planet %s'%(planet,)
				for unit in store.get_garrison_units(coord, value_in=('proto_id', probe_ids)):
					print 'found unit %s on planet %s'%(unit, planet,)
					action_create = action.ActionCreateFleet(user_id, fleet_name, coord)
					self.actions.add_action(action_create)
					fleet_id = action_create.fleet_id
					
					self.actions.add_action(action.ActionUnitMove(user_id, fleet_id, unit['unit_id']))
					
					#self.actions.add_action(action.Action('unit_move', user_id, {'planet':coord, 'unit_id':unit['unit_id'], 'fleet_id':fleet_id}))
					#self.actions.add_action(action.Action('unit_move', user_id, {'planet':coord, 'unit_id':unit['unit_id'], 'fleet_id':fleet_id}))
					
					#self.pending_actions.createNewFleet(coord, fleet_name)
					#pending_units.append( (self.pending_actions.get_action_id(), coord, unit['id'] ) )
					
					#print 'found unit %s on planet %s'%(unit, coord )
			
			if len(pending_units) == 0:
				continue
			
			#self.recv_data_callback[acc['login']] = (self.cb_move_units_to_fleets, user_id, pending_units )
			# exec actions to create fleets on the planets
			#self.perform_actions()
			
	def cb_move_units_to_fleets(self, user_id, units):
		
		turn = db.getTurn()
		self.pending_actions.user_id = user_id
		at_least_one = False
		#print 'executing move_units_to_fleets with user %s, units %s'%(user_id, units)
		for act_id, coord, unit_id in units:
			#print 'action %s, coord %s, unit %s'%(act_id, coord, unit_id)
			# get fleet for these coords
			res = db.get_action_result(act_id)
			if not res:
				#print 'oops no result'
				continue
			ret_id, is_ok = res
			#print 'result is %s %s'%(ret_id, is_ok)
			if not is_ok:
				continue
			
			at_least_one = True
			#print 'moving unit %s to fleet %s'%(unit_id, ret_id)
			self.pending_actions.moveUnitToFleet(ret_id, unit_id)
			
		if at_least_one:
			self.perform_actions()
	
	def harrison_units_to_fleets(self, user_id, coord, unit_type, fleets_ids):
		#TODO: check if fleet empty
		#add fleet new info to local-db
		
		turn = db.getTurn()
		self.pending_actions.user_id = user_id
		
		i = 0
		if len(fleet_ids) < 1:
			return

		for unit in db.db.iter_objects_list(db.Db.UNIT, {'=':{'x':coord[0], 'y':coord[1], 'fleet_id':0, 'class':unit_type}}):
			self.pending_actions.moveUnitToFleet(fleet_ids[i], unit['id'])
			i += 1
			if i >= len(fleet_ids):
				break

		self.perform_actions( )		

	def cancel_jump(self, evt):

		turn = db.getTurn()
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)

		for acc in config.accounts():
			user_id = int(acc['id'])
			self.pending_actions.user_id = user_id
			
			fleets = []
			fleet_flt = ['owner_id=%s'%(user_id,)]
			
			fleet_name = None #unicode('Fleet')
			# can also filter fleets by names
			#TODO: beware escapes
			if fleet_name:
				fleet_flt.append( 'name="%s"'%(fleet_name,) ) 
			for fleet in db.flyingFleets(turn, fleet_flt):
				#print 'found fleet %s'%(fleet,)
				if fleet['in_transit'] != 0:
					continue
				#print 'fleet %s can be stopped'%(fleet,)
			
				self.pending_actions.cancelJump(fleet['id'])
			
			self.perform_actions()
				
	def onFlyHomeScouts(self, _):
				
		for acc in config.accounts():
			if not 'id' in acc:
				continue
			user_id = int(acc['id'])
			self.pending_actions.user_id = user_id
			#print 'fly home scouts for user %s %s'%(user_id, acc['login'])
							
			# fly scouts back to base
			
			fleets = []
			fleet_flt = ['owner_id=%s'%(user_id,)]
			
			fleet_name = None #unicode('Fleet')
			# can also filter fleets by names
			#TODO: beware escapes
			if fleet_name:
				fleet_flt.append( 'name="%s"'%(fleet_name,) ) 
			for fleet in store.iter_objects_list('fleet', {'user_id':user_id}):
				#print 'found fleet %s'%(fleet,)
				# if fleet over empty planet - jump back home
				coord = get_coord(fleet)
				coord_filter = {'x':coord[0], 'y':coord[1]}
				planet = store.get_object('planet', coord_filter )
				#TODO: allow jump on all open-planets ( not only owned by user )
				coord_filter['user_id'] = user_id
				user_open_planet = store.get_object('open_planet', coord_filter )
				if user_open_planet:
					continue

				#print 'fleet %s not at home'%(fleet['id'],)
				units = []
				for unit in store.get_fleet_units(fleet['fleet_id']):
					#print 'fleet %s has unit %s'%(fleet['id'], unit)
					units.append(unit)
				
				# not a scout fleet if more then one unit in fleet
				# if zero units - don't care about empty fleet as well
				if len(units) != 1:
					#print 'fleet %s has %s units, while required 1'%(fleet['id'], len(units))
					continue

				if int(units[0]['unit_id']) in self.manual_control_units:
					continue

				proto = store.get_object('proto', {'proto_id':units[0]['proto_id']})
				if proto['carapace'] != CARAPACE_PROBE:
					#print 'fleet %s unit %s is not a probe'%(fleet['id'], units[0])
					continue

				#jump back
				#print 'fleet %s %s needs to get home'%(coord, fleet)
				fleets.append( (coord, fleet) )					

			if not fleets:
				#print 'no scout fleets found not at home'
				continue
			
			coords = []
			for planet in store.iter_objects_list('open_planet', {'user_id':user_id}):
				coord = get_coord(planet)
				coords.append( coord )
				#print 'possible home planet %s'%(coord,)
				
			if coords == None or fleets == []:
				#print 'oops %s %s'%(coords, fleets)
				continue
			
			#print 'looking for best route for %s fleets' %(len(fleets,),)
			for coord, fleet in fleets:
				#find closest planet
				closest_planet = coords[0]
				min_distance = util.distance(coords[0], coord)
				for c in coords:
					if util.distance(coord, c) < min_distance:
						min_distance = util.distance(coord, c)
						closest_planet = c
				
				# ok, found then jump
				#print 'Jump (%s) %s'%(closest_planet, fleet)
				
				self.actions.add_action( action.ActionJump(user_id, fleet['fleet_id'], closest_planet ))
				#self.pending_actions.fleetMove( fleet['fleet_id'], closest_planet )
			
			#self.perform_actions()

	def on_build_unit(self, evt):
		print 'build unit %s on %s'%(evt.attr1, evt.attr2)
		coord = evt.attr2
		user_planet = store.get_object('user_planet', {'x':coord[0], 'y':coord[1]})
		if not user_planet:
			print 'planet %s owner unknown'%(coord,)
			return
		self.actions.add_action(action.ActionBuild(user_planet['user_id'], coord, evt.attr1))
		self.planet_panel.update()
	# geo explore
	# load known planets
	# 1. rename ( baken )
	# 2. fly somewhere ( closest jumpable )
	# 
	
	def onExploreGeoAll(self, _):
		'upload pending events on server'
		
		explore_owned_planets = True
		
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		for acc in config.accounts():
			if not 'id' in acc:
				continue
			user_id = int(acc['id'])
				
			log.info('requesting user %s info'%(acc['login'],))
			# find if there is any explore-capable fleets over unexplored planets
			# or simply tell explore to every unit =))) game server will do the rest
			
			#1. find all fleets above empty planets
			
			# get fleet position, check if planet geo is unknown
			fleet_planet = {}
			pl = {}
			
			for fleet in store.iter_objects_list('fleet', {'user_id':acc['id']} ):
				#print 'got fleet %s'%(fleet,)
				coord = get_coord(fleet)
				
				if coord in pl:
					pl[coord].add(fleet['fleet_id'])
					continue

				planet = store.get_object('planet', {'x':coord[0], 'y':coord[1]})
				#check holes and stars
				if not planet:
					continue
				
				# check if already explored
				if 'o' in planet and planet['o']:
					continue
				
				if not coord in pl:
					pl[coord] = set()
				pl[ coord ].add(fleet['fleet_id'])
				#print 'Add to exploration list planet %s'%(planet,)
			
			acts = {}
			
			# get all fleet units, check if explore capable
			for coord, planet_fleets in pl.iteritems():
				for fleet_id in planet_fleets:
					for unit in store.get_fleet_units(fleet_id):
						#print '%s %s unit %s'%(coord, fleet_id, unit)
						# ok unit
						bc = unit['proto_id']
						
						#for proto in db.prototypes(['id=%s'%(bc,)]):
						#	print 'proto %s'%(proto,)

						#type 1 probably geo explore
						action_geo_explore = store.get_object('proto_action',{'proto_id':bc, 'proto_action_id':request.RequestMaker.GEO_EXPLORE})
						if action_geo_explore:
							acts[coord] = unit['unit_id']
							break
					# no need to request more then one explore of a single planet
					if coord in acts:
						break

			self.pending_actions.user_id = int(acc['id'])
			#self.pendingActions[int(acc['id'])] = actions
			#hw_planet = db.getUserHw(acc['id'])
			#actions.createNewFleet(hw_planet, 'a_new_shiny_fleet')
			
			at_least_one = False
			for coord, unit_id in acts.iteritems():
				#print 'explore (%s) %s'%(coord, unit_id)
				self.actions.add_action(action.ActionGeoExplore(user_id, unit_id, coord))
				#self.pending_actions.explore_planet( coord, unit_id )
				at_least_one = True
			
			if at_least_one:
				self.perform_actions()
				
				#request updated known_planets info
				#self.request_data('known_planets', acc)
				
		
		# now request new known_planets, to get the exploration results
		
	def request_data(self, request, acc):
		import loader
		l = loader.AsyncLoader()
		
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirExist(out_dir)
		log.info('requesting user %s info'%(acc['login'],))
		d = os.path.join(util.getTempDir(), 'raw_data') if not out_dir else out_dir
		l.getDcData(self, acc['login'], request, d, out_dir)
		l.start()
		
	def onActionsReply(self, event):
		user = event.attr1
		actions = event.attr2
		
		#self.pendingActions[int(user['id'])]
	
	def log(self, message):
		self.log_dlg.AppendText('%s %s\n'%(datetime.now(), message))

	def onLog(self, evt):
		self.log_dlg.AppendText(str(datetime.now()) + " " + evt.attr1 + '\n')
	
	def process_performed_actions(self, user_id):
		pass
	
	def onDownloadRawData(self, evt):
		key = evt.attr1
		path = evt.attr2
		if not key:
			log.info('all requested data downloaded')
			self.log('All requested data downloaded')
			save_load.save_local_data()
			#local_data_path = config.options['data']['path']
			#save_load.save_common_data(os.path.join(local_data_path, 'common')
			
			#sync_data_path = config.options['data']['sync_path']
			#if sync_data_path:
			#	save_load.save_common_data(os.path.join(sync_data_path), config.options['data']['sync_key'])
			self.map.update()
			return
		if not path:
			log.error('failed to load info for user %s'%(key,))
			self.log('Error: failed to load info for user %s'%(key,))
			return
		
		self.log('Downloaded %s %s'%(key, path))
		user = import_xml.processRawData(path)
		if not user:
			#status_text = 'Not authorized' if status == import_raw.XmlHandler.StatusAuthError else 'Turn in progress'
			self.log('Error processing %s'%(key))
		else:
			
			for login, acc in config.users.iteritems():
				if login == key and not 'id' in acc:
					acc['id'] = int(user['user_id'])
					print 'got user id %s for user %s'%(acc['id'], login)
					config.users[login] = acc
					config.saveUsers()
					
					config.user_id_dict[acc['id']] = acc
			
			if 'name' in user and 'turn' in user:
				self.backup_xml(path, user)
			if 'request' in user and '1' == user['request']:
				self.process_performed_actions(user['user_id'])
		
		#if key in self.recv_data_callback:
		#	func, user_id, data = self.recv_data_callback[key]
		#	del self.recv_data_callback[key]
		#	func(user_id, path)
		#	db.clear_action_result(user_id)
		
		self.map.update()
		self.object_filter.update()
		#self.history.updateTurns(self.map.turn)
		
		#self.started = False
		#self.perform_next_action()
	
	def backup_xml(self, path, user):
		backup_dir = os.path.join(config.options['data']['path'], 'backup/%s/%s_%s/'%(user['turn'], user['user_id'], user['name']))
		util.assureDirExist(backup_dir)
		shutil.copy(path, backup_dir)
	
	def onSelectUser(self, evt):
		user_id = evt.attr1

		#user_id = int(config.users[login]['id'])
		#self.unit_list.setPlayer( user_id )
		self.map.selectUser( user_id)
 
