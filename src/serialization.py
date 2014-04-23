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

def saveTable(table_name, keys, filters, turn_n = None):
	pt = config.options['data']['path']
	pt = os.path.join(pt, str(db.getTurn()))
	util.assureDirExist(pt)
	path = os.path.join(pt, '%s.csv'%(table_name,))
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

def save_table(table, keys):
	pt = config.options['data']['path']
	pt = os.path.join(pt, str(db.db.max_turn))
	util.assureDirExist(pt)
	path = os.path.join(pt, '%s.csv'%(table,))
	if table in db.db.has_turn:
		flt = {'=': {'turn': db.db.max_turn}}
	else:
		flt = {}
		
	try:
		f = open(path, 'wt')
		writer = csv.DictWriter(f, keys)
		writer.writeheader()
		for p in db.db.iter_objects_list(table, flt, keys):
			try:
				for s in unicode_strings:
					if s in p and p[s]:
						p[s] = p[s].encode('utf-8')
				writer.writerow(p)
			except UnicodeEncodeError, e:
				log.error('failed convert data %s - %s'%(p, e))
	except IOError, e:
		log.error('failed writing data to csv file %s: %s'%(path, e))
	

#def saveGeoPlanets():
#	saveTable(db.Db.PLANET, ('x','y','o','e','m','t','s'), None, 'planets_geo', db.getTurn())

def saveProto():
	save_table(db.Db.PROTO, ('owner_id', 'fly_speed', 'aim_bomb', 'color', 'build_speed', 'require_people', 'carapace', 'fly_range', 'id', 'class', 'cost_second', 'cost_main', 'cost_money', 'is_transportable', 'require_tech_level', 'support_second', 'name', 'stealth_level', 'bonus_s', 'bonus_m', 'bonus_o', 'max_count', 'bonus_e', 'support_main', 'weight', 'damage_laser', 'is_ground_unit', 'is_serial', 'aim_laser', 'is_spaceship', 'transport_capacity', 'is_offensive', 'detect_range', 'damage_bomb', 'bonus_production', 'description', 'scan_strength', 'hp', 'defence_laser', 'defence_bomb', 'carrier_capacity', 'laser_number', 'is_building', 'cost_people', 'bomb_number', 'is_war'))
	save_table(db.Db.PROTO_ACTION, ('id', 'type', 'proto_id', 'proto_owner_id', 'max_count', "cost_people", "cost_main", "cost_money", "cost_second", "planet_can_be"))

def savePlanets():
	save_table(db.Db.PLANET, ('x','y','o','e','m','t','s','owner_id', 'name', 'is_open'))
	save_table(db.Db.OPEN_PLANET, ('x','y','user_id'))
	#saveTable('planet', ('x','y','owner_id', 'name', 'is_open'), ['owner_id is not null'], 'planets')

def saveFleets():
	save_table(db.Db.FLEET, ('id', 'x','y','owner_id', 'is_hidden','name','weight'))
	save_table(db.Db.FLYING_FLEET, ('id', 'x','y','in_transit', 'owner_id','from_x','from_y','weight', 'arrival_turn','is_hidden'))
	save_table(db.Db.FLYING_ALIEN_FLEET, ('x','y','user_id','from_x','from_y','weight', 'arrival_turn','is_hidden'))
		
def saveUnits():
	save_table(db.Db.UNIT, ('id', 'hp','class', 'fleet_id'))

def saveGarrisonUnits():
	save_table(db.Db.GARRISON_UNIT, ('id', 'hp','class', 'x', 'y'))

def saveAlienUnits():
	save_table(db.Db.ALIEN_UNIT, ('id', 'carapace','color','weight','fleet_id'))
	
def saveUsers():
	save_table(db.Db.USER, ('id', 'name', 'race_id', 'login'))
	save_table(db.Db.HW, ('hw_x', 'hw_y', 'player_id'))
	save_table(db.Db.RACE, ('id', 'temperature_delta',  'temperature_optimal',  'resource_nature',  'population_growth', 'resource_main', 'resource_secondary', 'modifier_fly', 'modifier_build_war', 'modifier_build_peace', 'modifier_science', 'modifier_stealth', 'modifier_detection', 'modifier_mining', 'modifier_price', 'name'))
	#'modifier_build_ground', 'modifier_build_space',
	
def savePlayers():
	save_table(db.Db.PLAYER, ('player_id', 'name'))

def save():
	log.info('saving data for turn %s'%(db.getTurn(),))
	savePlanets()
	saveFleets()
	saveUnits()
	saveGarrisonUnits()
	saveAlienUnits()
	saveProto()
	saveUsers()
	savePlayers()
	
	save_sync_data()

def get_user_nickname():
	nick = config.options['user']['nick']
	if nick:
		return nick

	# find out first user id ( consider it user nickname )
	min_id = None
	for user in db.users():
		if not user['login'] in config.users:
			continue
		user_id = int(user['id'])
		if not min_id:
			min_id = user_id
			nick = user['name']
		elif user_id < min_id:
			min_id = user_id
			nick = user['name']
	if min_id:
		return nick
	return None
	
def load_sync_data():
	sync_path = config.options['data']['sync_path']
	if not sync_path or sync_path == '':
		print 'sync path not specified, sync not performed'
		return
		
	turns_path = os.path.join(sync_path, 'turns')
	if not os.path.exists(turns_path):
		#print 'sync path %s not exist'%(turns_path,)
		return
	available_turns = []
	for f in os.listdir(turns_path):
		available_turns.append(int(f))
	
	if not available_turns:
		#print 'no sync data found in %s'%(turns_path,)
		return
	
	load_turn = db.getTurn()
	available_turns.sort()

	nick = get_user_nickname()
	
	total_load_turns = 0
	for load_turn in available_turns[::-1]:
		
		total_load_turns += 1
		if total_load_turns > 3:
			break
	
		turn_path = os.path.join(turns_path, str(load_turn))
		for d in os.listdir(turn_path):
			if d == nick:
				continue
			acc_path = os.path.join(turn_path, d)
			#print 'load %s turn: %s'%(d, load_turn)
			db.prepareTurn(load_turn)
			
			# do load
			unpack_dir = os.path.join(os.path.join(os.path.join( util.getTempDir(), 'unpack_sync' ), d), str(load_turn))
			util.assureDirClean(unpack_dir)
			for gz_file in os.listdir(acc_path):
				outf = os.path.join(unpack_dir, gz_file)
				if outf.endswith('.gz'):
					outf = outf[:-len('.gz')]
				util.unpack(os.path.join(acc_path, gz_file), outf)
				table_name = os.path.basename(outf)[:-len('.csv')]
				
				load_table(table_name, load_turn, os.path.dirname(outf))
				
				#if table_name == db.Db.PROTO or table_name == db.Db.PROTO_ACTION or table_name == db.Db.OPEN_PLANET or table_name == db.Db.USER or table_name == db.Db.RACE or table_name == db.Db.PLAYER:
				#	loadTable(table_name, None, load_turn, None, os.path.dirname(outf))
				#else:
				#	loadTable(table_name, load_turn, None, None, os.path.dirname(outf))
				
			

# ~/Dropbox/sync_kingdom_name/turns/47/user_vasya/data.csv.gz
def save_sync_data():
	
	sync_path = config.options['data']['sync_path']
	if not sync_path or sync_path == '':
		print 'sync path not specified, sync not performed'
		return
		
	turns_path = os.path.join(sync_path, 'turns/%s'%(db.getTurn(),))
		
	nick = get_user_nickname()
	if not nick:
		print 'no users found, nothing to save'
		return
	#print 'user nick is %s'%(nick,)
	
	outp = os.path.join(turns_path, nick)
	util.assureDirExist(outp)
		
	pt = os.path.join(config.options['data']['path'], str(db.getTurn()))
	if not os.path.exists(pt):
		return
		
	for f in os.listdir(pt):
		util.pack(os.path.join(pt, f), os.path.join(outp, f+".gz"))

def loadExternalTable(path, turn_n ):
	table = os.path.basename(path)
	#print 'table name %s from path %s'%(table, path)
	try:
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
			db.setData(table, p, turn_n)
	except IOError, e:
		log.error('failed to load table %s: %s'%(table_name, e))


def load_table(table_name, turn, cb = None, external_path = None):
	#if cb:
	#	util.appendLog(cb, 'loading "%s" from turn %s'%(table_name, turn))
	try:

		path = os.path.join(os.path.join(external_path if external_path else config.options['data']['path'], str(turn)), '%s.csv'%(table_name,))
	
		print 'loading %s'%(path,)
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
				
			db.db.smart_update_object(table_name, turn, p)
	except IOError, e:
		#print 'failed to load table %s'%(table_name, )
		log.error('failed to load table %s'%(table_name, ))
		#if cb:
		#	util.appendLog(cb, 'Error loading "%s" from turn %s'%(table_name, turn_n))
	#if cb:
	#	util.appendLog(cb, '"%s" from turn %s loaded'%(table_name, turn_n))
		
def loadTable(table_name, turn_n = None, load_turn = None, cb = None, external_path = None):
	#print 'loading table %s at %s %s from %s'%(table_name, turn_n, load_turn, external_path)
	if cb:
		util.appendLog(cb, 'loading "%s" from turn %s'%(table_name, turn_n))
	try:
		if turn_n:
			load_turn = turn_n

		if external_path:
			path = external_path
		else:
			path = config.options['data']['path']
			if load_turn:
				path = os.path.join(path, str(load_turn))

		path = os.path.join(path, '%s.csv'%(table_name,))
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
			#print 'setting data for table %s %s %s'%(table_name, p, turn_n)
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
		#print 'load all geo sizes from %s'%path
		for p in csv.DictReader(open(path, 'rt')):
			db.set_planet_geo_size(p)
	except IOError, e:
		log.error('failed to load csv %s: %s'%(path, e))

geo_size_loaded = set()
def load_geo_size(path, left_top, size):
	global geo_size_loaded
	if path in geo_size_loaded:
		#print 'no double loading %s'%path
		return
	try:
		#print 'loading geo %s'%path
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
		#print 'loading %s'%(f,)
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
	
	#print 'was %s %s got %s %s'%(x,y, px, py)
	
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
	#print 'get rect %s %s : %s %s'%(px,py, dx, dy)
	
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
	loadTable(db.Db.PLANET, turn_n, cb=cb)
	loadTable(db.Db.OPEN_PLANET, None, turn_n, cb=cb)
	if int(config.options['filter']['inhabited_planets'])==0:
		loadGeoPlanets(turn_n)

def loadFleets(turn_n = None, cb = None):
	loadTable(db.Db.FLEET, turn_n)
	loadTable(db.Db.FLYING_FLEET, turn_n)
	loadTable(db.Db.FLYING_ALIEN_FLEET, turn_n)
	
def loadUnits(turn_n = None, cb = None):
	loadTable(db.Db.UNIT, turn_n, cb=cb)

def loadGarrisonUnits(turn_n = None, cb = None):
	loadTable(db.Db.GARRISON_UNIT, turn_n, cb=cb)

def loadAlienUnits(turn_n = None, cb = None):
	loadTable(db.Db.ALIEN_UNIT, turn_n, cb=cb)
	
def loadProto(turn_n = None, cb = None):
	loadTable(db.Db.PROTO, None, turn_n, cb=cb)
	loadTable(db.Db.PROTO_ACTION, None, turn_n, cb=cb)
	
def loadUsers(turn_n = None, cb = None):
	loadTable(db.Db.USER, None, turn_n, cb=cb)
	loadTable(db.Db.HW, turn_n, cb=cb)
	loadTable(db.Db.RACE, None, turn_n, cb=cb)
	
def loadPlayers(turn_n = None, cb = None):
	loadTable(db.Db.PLAYER, None, turn_n, cb=cb)

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
		#print 'Data path specified "%s" does not exist'%(path,)
		return None
		
	for pt in os.listdir(path):
		if os.path.isdir(os.path.join(path, pt)):
			turn = get_turn_number(pt)
			if turn:
				db.db.turns[turn] = False
				max_turn = max(max_turn, turn)
	#print 'loaded %s turns, max turn is %s'%(len(db.db.turns.keys()), max_turn)
	if cb:
		util.appendLog(cb, 'loaded %d turns, max turn is %d'%(len(db.db.turns.keys()), max_turn))
	return max_turn

def load(turn_n = None, ev_cb = None):
	#TODO: make async ( other thread )
	load_sync_data()
	
	if not turn_n:
		turn_n = getLastTurn(ev_cb)
		if not turn_n:
			return
	#print 'loading turn %s'%(turn_n,)
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
	
	save_sync_data()

#def asyncLoad():
#	import thread
#	thread.start_new_thread(load, () )
