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
from datetime import datetime

def get_coord(obj):
	x = obj['x']
	y = obj['y']
	if type(x) is int:
		return x,y
	return int(x), int(y)
	
def filter_coord(coord):
	return ['x=%s'%(coord[0],), 'y=%s'%(coord[1],)]
	
def distance(a, b):
	dx = a[0]-b[0]
	dy = a[1]-b[1]
	return math.sqrt( dx * dx + dy * dy ) 

def planet_area_filter(lt, size):
	return ['x>=%s'%(lt[0],), 'y>=%s'%(lt[1],), 'x<=%s'%(lt[0]+size[0],) ,'y<=%s'%(lt[1]+size[1],)]
	
CARAPACE_PROBE = 11

log = logging.getLogger('dclord')

h = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
h.setFormatter(formatter)
log.addHandler(h)
log.setLevel(logging.DEBUG)

class DcFrame(wx.Frame):
	def __init__(self, parent):
		sz = int(config.options['window']['width']), int(config.options['window']['height'])
		wx.Frame.__init__(self, parent, -1, "dcLord (%s): Divide & Conquer client (www.the-game.ru)"%(version.getVersion(),), style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE, size=sz)
		
		if int(config.options['window']['is_maximized'])==1:
			self.Maximize()
					
		#import_raw.processAllUnpacked()
		#self.map.turn = db.db.max_turn

		self.log_dlg = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE)
		self.log_dlg.Disable()
		self.log_dlg.SetBackgroundColour('WHITE')
		serialization.load(ev_cb = self)
		
		self.info_panel = planet_window.InfoPanel(self)
		self.object_filter = object_filter.FilterPanel(self)
		self.planet_filter = object_filter.FilterFrame(self)
		#self.unit_list = unit_list.UnitPrototypeListWindow(self, 0)
		self.history = history.HistoryPanel(self)
		#self.area_list = area_panel.AreaListWindow(self)

		self.sync_path = config.options['data']['sync_path']
		self.info_panel.turn = db.getTurn()
		print 'db max turn is %s'%(db.getTurn(),)
		
		self.map = map.Map(self)
		self.map.turn = db.getTurn()
		self.map.set_planet_filter(self.planet_filter)
		print 'map turn is set to %s'%(self.map.turn,)
		self.map.update()

		self.started = False
		self.actions_queue = []
		
		self.pf = None
		
		if self.map.turn != 0:
			self.log('loaded data for turn %d'%(self.map.turn,))
		
		self.pending_actions = request.RequestMaker()
		
		self._mgr = wx.aui.AuiManager(self)
		
		
		info = wx.aui.AuiPaneInfo()
		info.CenterPane()
		info.Fixed()
		info.DefaultPane()
		info.Resizable(True)
		info.CaptionVisible(False)
		
		self._mgr.AddPane(self.map, info)
		self._mgr.AddPane(self.history, wx.RIGHT, "Turn")
		self._mgr.AddPane(self.info_panel, wx.RIGHT, "Info")
		self._mgr.AddPane(self.planet_filter, wx.LEFT, "Planets")
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


		#p = config.options['window']['pane-info']
		#if p:
		#	print 'load p %s'%(p,)
		#	self._mgr.LoadPerspective( p )
		
		self.recv_data_callback = {}
		
		self.makeMenu()
		
		self.Bind(event.EVT_DATA_DOWNLOAD, self.onDownloadRawData)
		self.Bind(event.EVT_MAP_UPDATE, self.onMapUpdate)
		self.Bind(event.EVT_USER_SELECT, self.onSelectUser)
		self.Bind(event.EVT_ACTIONS_REPLY, self.onActionsReply)
		self.Bind(event.EVT_SELECT_OBJECT, self.info_panel.selectObject)
		self.Bind(event.EVT_TURN_SELECTED, self.onTurnSelected)
		self.Bind(event.EVT_LOG_APPEND, self.onLog)
	
		#import_raw.processAllUnpacked()
		#serialization.save()
		
		#todo - restore previous state
		#self.Maximize()
		
		self.history.updateTurns(self.map.turn)
		
	def makeMenu(self):
		fileMenu = wx.Menu()
		exit_action = fileMenu.Append(wx.ID_ANY, "E&xit")
		self.Bind(wx.EVT_MENU, self.onClose, exit_action)
		self.Bind(wx.EVT_MENU, self.onAbout, fileMenu.Append(wx.ID_ANY, "&About dcLord"))
		
		gameMenu = wx.Menu()
		self.updateMenu = gameMenu.Append(wx.ID_ANY, "&Download from sever")
		self.updateGeo = gameMenu.Append(wx.ID_ANY, "Download known planets from sever")
		
		self.geo_explore_menu = gameMenu.Append(wx.ID_ANY, "&Geo Explore all")
		self.fly_home_menu = gameMenu.Append(wx.ID_ANY, "Scouts fly home")
		self.make_fleets_menu = gameMenu.Append(wx.ID_ANY, "Make scout fleets")
		self.send_scouts = gameMenu.Append(wx.ID_ANY, "Send scout fleets")
		self.cancel_jump_menu = gameMenu.Append(wx.ID_ANY, "Cancel jump") 
		
		usersMenu = gameMenu.Append(wx.ID_ANY, "U&sers")
		routesMenu = gameMenu.Append(wx.ID_ANY, "&Routes")
		
		syncMenu = wx.Menu()
		set_sync_dir = syncMenu.Append(wx.ID_ANY, "Set sync path")
		
		self.view = wx.Menu()
		self.view_show_geo = self.view.Append(wx.ID_ANY, "Show geo", kind=wx.ITEM_CHECK)
		self.view.Check(self.view_show_geo.GetId(), 1==int(config.options['map']['draw_geo']))
		
		#actionMenu = wx.Menu()
		#actionDefineArea = actionMenu.Append(
		
		panel = wx.MenuBar()
		panel.Append(fileMenu, "&File")
		panel.Append(gameMenu, "G&ame")
		panel.Append(self.view, "Vie&w")
		panel.Append(syncMenu, "Sync")
		self.SetMenuBar(panel)
		
		self.Bind(wx.EVT_MENU, self.onShowGeo, self.view_show_geo)
		self.Bind(wx.EVT_MENU, self.onShowUsers, usersMenu)
		self.Bind(wx.EVT_MENU, self.onUpdate, self.updateMenu)
		self.Bind(wx.EVT_MENU, self.onUpdateGeo, self.updateGeo)
		
		self.Bind(wx.EVT_MENU, self.onExploreGeoAll, self.geo_explore_menu)
		self.Bind(wx.EVT_MENU, self.cancel_jump, self.cancel_jump_menu)
		self.Bind(wx.EVT_MENU, self.onSendScouts, self.send_scouts)
		self.Bind(wx.EVT_MENU, self.onFlyHomeScouts, self.fly_home_menu)
		self.Bind(wx.EVT_MENU, self.onMakeScoutFleets, self.make_fleets_menu)
		self.Bind(wx.EVT_MENU, self.onCalculateRoutes, routesMenu)
		self.Bind(wx.EVT_MENU, self.onSetSyncPath, set_sync_dir)
	
		self.Bind(wx.EVT_CLOSE, self.onClose, self)

	
	def onSetSyncPath(self, evt):
		dlg = wx.DirDialog(self, 'Set sync directory path', os.path.join('/home/xar/Dropbox', 'the-game-sync'))
		if dlg.ShowModal() == wx.ID_OK:
			self.sync_path = dlg.GetPath()
			config.options['data']['sync_path'] = self.sync_path
			self.sync_data()
			
	def sync_data(self):
		serialization.load_sync_data()
		serialization.save_sync_data()
		
	def onCalculateRoutes(self, evt):
		planets = []
		for p in db.planets(self.map.turn, ['owner_id is not null'], ('x', 'y')):
			planets.append( (int(p['x']), int(p['y'])))
			
		
		self.pf = algorithm.PathFinder(planets[0], planets[1], 1.2, 6, planets)
		self.map.show_route(self.pf)
		self.map.update()
		
		while self.pf.angle < 120:
			self.findRoute()
			if self.pf.is_found():
				break
			self.pf.extend()
		
	def findRoute(self):
		
		isdone = False
		while not isdone:
			isdone = self.pf.step()
			self.map.update()
			wx.Yield()
	
	def onShowGeo(self, evt):
		show_geo = 1 == int(config.options['map']['draw_geo'])
		show_geo = 0 if show_geo==1 else 1
		config.options['map']['draw_geo'] = show_geo
		self.map.draw_geo = 1==show_geo
		
		#self.view.Check(self.view_show_geo.GetId(), bool())
		self.map.update()
		
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
			l.getDcData(self, acc['login'], 'known_planets', d)
		l.start()

	def onUpdate(self, event):
		'download and process info from server'
		import loader
		l = loader.AsyncLoader()
		
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		for acc in config.accounts():
			log.info('requesting user %s info'%(acc['login'],))
			l.getUserInfo(self, acc['login'], out_dir)
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
		for act in db.proto_actions(['proto_id=%s'%(unit['class'],)]):
			if act['type']== request.RequestMaker.GEO_EXPLORE:
				return True
		return False
	
	def is_geo_scout_fleet(self, turn, fleet_id):
		for u in db.units(turn, ['fleet_id=%s'%(fleet_id,)]):
			if self.is_geo_scout(u):
				return True
		return False
	
	def get_unit_range(self, unit):
		for proto in db.prototypes(['id=%s'%(unit['class'],)]):
			return float(proto['fly_range'])

	def onSendScouts(self, _):
		turn = db.getTurn()
		min_size = 70
		
		friend_geo_scout_ids = []
		for user in db.users():
			friend_geo_scout_ids.append(str(user['id']))
		
		for acc in config.accounts():
			user_id = int(acc['id'])
			self.pending_actions.user_id = user_id
			print 'send scouts %s size %s'%(user_id, min_size)
			
			# find units that can geo-explore
			# find the ones that are already in fleets in one of our planets
			
			fly_range = 0.0
			ready_scout_fleets = {}
			# get all fleets over our planets
			for planet in db.open_planets(user_id):
				print 'open planet %s'%(planet,)
				coord = get_coord(planet)
				for fleet in db.fleets(turn, filter_coord(coord)+['owner_id=%s'%(user_id,)]):
					units = db.get_units(turn, ['fleet_id=%s'%(fleet['id'],)])
					if len(units) != 1:
						continue
					unit = units[0]
					if int(unit['id']) in self.manual_control_units:
						continue

					if not self.is_geo_scout(unit):
						continue
					fly_range = max(fly_range, self.get_unit_range(unit))
					print 'unit %s on planet %s for fleet %s is geo-scout'%(unit, coord, fleet)
					# ok, this is geo-scout, single unit in fleet, on our planet
					#ready_scout_fleets.append((coord, fleet))
					ready_scout_fleets.setdefault(coord, []).append((fleet, fly_range))
					
			
			# get possible planets to explore in nearest distance
			for coord in ready_scout_fleets.keys():
				serialization.load_geo_size_center(coord, 10)
			
			# jump to nearest/biggest unexplored planet
			exclude = set()
			for coord, fleets in ready_scout_fleets.iteritems():
				lt = int(coord[0]-fly_range), int(coord[1]-fly_range)
				
				possible_planets = []
				#s!=11 - skip stars
				for p in db.planets_size(['s>=%s'%(min_size,), 's!=11'] + planet_area_filter( lt, (int(fly_range*2), int(fly_range*2)))):
					dest = get_coord(p)
					if dest in exclude:
						continue
					dist = distance(dest, coord)
					if dist > fly_range:
						continue
						
					planet = db.get_planet(dest)
					if planet and 'o' in planet:
						continue
					
					has_flying_geo_scouts = False
					# get list of all flying fleets ( or our allies and mults ) to this planet 
					for fleet in db.flyingFleets(turn, filter_coord(dest) + ['owner_id in(%s)'%','.join(friend_geo_scout_ids)]):
						# check if the fleet is geo-scout
						if self.is_geo_scout_fleet(turn, fleet['id']):
							has_flying_geo_scouts = True
							print 'found another scout %s, skip planet %s'%(fleet, dest)
					if has_flying_geo_scouts:
						exclude.add(dest)
						continue
					
					#TODO: can check if it will take too long for the other fleet, send ours
					
					possible_planets.append( (dist, dest) )

				for fleet, fleet_range in fleets:
					for dist, planet in sorted(possible_planets):
						if dist > fleet_range:
							continue
						# ok fly to it
						self.pending_actions.fleetMove(fleet['id'], planet)
						exclude.add( planet )
						print 'jump %s from %s to %s'%(fleet, coord, planet)
						possible_planets.remove( (dist, planet ) )
						break
							
			self.perform_actions()

	
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
			user_id = int(acc['id'])
			
			
			#if user_id < 601140:
			#	continue

			units_classes = db.get_units_class(turn, ['carapace=%s'%(carapace,), 'owner_id=%s'%(user_id,)])
			any_class = 'class in (%s)'%(','.join([str(cls) for cls in units_classes]),)
			print 'testing user %s with class %s'%(user_id, any_class)
			
			self.pending_actions.user_id = user_id
			pending_units = []
			
			for planet in db.planets(turn, ['owner_id=%s'%(user_id,)]):
				coord = get_coord(planet)
				print 'checking harrison for planet %s'%(planet,)
				for unit in db.garrison_units(turn, filter_coord(coord) + [any_class]):
					print 'found unit %s on planet %s'%(unit, planet,)
					self.pending_actions.createNewFleet(coord, fleet_name)
					pending_units.append( (self.pending_actions.get_action_id(), coord, unit['id'] ) )
					print 'found unit %s on planet %s'%(unit, coord )
			
			if len(pending_units) == 0:
				continue
			
			self.recv_data_callback[acc['login']] = (self.cb_move_units_to_fleets, user_id, pending_units )
			# exec actions to create fleets on the planets
			self.perform_actions()
			
	def cb_move_units_to_fleets(self, user_id, units):
		
		turn = db.getTurn()
		self.pending_actions.user_id = user_id
		at_least_one = False
		print 'executing move_units_to_fleets with user %s, units %s'%(user_id, units)
		for act_id, coord, unit_id in units:
			print 'action %s, coord %s, unit %s'%(act_id, coord, unit_id)
			# get fleet for these coords
			res = db.get_action_result(act_id)
			if not res:
				print 'oops no result'
				continue
			ret_id, is_ok = res
			print 'result is %s %s'%(ret_id, is_ok)
			if not is_ok:
				continue
			
			at_least_one = True
			print 'moving unit %s to fleet %s'%(unit_id, ret_id)
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
		
		for unit in db.garrison_units(turn, ['x=%s'%(coord[0],), 'y=%s'%(coord[1],), 'class=%s'%(unit_type,)]):
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
				print 'fleet %s can be stopped'%(fleet,)
			
				self.pending_actions.cancelJump(fleet['id'])
			
			self.perform_actions()
				
	def onFlyHomeScouts(self, _):
		turn = db.getTurn()
				
		for acc in config.accounts():
			user_id = int(acc['id'])
			self.pending_actions.user_id = user_id
			print 'fly home scouts for user %s %s'%(user_id, acc['login'])
							
			# fly scouts back to base
			
			fleets = []
			fleet_flt = ['owner_id=%s'%(user_id,)]
			
			fleet_name = None #unicode('Fleet')
			# can also filter fleets by names
			#TODO: beware escapes
			if fleet_name:
				fleet_flt.append( 'name="%s"'%(fleet_name,) ) 
			for fleet in db.fleets(turn, fleet_flt):
				print 'found fleet %s'%(fleet,)
				# if fleet over empty planet - jump back home
				coord = get_coord(fleet)
				planet = db.get_planet( coord )
				if not planet or not planet['owner_id'] or int(planet['owner_id']) != user_id:
					print 'fleet %s not at home'%(fleet['id'],)
					units = []
					for unit in db.units(turn, ['fleet_id=%s'%(fleet['id'],)]):
						print 'fleet %s has unit %s'%(fleet['id'], unit)
						units.append(unit)
					
					# not a scout fleet if more then one unit in fleet
					# if zero units - don't care about empty fleet as well
					if len(units) != 1:
						print 'fleet %s has %s units, while required 1'%(fleet['id'], len(units))
						continue

					if int(units[0]['id']) in self.manual_control_units:
						continue

					proto = db.get_prototype(units[0]['class'])
					if proto['carapace'] != CARAPACE_PROBE:
						print 'fleet %s unit %s is not a probe'%(fleet['id'], units[0])
						continue

					#jump back
					print 'fleet %s %s needs to get home'%(coord, fleet)
					fleets.append( (coord, fleet) )					

			if not fleets:
				print 'no scout fleets found not at home'
				continue
			
			coords = []
			for planet in db.planets(turn, ['owner_id=%s'%(user_id,)]):
				coord = get_coord(planet)
				coords.append( coord )
				print 'possible home planet %s'%(coord,)
				
			if coords == None or fleets == []:
				print 'oops %s %s'%(coords, fleets)
				continue
			
			print 'looking for best route for %s fleets' %(len(fleets,),)
			for coord, fleet in fleets:
				#find closest planet
				closest_planet = coords[0]
				min_distance = distance(coords[0], coord)
				for c in coords:
					if distance(coord, c) < min_distance:
						min_distance = distance(coord, c)
						closest_planet = c
				
				# ok, found then jump
				print 'Jump (%s) %s'%(closest_planet, fleet)
				self.pending_actions.fleetMove( fleet['id'], closest_planet )
			
			self.perform_actions()
		
	# geo explore
	# load known planets
	# 1. rename ( baken )
	# 2. fly somewhere ( closest jumpable )
	# 

	def onExploreGeoAll(self, _):
		'upload pending events on server'
		
		turn = db.getTurn()
		explore_owned_planets = True
		
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		for acc in config.accounts():
			log.info('requesting user %s info'%(acc['login'],))
			# find if there is any explore-capable fleets over unexplored planets
			# or simply tell explore to every unit =))) game server will do the rest
			
			#1. find all fleets above empty planets
			
			# get fleet position, check if planet geo is unknown
			fleet_planet = {}
			pl = {}
			
			for fleet in db.fleets(turn, ['owner_id=%s'%(acc['id'],)] ):
				print 'got fleet %s'%(fleet,)
				coord = get_coord(fleet)
				cfilter = filter_coord(coord)
				for planet in db.planets(turn, cfilter):
					# skip if occupied
					if planet['owner_id'] and not explore_owned_planets:
						continue
					if planet['o'] and planet['e'] and planet['m'] and planet['t']:
						continue
					#check holes and stars
					if not db.is_planet(coord):
						print '%s not a planet'%(coord,)
						continue
					if not coord in pl:
						pl[coord] = set()
					pl[ coord ].add(fleet['id'])
					print 'planet unexplored %s'%(planet,)
			
			acts = {}
			
			# get all fleet units, check if explore capable
			for coord, planet_fleets in pl.iteritems():
				for fleet_id in planet_fleets:
					for unit in db.units(turn, ['fleet_id=%s'%(fleet_id,)]):
						print '%s %s unit %s'%(coord, fleet_id, unit)
						# ok unit
						bc = unit['class']
						
						#for proto in db.prototypes(['id=%s'%(bc,)]):
						#	print 'proto %s'%(proto,)

						#type 1 probably geo explore
						for act in db.proto_actions(['proto_id=%s'%(bc,), 'type=1']):
							#print 'ACTION: %s %s %s'%(coord, bc, act)
							acts[coord] = unit['id']

			self.pending_actions.user_id = int(acc['id'])
			#self.pendingActions[int(acc['id'])] = actions
			#hw_planet = db.getUserHw(acc['id'])
			#actions.createNewFleet(hw_planet, 'a_new_shiny_fleet')
			
			at_least_one = False
			for coord, unit_id in acts.iteritems():
				print 'explore (%s) %s'%(coord, unit_id)
				self.pending_actions.explore_planet( coord, unit_id )
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
	
	def onDownloadRawData(self, evt):
		key = evt.attr1
		data = evt.attr2
		if not key:
			log.info('all requested data downloaded')
			self.log('All requested data downloaded')
			serialization.save()
			return
		if not data:
			log.error('failed to load info for user %s'%(key,))
			self.log('Error: failed to load info for user %s'%(key,))
			return
		
		self.log('Downloaded %s %s'%(key, data))
		status = import_raw.processRawData(data)
		if status != import_raw.XmlHandler.StatusOk:
			status_text = 'Not authorized' if status == import_raw.XmlHandler.StatusAuthError else 'Turn in progress'
			self.log('Error processing %s %s'%(key, status_text))
		
		if key in self.recv_data_callback:
			func, user_id, data = self.recv_data_callback[key]
			del self.recv_data_callback[key]
			func(user_id, data)
			db.clear_action_result(user_id)
		
		self.map.turn = db.db.max_turn
		self.map.update()
		self.object_filter.update()
		self.history.updateTurns(self.map.turn)
		
		self.started = False
		self.perform_next_action()
		
	
	def onSelectUser(self, evt):
		user_id = evt.attr1
		#user_id = int(config.users[login]['id'])
		#self.unit_list.setPlayer( user_id )
		print 'selecting user %s'%(user_id, )
		self.map.selectUser( user_id) 
 
	def onTurnSelected(self, evt):
		turn = evt.attr1
		#only load if db does not know about this turn
		if not turn in db.db.turns or not db.db.turns[turn]:
			serialization.load(turn, self)
		self.map.turn = turn
		self.map.update()
		log.info('update info panel with turn %s'%(self.map.turn,))
		self.info_panel.update(self.map.turn)
