from store import store
import csv
import os
import logging
import util
import config

unicode_strings = [u'name', u'description']
#last_sync = {}

def csv_open(path, keys):
	writer = csv.DictWriter(open(path, 'wt'), fieldnames=keys)
	writer.writeheader()
	return writer

def save_csv(path, data):
	if not data or data == {}:
		return
		
	writer = csv_open(path, data[0].keys())
	for p in data:
		writer.writerow({k:(v.encode('utf8') if (k in unicode_strings and v) else v) for k,v in p.items()})
	#last_sync[path] = os.stat(path).st_mtime
		
def save_csv_table(path, table, data_filter):
	writer = None
	f = os.path.join(path, '%s.csv'%(table,))
	for p in store.iter_objects_list(table, data_filter):
		if not writer:
			writer = csv_open(f, p.keys())
		writer.writerow({k:(v.encode('utf8') if (k in unicode_strings and v) else v) for k,v in p.items()})
		
	#last_sync[f] = os.stat(f).st_mtime
		
def load_csv_table(path, table):
	try:
		f = os.path.join(path, '%s.csv'%(table,))
		#last_sync[f] = os.stat(f).st_mtime
		for p in csv.DictReader(open(f, 'rt')):
			store.add_data(table, {k:(v.decode('utf8') if (k in unicode_strings and v) else v) for k,v in p.items()})
	except OSError as e:
		print 'Load csv table %s %s failed: %s'%(path, table, e)
	except IOError as e:
		print 'Load csv table %s %s failed: %s'%(path, table, e)
		
def iter_csv_table(path, table):
	try:
		f = os.path.join(path, '%s.csv'%(table,))
		#last_sync[f] = os.stat(f).st_mtime
		for p in csv.DictReader(open(f, 'rt')):
			yield {k:(v.decode('utf8') if (k in unicode_strings and v) else v) for k,v in p.items()}
	except OSError as e:
		print 'Load csv table %s %s failed: %s'%(path, table, e)	
	except IOError as e:
		print 'Load csv table %s %s failed: %s'%(path, table, e)
		
def iter_csv(path):
	objs = []
	#last_sync[path] = os.stat(path).st_mtime
	for p in csv.DictReader(open(path, 'rt')):
		yield {k:(v.decode('utf8') if (k in unicode_strings and v) else v) for k,v in p.items()}
			
def load_csv(path):
	objs = []
	for p in iter_csv(path):
		objs.append(p)
	return objs

def save_user_data(user_id, path):
	util.assureDirExist(path)
	
	user_filter = {'user_id':user_id}
	save_csv_table(path, 'user', user_filter)
	save_csv_table(path, 'open_planet', user_filter)
	save_csv_table(path, 'race', user_filter)
	save_csv_table(path, 'diplomacy', user_filter)
	save_csv_table(path, 'hw', user_filter)

	save_csv_table(path, 'flying_fleet', user_filter)
	save_csv_table(path, 'flying_alien_fleet', user_filter)
	save_csv_table(path, 'user_planet', user_filter)
	save_csv_table(path, 'fleet', user_filter)
	save_csv_table(path, 'proto', user_filter)
	
	fleet_unit_writer = csv_open( os.path.join(path, 'fleet_unit.csv'), store.keys('fleet_unit'))
	unit_writer = csv_open( os.path.join(path, 'unit.csv'), store.keys('unit'))
	for fleet in store.iter_objects_list('fleet', {'user_id':user_id}):
		for fleet_unit in store.iter_objects_list('fleet_unit', {'fleet_id':fleet['fleet_id']}):
			fleet_unit_writer.writerow(fleet_unit)
			unit_writer.writerow( store.get_object('unit', {'unit_id':fleet_unit['unit_id']}) )
			
	garrison_unit_writer = csv_open(os.path.join(path, 'garrison_unit.csv'), store.keys('garrison_unit'))
	garrison_queue_unit_writer = csv_open(os.path.join(path, 'garrison_queue_unit.csv'), store.keys('garrison_queue_unit'))
	#save_csv_table(path, 'garrison_queue_unit')
	for planet in store.iter_objects_list('user_planet', {'user_id':user_id}):
		for garrison_unit in store.iter_objects_list('garrison_unit', {'x':planet['x'], 'y':planet['y']}):
			garrison_unit_writer.writerow(garrison_unit)
			unit_writer.writerow( store.get_object('unit', {'unit_id':garrison_unit['unit_id']}) )
			
		for queue_unit in store.iter_objects_list('garrison_queue_unit', {'x':planet['x'], 'y':planet['y']}):
			garrison_queue_unit_writer.writerow( queue_unit )
	
	proto_actions_writer = csv_open(os.path.join(path, 'proto_action.csv'), store.keys('proto_action'))
	for proto in store.iter_objects_list('proto', {'user_id':user_id}):
		proto_actions_writer.writerows(store.get_objects_list('proto_action', {'proto_id':proto['proto_id']}))
	
def save_common_data(path):
	util.assureDirExist(path)
	
	save_csv_table(path, 'user', {})
	save_csv_table(path, 'planet', {})
	save_csv_table(path, 'planet_geo', {})
	save_csv_table(path, 'alien_fleet', {})
	save_csv_table(path, 'alien_unit', {})
	
def is_updated(path):
	global last_sync
	for filename in os.listdir(path):
		f = os.path.join(path, filename)
		if not f in last_sync:
			return True
		if last_sync[f] != os.stat(f).st_mtime:
			return True
	return False
	
#def sync_common_data(path):
#	if is_updated(path):
#		load_common_data(path)
#	save_common_data(path)
	
def save_local_data():
	save_data(config.options['data']['path'])
	
	if config.options['data']['sync_path']:
		save_data(os.path.join(config.options['data']['sync_path'], config.options['data']['sync_key']))
	
def save_data(path):
	save_common_data(os.path.join(path, 'common'))
	
	user_base_path = os.path.join(path, 'users')
	for user in store.iter_objects_list('user'):
		if user['login'] and config.has_user(user['login']):
			save_user_data(user['user_id'], os.path.join(user_base_path, user['name']))
	
def load_user_data(path):
	for user in iter_csv_table(path, 'user'):
		print 'load user %s'%(user,)
		turn = int(user['turn'])
		store_user = store.get_user(user['user_id'])
		if store_user and 'turn' in store_user:
			store_user_turn = store_user['turn']
			if store_user_turn and int(store_user_turn) >= turn:
				print 'User %s already exist in db, actual db turn info %s'%(store_user['name'], store_user_turn)
				continue
		store.add_user(user)
	
		# no need to make it on this level, as there should be only one user
		store.clear_user_data(user['user_id'])
		
		load_csv_table(path, 'open_planet')
		load_csv_table(path, 'race')
		load_csv_table(path, 'diplomacy')
		load_csv_table(path, 'hw')

		load_csv_table(path, 'flying_fleet')
		load_csv_table(path, 'flying_alien_fleet')
		load_csv_table(path, 'user_planet')
		load_csv_table(path, 'fleet')
		load_csv_table(path, 'proto')
		
		load_csv_table(path, 'proto_action')
		load_csv_table(path, 'fleet_unit')
		load_csv_table(path, 'garrison_unit')
		load_csv_table(path, 'garrison_queue_unit')
		
		load_csv_table(path, 'unit')
		load_csv_table(path, 'proto_action')
		
		store.normalize_user_fleets(user['user_id'])
		

geo_size_loaded = set()
def load_geo_size(path, left_top, size):
	global geo_size_loaded
	if path in geo_size_loaded:
		#print 'no double loading %s'%path
		return
	try:
		#print 'loading geo %s'%path
		for p in csv.DictReader(open(path, 'rt')):
			#x=int(p['x'])
			#y=int(p['y'])
			img = int(p['img'])
			s = int(p['s'])
			
			#skip holes
			if img >= 90:
				continue
			
			#skip stars
			#if s == 11:
			#	continue
			#if in_rect( (x,y), left_top, size):
			store.add_planet_size(p)
		
		geo_size_loaded.add(path)
	except IOError, e:
		log.error('failed to load geo size csv %s: %s'%(path, e))		

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
	

def load_common_data(path):	

	for data in iter_csv_table(path, 'user'):
		# it will not load user specific info otherwise
		data['turn'] = '0'
		store.update_data('user', ['user_id'], data)
		
	for data in iter_csv_table(path, 'planet'):
		store.update_data('planet', ['x', 'y'], data)

	for data in iter_csv_table(path, 'alien_fleet'):
		store.update_data('alien_fleet', ['fleet_id'], data)
	
	store.normalize_fleets()
		
	load_csv_table(path, 'planet_geo')
	load_csv_table(path, 'alien_unit')
	
	for planet in store.iter_objects_list('planet'):
		load_geo_size_at((int(planet['x']), int(planet['y'])))
	
def load_local_data():
	load_data(config.options['data']['path'])

	if config.options['data']['sync_path']:
		if os.path.exists(config.options['data']['sync_path']):
			for f in os.listdir(config.options['data']['sync_path']):
				if f == config.options['data']['sync_key']:
					continue
				load_data(os.path.join(os.path.join(config.options['data']['sync_path'], f)))

def load_data(path):
	
	user_base_path = os.path.join(path, 'users')
	if os.path.exists(user_base_path):
		for p in os.listdir(user_base_path):
			load_user_data(os.path.join(user_base_path, p))

	load_common_data(os.path.join(path, 'common'))
	
import unittest
class TestSaveLoad(unittest.TestCase):
	def setUp(self):
		pass
	
	def test_load_save(self):
		user_id = 3
		user_data = {'user_id':user_id, 'race_id':22, 'name':u'test_user', 'turn':33}
		store.add_user(user_data)
		
		save_user_data(user_id, '/tmp/test')
		
if __name__ == '__main__':
	unittest.main()

