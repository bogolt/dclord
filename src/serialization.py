import db
import csv
import config
import os
import os.path
import logging
import util
import wx

log = logging.getLogger('dclord')

unicode_strings = ['name', 'description']

def saveTable(table_name, keys, filters, out_name = None, turn_n = None):
	out_file_path = out_name if out_name else table_name
	pt = config.options['data']['path']
	pt = os.path.join(pt, str(db.getTurn()))
	util.assureDirExist(pt)
	path = os.path.join(pt, '%s.csv'%(out_file_path,))
	try:
		f = open(path, 'wt')
		writer = csv.DictWriter(f, keys)
		writer.writeheader()
		for p in db.items(table_name, filters, keys, turn_n):
			try:
				for s in unicode_strings:
					if s in p and p[s]:
						p[s] = p[s].encode('utf-8')
				writer.writerow(p)
			except UnicodeEncodeError, e:
				log.error('failed convert data %s - %s'%(p, e))
	except IOError, e:
		log.error('failed writing data to csv file %s: %s'%(path, e))

def saveGeoPlanets():
	saveTable('planet', ('x','y','o','e','m','t','s'), None, 'planets_geo', db.getTurn())

def saveProto():
	saveTable('proto', ('owner_id', 'fly_speed', 'aim_bomb', 'color', 'build_speed', 'require_people', 'carapace', 'fly_range', 'id', 'class', 'cost_second', 'cost_main', 'cost_money', 'is_transportable', 'require_tech_level', 'support_second', 'name', 'stealth_level', 'bonus_s', 'bonus_m', 'bonus_o', 'max_count', 'bonus_e', 'support_main', 'weight', 'damage_laser', 'is_ground_unit', 'is_serial', 'aim_laser', 'is_spaceship', 'transport_capacity', 'is_offensive', 'detect_range', 'damage_bomb', 'bonus_production', 'description', 'scan_strength', 'hp', 'defence_laser', 'defence_bomb', 'carrier_capacity', 'laser_number', 'is_building', 'cost_people', 'bomb_number', 'is_war'), None, 'prototypes')
	saveTable('proto_action', ('id', 'type', 'proto_id', 'proto_owner_id', 'max_count', "cost_people", "cost_main", "cost_money", "cost_second", "planet_can_be"), None, 'proto_actions')

def savePlanets():
	saveTable('planet', ('x','y','o','e','m','t','s','owner_id', 'name', 'is_open'), ['owner_id is not null'], 'planets', db.getTurn())
	saveTable('open_planets', ('x','y','user_id'), [], 'open_planets', None)
	#saveTable('planet', ('x','y','owner_id', 'name', 'is_open'), ['owner_id is not null'], 'planets')

def saveFleets():
	saveTable(db.Db.FLEET, ('id', 'x','y','owner_id', 'is_hidden','name','weight'), None, 'fleets', db.getTurn())
	saveTable(db.Db.FLYING_FLEET, ('id', 'x','y','in_transit', 'owner_id','from_x','from_y','weight', 'arrival_turn','is_hidden'), None, 'flying_fleets', db.getTurn())
	saveTable(db.Db.FLYING_ALIEN_FLEET, ('x','y','user_id','from_x','from_y','weight', 'arrival_turn','is_hidden'), None, 'flying_alien_fleets', db.getTurn())
		
def saveUnits():
	saveTable('unit', ('id', 'hp','class', 'fleet_id'), [], 'units', db.getTurn())

def saveGarrisonUnits():
	saveTable('garrison_unit', ('id', 'hp','class', 'x', 'y'), [], 'garrison_units', db.getTurn())

def saveAlienUnits():
	saveTable('alien_unit', ('id', 'carapace','color','weight','fleet_id'), [], 'alien_units', db.getTurn())
	
def saveUsers():
	saveTable('user', ('id', 'name', 'race_id'), None, 'users')
	saveTable('hw', ('hw_x', 'hw_y', 'player_id'), None, 'hw', db.getTurn())
	
def savePlayers():
	saveTable('player', ('player_id', 'name'), None, 'players', db.getTurn())

def save():
	log.info('saving data for turn %s'%(db.getTurn(),))
	saveGeoPlanets()
	savePlanets()
	saveGeoPlanets()
	saveFleets()
	saveUnits()
	saveGarrisonUnits()
	saveAlienUnits()
	saveProto()
	saveUsers()
	savePlayers()
	
	#save_sync_data()

def load_sync_data():
	sync_path = config.options['data']['sync_path']
	if not sync_path or sync_path == '':
		return

	acc_path = os.path.join(sync_path, 'users')
	if not os.path.exists(acc_path):
		util.assureDirExist(acc_path)
			
	# read data we don't have
	
	nick = config.options['user']['nick']
	if not nick:
		nick = str(min(config.user_id_dict.keys()))
		
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
			loadExternalTable(outf, turn)	
				
def save_sync_data():
	
	sync_path = config.options['data']['sync_path']
	if not sync_path or sync_path == '':
		return
		
	nick = config.options['user']['nick']
	if not nick and config.user_id_dict != {}:
		nick = str(min(config.user_id_dict.keys()))
		
	acc_path = os.path.join(sync_path, 'users')
	if not os.path.exists(acc_path):
		util.assureDirExist(acc_path)

	out_acc_p = os.path.join(acc_path, nick)
	outp = os.path.join(out_acc_p, str(db.getTurn()))
	util.assureDirExist(outp)
	pt = os.path.join(config.options['data']['path'], str(db.getTurn()))
	for f in os.listdir(pt):
		util.pack(os.path.join(pt, f), os.path.join(outp, os.path.join(f, ".gz") ))

def loadExternalTable(path, turn_n ):
	try:
		table = os.path.basename(path)
		for p in csv.DictReader(open(path, 'rt')):
			for s in unicode_strings:
				if s in p and p[s]:
					p[s] = p[s].decode('utf-8')
			db.setData(table, p, turn_n)
	except IOError, e:
		log.error('failed to load table %s: %s'%(table_name, e))
		if cb:
			util.appendLog(cb, 'Error loading "%s" from turn %s'%(table_name, turn_n))	

def loadTable(table_name, file_name, turn_n = None, load_turn = None, cb = None):
	if cb:
		util.appendLog(cb, 'loading "%s" from turn %s'%(table_name, turn_n))
	try:
		path = config.options['data']['path']
		if turn_n:
			load_turn = turn_n
		if load_turn:
			path = os.path.join(path, load_turn)
		path = os.path.join(path, '%s.csv'%(file_name,))
		for p in csv.DictReader(open(path, 'rt')):
			for s in unicode_strings:
				if s in p and p[s]:
					p[s] = p[s].decode('utf-8')
			todel = []
			for k,v in p.iteritems():
				if v == '' or v==unicode(''):
					todel.append(k)
			for td in todel:
				del p[td]
			db.setData(table_name, p, turn_n)
	except IOError, e:
		log.error('failed to load table %s: %s'%(table_name, e))
		if cb:
			util.appendLog(cb, 'Error loading "%s" from turn %s'%(table_name, turn_n))
		return
	if cb:
		util.appendLog(cb, '"%s" from turn %s loaded'%(table_name, turn_n))

		
def loadCsv(file_name, turn_n = None):
	path = config.options['data']['path']
	if turn_n:
		path = os.path.join(path, str(turn_n))
	log.info('loading %s for %s turn'%(file_name, 'current' if turn_n else turn_n))
	try:
		path = os.path.join(path, '%s.csv'%(file_name,))
		for p in csv.DictReader(open(path, 'rt')):
			for s in unicode_strings:
				if s in p and p[s]:
					p[s] = p[s].decode('utf-8')
			yield p
	except IOError, e:
		log.error('failed to load csv %s: %s'%(file_name, e))	
	log.info('loading %s done'%(file_name,))

def in_rect(coord, left_top, size):
	if coord[0] < left_top[0]:
		return False
	if coord[1] < left_top[1]:
		return False
		
	if coord[0] > left_top[0] + size[0]:
		return False

	if coord[1] > left_top[1] + size[1]:
		return False
	return True

def load_geo_size_all(path):
	try:
		print 'load all geo sizes from %s'%path
		for p in csv.DictReader(open(path, 'rt')):
			db.set_planet_geo_size(p)
	except IOError, e:
		log.error('failed to load csv %s: %s'%(path, e))

geo_size_loaded = set()
def load_geo_size(path, left_top, size):
	global geo_size_loaded
	if path in geo_size_loaded:
		print 'no double loading %s'%path
		return
	try:
		print 'loading geo %s'%path
		for p in csv.DictReader(open(path, 'rt')):
			x=int(p['x'])
			y=int(p['y'])
			img = int(p['img'])
			s = int(p['s'])
			
			#skip holes
			if img >= 90:
				continue
			
			#skip stars
			#if s == 11:
			#	continue
			#if in_rect( (x,y), left_top, size):
			db.set_planet_geo_size(p)
		
		geo_size_loaded.add(path)
	except IOError, e:
		log.error('failed to load csv %s: %s'%(path, e))		

def load_all_visible_geo(path ):
	for f in os.listdir(path):
		print 'loading %s'%(f,)
		try:
			for p in csv.DictReader(open(os.path.join(path,f), 'rt')):
				for s in unicode_strings:
					if s in p and p[s]:
						p[s] = p[s].decode('utf-8')
				db.setData('planet_size', p, None)
				yield p
		except IOError, e:
			log.error('failed to load csv %s: %s'%(path, e))	

def get_coord_point_left(v):
	v_0 = (v / 10) * 10
	v100 = (v_0 / 100) * 100
	v10 = v_0 - v100
	
	return v100 + (0 if v10 < 50 else 50 )

def get_coord_point_right(v):
	return get_coord_point_left(v) + 50

def load_geo_size_rect(left_top, size):
	x,y = left_top
	step = 25
	
	px = (x-x%step) if x >= step else 0
	py = (y-y%step) if y >= step else 0
	
	print 'was %s %s got %s %s'%(x,y, px, py)
	
	lx = x + size[0]
	ly = y + size[0]

	dx = (lx-lx%step) if lx >= step else 0
	dy = (ly-ly%step) if ly >= step else 0
	
	if px == dx:
		dx += step
	
	if py == dy:
		dy += step
	
	path = config.options['data']['geo-size']
	x = px
	y = py
	print 'get rect %s %s : %s %s'%(px,py, dx, dy)
	
	for x in range(px, dx+step, step):
		for y in range(py, dy+step, step):
			load_geo_size( os.path.join(path, '%s_%s.csv'%(x, y)), left_top, size )

def load_geo_size_center(center, dist):
	x,y = center
	load_geo_size_rect((x-dist, y-dist), (dist*2,dist*2))

def load_geo_size_at(center):
	x,y = center
	
	step = 25
	
	px = (x-x%step) if x >= step else 0
	py = (y-y%step) if y >= step else 0
	path = config.options['data']['geo-size']
	load_geo_size( os.path.join(path, '%s_%s.csv'%(px, py)), (x,y), (x,y) )

@util.run_once
def loadGeoPlanets(turn_n = None, cb = None):
	#for p in load_all_visible_geo(os.path.join(config.options['data']['path'], 'geo_size')):
	#	db.smartUpdate('planet', ['x=%s'%(p['x'],), 'y=%s'%(p['y'],)], p, turn_n)
	
	for p in loadCsv('planets_geo', turn_n):
		db.smartUpdate('planet', ['x=%s'%(p['x'],), 'y=%s'%(p['y'],)], p, turn_n)
	
def loadPlanets(turn_n = None, cb = None):
	loadTable('planet', 'planets', turn_n, cb=cb)
	loadTable('open_planets', 'open_planets', None, turn_n, cb=cb)
	if int(config.options['filter']['inhabited_planets'])==0:
		loadGeoPlanets(turn_n)

def loadFleets(turn_n = None, cb = None):
	loadTable('fleet', 'fleets', turn_n)
	loadTable(db.Db.FLYING_FLEET, 'flying_fleets', turn_n)
	loadTable(db.Db.FLYING_ALIEN_FLEET, 'flying_alien_fleets', turn_n)
	
def loadUnits(turn_n = None, cb = None):
	loadTable('unit', 'units', turn_n, cb=cb)

def loadGarrisonUnits(turn_n = None, cb = None):
	loadTable('garrison_unit', 'garrison_units', turn_n, cb=cb)

def loadAlienUnits(turn_n = None, cb = None):
	loadTable('alien_unit', 'alien_units', turn_n, cb=cb)
	
def loadProto(turn_n = None, cb = None):
	loadTable('proto', 'prototypes', None, turn_n, cb=cb)
	loadTable('proto_action', 'proto_actions', None, turn_n, cb=cb)
	
def loadUsers(turn_n = None, cb = None):
	loadTable('user', 'users', None, turn_n, cb=cb)
	loadTable('hw', 'hw', turn_n, cb=cb)
	
def loadPlayers(turn_n = None, cb = None):
	loadTable('player', 'players', turn_n, cb=cb)

def get_turn_number(s):
	try:
		return int(s)
	except:
		return None

def getLastTurn(cb = None):
	path = config.options['data']['path']
	max_turn = 0
	if not os.path.exists(path):
		if cb:
			util.appendLog(cb, 'Data path specified "%s" does not exist'%(path,))
		return None
		
	for pt in os.listdir(path):
		if os.path.isdir(os.path.join(path, pt)):
			turn = get_turn_number(pt)
			if turn:
				db.db.turns[turn] = False
				max_turn = max(max_turn, turn)
	print 'loaded %s turns, max turn is %s'%(len(db.db.turns.keys()), max_turn)
	if cb:
		util.appendLog(cb, 'loaded %d turns, max turn is %d'%(len(db.db.turns.keys()), max_turn))
	return max_turn

def load(turn_n = None, ev_cb = None):
	#TODO: make async ( other thread )
	if not turn_n:
		turn_n = getLastTurn(ev_cb)
		if not turn_n:
			return
	print 'loading turn %s'%(turn_n,)
	if turn_n:
		turn_n = str(turn_n)
		
	if ev_cb:
		util.appendLog(ev_cb, 'loading %s turn'%(turn_n,))
	db.prepareTurn(turn_n)

	loadPlanets(turn_n, ev_cb)
	loadFleets(turn_n, ev_cb)
	loadUnits(turn_n, ev_cb)
	loadGarrisonUnits(turn_n, ev_cb)
	loadAlienUnits(turn_n, ev_cb)
	loadProto(turn_n, ev_cb)
	loadUsers(turn_n, ev_cb)
	loadPlayers(turn_n, ev_cb)

#def asyncLoad():
#	import thread
#	thread.start_new_thread(load, () )
