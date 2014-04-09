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
	
def distance(a, b):
	dx = a[0]-b[0]
	dy = a[1]-b[1]
	return math.sqrt( dx * dx + dy * dy ) 

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

		#p = config.options['window']['pane-info']
		#if p:
		#	print 'load p %s'%(p,)
		#	self._mgr.LoadPerspective( p )
		
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
		self.uploadMenu = gameMenu.Append(wx.ID_ANY, "&Geo Explore and fly back")
		usersMenu = gameMenu.Append(wx.ID_ANY, "U&sers")
		routesMenu = gameMenu.Append(wx.ID_ANY, "&Routes")
		
		syncMenu = wx.Menu()
		set_sync_dir = syncMenu.Append(wx.ID_ANY, "Set sync path")
		
		#actionMenu = wx.Menu()
		#actionDefineArea = actionMenu.Append(
		
		panel = wx.MenuBar()
		panel.Append(fileMenu, "&File")
		panel.Append(gameMenu, "G&ame")
		panel.Append(syncMenu, "Sync")
		self.SetMenuBar(panel)
				
		self.Bind(wx.EVT_MENU, self.onUpdate, self.updateMenu)
		self.Bind(wx.EVT_MENU, self.onUpload, self.uploadMenu)
		self.Bind(wx.EVT_MENU, self.onShowUsers, usersMenu)
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
		self.sync_path = config.options['data']['sync_path']
		if not self.sync_path or self.sync_path == '':
			return

		nick = config.options['user']['nick']
		if not nick:
			nick = str(min(config.user_id_dict.keys()))

		acc_path = os.path.join(self.sync_path, 'users')
		if not os.path.exists(acc_path):
			util.assureDirExist(acc_path)
		
		out_acc_p = os.path.join(acc_path, nick)
		outp = os.path.join(out_acc_p, str(db.getTurn()))
		util.assureDirExist(outp)
		pt = os.path.join(config.options['data']['path'], str(db.getTurn()))
		for f in os.listdir(pt):
			util.pack(os.path.join(pt, f), os.path.join(outp, f) )
		
		# read data we don't have
		for acc in os.listdir(acc_path):
			if acc == nick:
				continue
			
			# copy back to us new data
			path = os.path.join(acc_path, acc)
			
			turn = max( [int(d) for d in os.listdir(path) ] )
			turn_path = os.path.join(path, str(turn) )
			out_dir = os.path.join( wx.GetTempDir(), os.path.join('unpack_sync', acc) )
			for gz_file in os.listdir(turn_path):
				outf = os.path.join(out_dir, gz_file)
				util.unpack(os.path.join(turn_path, gz_file), outf)
				serialization.loadExternalTable(outf, turn)
			
		
		# ok now save our data
		
		
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
		
	
	def perform_actions(self):
		if self.pending_actions.is_empty():
			return
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		
		l = loader.AsyncLoader()
		l.sendActions(self, config.user_id_dict[self.pending_actions.user_id]['login'], self.pending_actions, out_dir)
		l.start()
		
		self.pending_actions.clear()
		
	def create_fleet(self, user_id, fleet_name, planet_coord, count = 1):
		
		self.pending_actions.user_id = user_id
		
		for _ in range(0, count):
			self.pending_actions.createNewFleet(coord, fleet_name)
		
		self.perform_actions()
		
	def auto_geo_scout(self, user_id):
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
		
		pass
	
	def harrison_units_to_fleets(self, user_id, coord, unit_type, fleets_ids):
		#TODO: check if fleet empty
		#add fleet new info to local-db
		
		turn = self.db.getTurn()
		self.pending_actions.user_id = user_id
		
		i = 0
		if len(fleet_ids) < 1:
			return
		
		for unit in self.db.garrison_units(turn, ['x=%s'%(coord[0],), 'y=%s'%(coord[1],), 'class=%s'%(unit_type,)]):
			self.pending_actions.moveUnitToFleet(fleet_ids[i], unit['id'])
			i += 1
			if i >= len(fleet_ids):
				break

		self.perform_actions( )		
		
#	def get_planet_fleets(self, coord, fleet_name):
#		for fleet in self.db.fleets(
	
	
	def cancel_jump(self):

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
		
	def send_back(self):
		turn = db.getTurn()
		out_dir = os.path.join(util.getTempDir(), config.options['data']['raw-dir'])
		util.assureDirClean(out_dir)
		
		for acc in config.accounts():
			user_id = int(acc['id'])
			self.pending_actions.user_id = user_id
							
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

					proto = db.get_prototype(units[0]['class'])
					if proto['carapace'] != CARAPACE_PROBE:
						print 'fleet %s unit %s is not a probe'%(fleet['id'], units[0])
						continue

					#jump back
					print 'fleet %s %s needs to get home'%(coord, fleet)
					fleets.append( (coord, fleet) )					

			user_id = int(acc['id'])
			
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

	def explore_all(self):
		'upload pending events on server'
		
		turn = db.getTurn()
		
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
				for planet in db.planets(turn, ['x=%s'%(fleet['x'],), 'y=%s'%(fleet['y'],)]):
					# skip if occupied
					if planet['owner_id']:
						continue
					if not planet['o'] or not planet['e'] or not planet['m'] or not planet['t']:
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
			
			for coord, unit_id in acts.iteritems():
				print 'explore (%s) %s'%(coord, unit_id)
				self.pending_actions.explore_planet( coord, unit_id )
			self.perform_actions()
		
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
		self.map.turn = db.db.max_turn
		self.map.update()
		self.history.updateTurns(self.map.turn)
		
	
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
