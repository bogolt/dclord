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

def save_table(table, keys):
	pt = config.options['data']['path']
	pt = os.path.join(pt, str(db.db.max_turn))
	util.assureDirExist(pt)
	path = os.path.join(pt, '%s.csv'%(table,))
	#if table in db.db.has_turn:
	#	flt = {'=': {'turn': db.db.max_turn}}
	#else:
	#	flt = {}
		
	try:
		f = open(path, 'wt')
		writer = csv.DictWriter(f, keys)
		writer.writeheader()
		for p in db.db.iter_objects_list(table):
			try:
				for s in unicode_strings:
					if s in p and p[s]:
						p[s] = p[s].encode('utf-8')
				writer.writerow(p)
			except UnicodeEncodeError, e:
				log.error('failed convert data %s - %s'%(p, e))
	except IOError, e:
		log.error('failed writing data to csv file %s: %s'%(path, e))
	

def save():
	log.info('saving data for turn %s'%(db.getTurn(),))
	
	for table, keys in db.Db.table_keys.iteritems():
		save_table(table, keys)

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


def load_table(table_name, turn, external_path = None):
	#if cb:
	#	util.appendLog(cb, 'loading "%s" from turn %s'%(table_name, turn))
	try:
		p = external_path
		if not p:
			p = os.path.join(config.options['data']['path'], str(turn))
		path = os.path.join(p, '%s.csv'%(table_name,))
	
		print 'load_table %s'%(path,)
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
			
			if 'turn' in p:
				t = int(p['turn'])
			else:
				t = turn
			
			db.db.smart_update_object(table_name, t, p)
	except IOError, e:
		#print e
		#print 'failed to load table %s %s'%(table_name, unicode(e).decode('utf-8'))
		try:
			log.error('failed to load table %s: %s'%(table_name, e))
		except:
			pass
		#if cb:
		#	util.appendLog(cb, 'Error loading "%s" from turn %s'%(table_name, turn_n))
	#if cb:
	#	util.appendLog(cb, '"%s" from turn %s loaded'%(table_name, turn_n))
		
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
	db.db.max_turn = max_turn
	if cb:
		util.appendLog(cb, 'loaded %d turns, max turn is %d'%(len(db.db.turns.keys()), max_turn))
	return max_turn

def load(turn_n = None, ev_cb = None):
	#TODO: make async ( other thread )
	
	turn = getLastTurn(ev_cb)
	for table, keys in db.Db.table_keys.iteritems():
		load_table(table, turn)

	load_sync_data()
