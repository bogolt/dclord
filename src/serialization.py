import db
import csv
import config
import os
import os.path
import logging
import util

log = logging.getLogger('dclord')

unicode_strings = ['name', 'description']

def saveTable(table_name, keys, filters, out_name = None, turn_n = None):
	out_file_path = out_name if out_name else table_name
	pt = config.options['data']['path']
	if turn_n:
		pt = os.path.join(pt, str(turn_n))
	util.assureDirExist(pt)
	path = os.path.join(pt, '%s.csv'%(out_file_path,))
	try:
		f = open(path, 'wt')
		writer = csv.DictWriter(f, keys)
		writer.writeheader()
		for p in db.items(table_name, filters, keys):
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
	saveTable('planet', ('x','y','o','e','m','t','s'), None, 'planets_geo')

def saveProto():
	saveTable('proto', ('owner_id', 'fly_speed', 'aim_bomb', 'color', 'build_speed', 'require_people', 'carapace', 'fly_range', 'id', 'class', 'cost_second', 'cost_main', 'cost_money', 'is_transportable', 'require_tech_level', 'support_second', 'name', 'stealth_level', 'bonus_s', 'bonus_m', 'bonus_o', 'max_count', 'bonus_e', 'support_main', 'weight', 'damage_laser', 'is_ground_unit', 'is_serial', 'aim_laser', 'is_spaceship', 'transport_capacity', 'is_offensive', 'detect_range', 'damage_bomb', 'bonus_production', 'description', 'scan_strength', 'hp', 'defence_laser', 'defence_bomb', 'carrier_capacity', 'laser_number', 'is_building', 'cost_people', 'bomb_number', 'is_war'), None, 'prototypes')
	saveTable('proto_action', ('id', 'max_count', "cost_people", "cost_main", "cost_money", "cost_second", "planet_can_be"), None, 'proto_actions')

def savePlanets():
	saveTable('planet', ('x','y','o','e','m','t','s','owner_id', 'name', 'is_open'), ['owner_id is not null'], 'planets', db.getTurn())
	#saveTable('planet', ('x','y','owner_id', 'name', 'is_open'), ['owner_id is not null'], 'planets')

def saveFleets():
	saveTable('fleet', ('id', 'x','y','owner_id', 'is_hidden','turn','name','weight'), None, 'fleets', db.getTurn())
	saveTable('incoming_fleet', ('id', 'x','y','owner_id','from_x','from_y','weight', 'arrival_turn','temp_id', 'is_hidden','turn'), None, 'incoming_fleets', db.getTurn())
		
def saveUnits():
	saveTable('unit', ('id', 'hp','class', 'fleet_id'), [], 'units', db.getTurn())

def saveGarrisonUnits():
	saveTable('garrison_unit', ('id', 'hp','class', 'x', 'y'), [], 'garrison_units', db.getTurn())

def saveAlienUnits():
	saveTable('alien_unit', ('id', 'carapace','color','weight','fleet_id'), [], 'alien_units', db.getTurn())
	
def saveUsers():
	saveTable('user', ('id','name','hw_x','hw_y','race_id'), None, 'users', db.getTurn())

def save():
	saveGeoPlanets()
	savePlanets()
	saveGeoPlanets()
	saveFleets()
	saveUnits()
	saveGarrisonUnits()
	saveAlienUnits()
	saveProto()
	saveUsers()

def loadTable(table_name, file_name, turn_n = None):
	try:
		path = config.options['data']['path']
		if turn_n:
			path = os.path.join(path, turn_n)
		path = os.path.join(path, '%s.csv'%(file_name,))
		for p in csv.DictReader(open(path, 'rt')):
			for s in unicode_strings:
				if s in p and p[s]:
					p[s] = p[s].decode('utf-8')
			db.setData(table_name, p, turn_n)
	except IOError, e:
		log.error('failed to load table %s: %s'%(table_name, e))
		
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

@util.run_once
def loadGeoPlanets():
	for p in loadCsv('planets_geo'):
		db.smartUpdate('planet', ['x=%s'%(p['x'],), 'y=%s'%(p['y'],)], p)
	
def loadPlanets(turn_n = None):
	loadTable('planet', 'planets', turn_n)
	if int(config.options['filter']['inhabited_planets'])==0:
		loadGeoPlanets()

def loadFleets(turn_n = None):
	loadTable('fleet', 'fleets', turn_n)
	loadTable('incoming_fleet', 'incoming_fleets', turn_n)
	
def loadUnits(turn_n = None):
	loadTable('unit', 'units', turn_n)

def loadGarrisonUnits(turn_n = None):
	loadTable('garrison_unit', 'garrison_units', turn_n)

def loadAlienUnits(turn_n = None):
	loadTable('alien_unit', 'alien_units', turn_n)
	
def loadProto(turn_n = None):
	loadTable('proto', 'prototypes')
	loadTable('proto_action', 'proto_actions')
	
def loadUsers(turn_n = None):
	loadTable('user', 'users')
	

def get_turn_number(s):
	try:
		return int(s)
	except:
		return None

def getLastTurn():
	path = config.options['data']['path']
	max_turn = 0
	for pt in os.listdir(path):
		if os.path.isdir(os.path.join(path, pt)):
			turn = get_turn_number(pt)
			if turn:
				db.db.turns[turn] = False
				max_turn = max(max_turn, turn)
	print 'loaded %s turns, max turn is %s'%(len(db.db.turns.keys()), max_turn)
	return max_turn

def load(turn_n = None):
	if not turn_n:
		turn_n = getLastTurn()
	print 'loading turn %s'%(turn_n,)
	if turn_n:
		turn_n = str(turn_n)
	db.prepareTurn(turn_n)
	loadPlanets(turn_n)
	loadFleets(turn_n)
	loadUnits(turn_n)
	loadGarrisonUnits(turn_n)
	loadAlienUnits(turn_n)
	loadProto(turn_n)
	loadUsers(turn_n)

#def asyncLoad():
#	import thread
#	thread.start_new_thread(load, () )
