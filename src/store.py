# -*- coding: utf-8 -*-
import sqlite3
import logging
import sys, traceback
import util
import math

def to_pos(a,b):
	return int(a),int(b)
	
def to_str_list(lst):
	return [str(x) for x in lst]


log = logging.getLogger('dclord')

tables = {'planet':['x', 'y', 'o','e','m','t','s', 'user_id', 'name', 'turn'],
		'planet_size':['x','y','image','s'],
		'open_planet':['x','y','user_id'], #open planets for specified user-id
		'user_planet':['x','y','user_id', 'corruption', 'population', 'is_open'],
		'fleet':['x','y','user_id','fleet_id','name', 'times_spotted', 'is_hidden'],
		'alien_fleet':['x','y','user_id','fleet_id','name', 'is_hidden', 'turn'],
		'flying_fleet':['x','y','user_id','fleet_id','name', 'from_x', 'from_y', 'arrival_turn', 'in_transit'],
		'alien_flying_fleet':['x','y','user_id','from_x', 'from_y', 'arrival_turn', 'weight'], #user_id who spot fleet, no primary key, no fleet user owner
		'unit':['unit_id', 'hp', 'proto_id'],
		'fleet_unit':['unit_id', 'fleet_id'],
		'garrison_unit':['unit_id', 'x', 'y'],
		'garrison_queue_unit':['unit_id', 'x', 'y', 'proto_id', 'done', 'build_order'],
		'alien_unit':['fleet_id', 'unit_id', 'class', 'weight', 'carapace','color'],
		'user':['user_id', 'name', 'race_id', 'login', 'resource_main', 'resource_secondary', 'money', 'turn'],
		'race':['race_id', 'user_id', 'temperature_delta',  'temperature_optimal',  'resource_nature',  'population_growth', 'resource_main', 'resource_secondary', 'modifier_fly', 'modifier_build_war', 'modifier_build_peace', 'modifier_science', 'modifier_stealth', 'modifier_detection', 'modifier_mining', 'modifier_price', 'name'],
		'diplomacy':['user_id', 'other_user_id', 'relation'], #dip relation from user to other_user
		'proto':['proto_id', 'user_id', 'fly_speed', 'aim_bomb', 'color', 'build_speed', 'require_people', 'carapace', 'fly_range', 'class', 'cost_second', 'cost_main', 'cost_money', 'is_transportable', 'require_tech_level', 'support_second', 'name', 'stealth_level', 'bonus_s', 'bonus_m', 'bonus_o', 'max_count', 'bonus_e', 'support_main', 'weight', 'damage_laser', 'is_ground_unit', 'is_serial', 'aim_laser', 'is_spaceship', 'transport_capacity', 'is_offensive', 'detect_range', 'damage_bomb', 'bonus_production', 'description', 'scan_strength', 'hp', 'defence_laser', 'defence_bomb', 'carrier_capacity', 'laser_number', 'is_building', 'cost_people', 'bomb_number', 'is_war'],
		'proto_action':['proto_action_id', 'proto_id', 'max_count', "cost_people", "cost_main", "cost_money", "cost_second", "planet_can_be"],
		'hw':['x','y', 'user_id'],
		'action':['x','y','user_id','action_type','unit_id','cancel_id','fleet_id']
}

DIP_RELATION_UNSPECIFIED = -1
DIP_RELATION_ENEMY = 0
DIP_RELATION_NEUTRAL = 1
DIP_RELATION_ALLY = 2
DIP_RELATION_VASSAL = 3
DIP_RELATION_LORD = 4

def extract(d, key_list):
	r = {}
	for key, value in d.items():
		if key in key_list:
			r[key] = value
	return r

class Store:
	def __init__(self):
		self.conn = sqlite3.connect(':memory:')
		self.create_tables()
		self.create_fleet_id = -1
	
	def create_tables(self):
		cur = self.conn.cursor()
		cur.execute("""create table if not exists user(
				user_id integer PRIMARY KEY,
				name text not null,
				race_id integer,
				login text,
				resource_main integer,
				resource_secondary integer,
				money integer,
				turn integer default 0
				)""")
				
		# each user may have it's own list of open planets ( consider Mobile Portal here )
		cur.execute("""create table if not exists open_planet(
				x integer(2) not null,
				y integer(2) not null,
				user_id integer not null,
				PRIMARY KEY (x, y, user_id))""")
				
		cur.execute("""create table if not exists race(
				race_id integer PRIMARY KEY,
				user_id integer not null,
				resource_nature integer(1) not null,
				resource_main integer(1) not null,
				resource_secondary integer(1) not null,
				
				temperature_optimal real,
				temperature_delta real,
				
				population_growth real,
				modifier_fly real,
				modifier_build_war real,
				modifier_build_peace real,
				modifier_science real,
				modifier_stealth real,
				modifier_detection real,
				modifier_mining real,
				modifier_price real,
				name text
				)""")
				
#				modifier_build_ground real,
#				modifier_build_space real,

		cur.execute("""create table if not exists planet_size(
				x integer(2) not null,
				y integer(2) not null,
				s integer(1),
				image integer(1),
				PRIMARY KEY (x, y))""")
		
		cur.execute("""create table if not exists requested_action(
				action_id integer PRIMARY KEY,
				user_id integer not null,
				return_id integer default 0,
				is_ok integer default 0
				)""")

		cur.execute("""create table if not exists planet(
				x integer(2) not null,
				y integer(2) not null,
				o integer(1),
				e integer(1),
				m integer(1),
				t integer(1),
				s integer(1),
				user_id integer,
				name text,
				turn integer default 0,
				PRIMARY KEY (x, y))""")

		cur.execute("""create table if not exists planet_geo(
				x integer(2) not null,
				y integer(2) not null,
				o integer(1),
				e integer(1),
				m integer(1),
				t integer(1),
				s integer(1),
				PRIMARY KEY (x, y))""")

		cur.execute("""create table if not exists user_planet(
				x integer(2) not null,
				y integer(2) not null,
				corruption integer(1),
				population integer,
				user_id integer,
				is_open integer(1),
				PRIMARY KEY (x, y))""")

				
		#what if approaching unknown fleet does not have an id?
		#id integer primary key,
		
		cur.execute("""create table if not exists diplomacy(
				user_id integer,
				other_user_id integer,
				relation integer(1),
				PRIMARY KEY(user_id, other_user_id)		
				)""")
		
		cur.execute("""create table if not exists hw(
				user_id integer PRIMARY KEY,
				x integer(2),
				y integer(2)
				)""")
		
		cur.execute("""create table if not exists fleet(
				fleet_id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				user_id integer,
				name text,
				is_hidden integer(1) default 0,
				times_spotted integer(1) default 0
				)""")

		cur.execute("""create table if not exists alien_fleet(
				fleet_id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				user_id integer,
				name text,
				weight integer,
				is_hidden integer(1) default 0,
				turn integer(2) default 0
				)""")

		cur.execute("""create table if not exists flying_fleet(
				fleet_id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				user_id integer,
				name text,
				from_x integer(2),
				from_y integer(2),
				arrival_turn integer(2),
				is_hidden integer(1),
				times_spotted integer(1),
				in_transit integer(1)
				)""")
						
		cur.execute("""create table if not exists alien_flying_fleet(
				x integer(2) not null,
				y integer(2) not null,
				user_id interger,
				from_x integer(2),
				from_y integer(2),
				arrival_turn integer(2),
				weight integer,
				is_hidden integer(1)
				)""")
				
		
		cur.execute("""create table if not exists unit(
				unit_id integer PRIMARY KEY,
				proto_id integer not null,
				hp integer not null
				)""")

		cur.execute("""create table if not exists fleet_unit(
				unit_id integer PRIMARY KEY,
				fleet_id integer)""")

		cur.execute("""create table if not exists garrison_unit(
				unit_id integer PRIMARY KEY,
				x integer(2),
				y integer(2))""")
				
		
		cur.execute("""create table if not exists alien_unit(
				unit_id integer PRIMARY KEY,
				fleet_id integer not null,
				carapace integer not null,
				class integer,
				color integer(1),
				weight integer,
				bc integer
				)""")
		
	
		cur.execute("""create table if not exists garrison_queue_unit(
				unit_id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				proto_id integer not null,
				done integer default 0,
				build_order integer default 0
				)""")
		
		cur.execute("""create table if not exists action(
				unit_id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				action_type integer not null,
				fleet_id integer,
				user_id integer not null,
				cancel_id integer
				)""")

		cur.execute("""create table if not exists proto(
				proto_id integer not null,
				user_id integer not null,
				class integer,
				carapace integer,
				weight integer,
				color integer(1) default 0,
				hp integer,
				
				fly_speed real,
				fly_range real,
				
				transport_capacity integer(1),
				carrier_capacity integer,
				is_transportable integer(1),
				
				aim_bomb real,
				aim_laser real,
				
				bomb_number integer(1),
				laser_number integer(1),
				
				defence_bomb real,
				defence_laser real,
				
				damage_bomb real,
				damage_laser real,
				
				name text,
				description text,
				
				is_war integer(1),
				
				support_main real,
				support_second real,
				
				require_tech_level integer(1),
				require_people integer,
				
				cost_main real,
				cost_second real,
				cost_money real,
				cost_people integer,
				
				is_ground_unit integer(1),
				is_spaceship integer(1),
				is_building integer(1),
				is_offensive integer(1),
				is_serial integer(1),
				
				build_speed integer,
				
				max_count integer,
				
				bonus_o integer,
				bonus_m integer,
				bonus_e integer,
				bonus_s integer,
				bonus_production integer,
				
				detect_range real,
				scan_strength real,
				stealth_level real,
				PRIMARY KEY (user_id, proto_id)
				)""")
				
		cur.execute("""create table if not exists proto_action(
				proto_action_id integer not null,
				proto_id integer not null,
				max_count integer,
				cost_people integer,
				cost_main integer,
				cost_second integer,
				cost_money integer,
				planet_can_be text,
				PRIMARY KEY(proto_id, proto_action_id))""") # as proto_action_id can easily duplicate
		
		self.conn.commit()		
		
	def clear_user_data(self, user_id):
		'clear all user-related data'
		#TODO: delete join do not work!, need to use nested select, or something else http://stackoverflow.com/questions/4967135/deleting-rows-from-sqlite-table-when-no-match-exists-in-another-table
		cur = self.conn.cursor()
	
		# delete fleet units
		cur.execute("delete from unit WHERE unit_id IN ( select unit_id from fleet_unit WHERE fleet_id IN (select fleet_id FROM fleet WHERE user_id=?))", (user_id,))
		cur.execute("delete from fleet_unit WHERE fleet_id IN (select fleet_id FROM fleet WHERE user_id=?)", (user_id,))

		# and flying fleet units
		cur.execute("delete from unit WHERE unit_id IN ( select unit_id from fleet_unit WHERE fleet_id IN (select fleet_id FROM flying_fleet WHERE user_id=?))", (user_id,))
		cur.execute("delete from fleet_unit WHERE fleet_id IN (select fleet_id FROM flying_fleet WHERE user_id=?)", (user_id,))

		# garrisons
		for user_planet in self.iter_objects_list('user_planet', {'user_id':user_id}):
			cur.execute('delete from unit WHERE unit_id IN ( select unit_id from garrison_unit WHERE garrison_unit.x = ? and garrison_unit.y = ?)', (user_planet['x'], user_planet['y']))
			cur.execute('delete from garrison_unit WHERE x = ? and y = ?', (user_planet['x'], user_planet['y']))
			cur.execute('delete from garrison_queue_unit WHERE x = ? and y = ?', (user_planet['x'], user_planet['y']))

		cur.execute('delete from user_planet WHERE user_id=?', (user_id,))
		cur.execute('delete from fleet WHERE user_id=?', (user_id,))
		cur.execute('delete from flying_fleet WHERE user_id=?', (user_id,))
		
		cur.execute('delete from action WHERE user_id=?', (user_id,))
		
		# mark all user-taken planets as empty
		cur.execute('update planet set user_id=0 WHERE user_id=?', (user_id,))
		
		# delete all proto actions and prototypes
		cur.execute('delete from proto_action WHERE proto_id IN (select proto_id from proto WHERE proto.user_id=?)', (user_id,))
		cur.execute('delete from proto WHERE proto.user_id=?', (user_id,))
		
		# delete open planets
		cur.execute('delete from open_planet WHERE user_id=?', (user_id,))
		
		#hw
		cur.execute('delete from hw WHERE user_id=?', (user_id,))
		
		# delete race
		cur.execute('delete from race WHERE user_id=?', (user_id,))
		
		cur.execute('delete from diplomacy WHERE user_id=?', (user_id,))
		
		# delete flying alien fleets ( unable distinct them from new ones )
		cur.execute('delete from alien_flying_fleet WHERE user_id=?', (user_id,))
		
		self.conn.commit()
	
	def add_user(self, user_data):
		'add new user'
		self.add_data('user', user_data)
		
	def add_user_info(self, user_id, user_name):
		user = self.get_user(user_id)
		if not user:
			self.add_data('user', {'user_id':user_id, 'name':user_name})
		
	def get_user_turn(self, user_id):
		user = self.get_object('user', {'user_id':user_id})
		if not user:
			return 0
		return int(user['turn'])
	
	def get_user_name(self, user_id):
		user = self.get_object('user', {'user_id':user_id})
		if not user:
			return '<unknown>'
		return user['name']
	def get_fleet_name(self, fleet_id):
		fleet = self.get_object('fleet', {'fleet_id':fleet_id})
		if not fleet:
			return '<none>'
		return fleet['name']
	
	def get_unit_name(self, unit_id):
		unit = self.get_object('unit', {'unit_id':unit_id})
		if not unit:
			return '<none>'
		proto = self.get_object('proto', {'proto_id':unit['proto_id']})
		if not proto:
			return '<proto-unknown>'
		return proto['name']
		
	def add_user_planet(self, planet_data):
		planet_data['turn'] = self.get_user_turn(planet_data['user_id'])
		self.add_data('user_planet', planet_data)
		self.add_data('planet', planet_data)
		self.add_data('open_planet', planet_data)
		
	def add_known_planet(self, data):
		
		self.update_planet(data)
		return
		
		# there is nothing except x,y,open for open_planet, so skip them here, not to clean our db
		if 'turn' in data:
			self.update_data('planet', ['x', 'y'], data)
		
		if 'o' in data:
			self.add_data('planet_geo', data)

	def add_open_planet(self, data):
		self.add_data('open_planet', data)
		
	def add_data(self, table, raw_data):
		cur = self.conn.cursor()
		
		data = extract(raw_data, tables[table])
		toDelete = []
		for k,v in data.items():
			if isinstance(v, str) and len(v) == 0:
				toDelete.append(k)
				# del data[k]
		for k in toDelete:
			del data[k]
		
		s = 'insert or replace into %s(%s) values(%s)'%(table, ','.join(data.keys()), ','.join([':%s'%(key_name,) for key_name in data.keys()]))
		#print s, data
		cur.execute(s, data)
		self.conn.commit()
		
	def add_planet_size(self, planet):
		
		pl = self.get_object('planet', {'x':planet['x'], 'y':planet['y']})
		if pl and 's' in pl and pl['s']:
			return
		
		cur = self.conn.cursor()
		
		#data = extract(raw_data, ['x','y','s', 'image'])
		
		s = 'insert or replace into planet_size(x,y,s,image) values(:x, :y, 10 * :s, :img)'
		#print s, planet
		cur.execute(s, planet)
		self.conn.commit()
		
		
	def update_data(self, table, filter_keys, data):
		'check data turn for max value'
		#if not 'turn' in data or not data['turn']:
		#	return
		u = self.get_object(table, {k:v for k,v in data.items() if k in filter_keys})
		if u and u['turn'] and int(u['turn']) > int(data['turn']):
			return
		
		self.add_data(table, data)
		
	def update_planet(self, planet):
		coord = {'x':planet['x'], 'y':planet['y']}
		pl = self.get_object('planet', coord)
		if not pl:
		#	if not 's' in planet or not planet['s']:
		#		size_obj = self.get_object('planet_size', coord)
		#		if size_obj:
		#			planet['s'] = size_obj['s']
		#		else:
		#			print 'Wrong planet_size data for %s'%(coord,)
			self.add_data('planet', planet)
			return True
		
		cur = self.conn.cursor()
		
		# check if need to update geo
		if (not 'o' in pl or not pl['o']) and ('o' in planet and planet['o']):
			#print 'update geo planet %s'%(planet,)
			cur.execute('update planet set o=:o, e=:e, m=:m, t=:t, s=:s WHERE x=:x AND y=:y', planet)
			self.conn.commit()
		
		if 'turn' in planet and planet['turn']:
			if int(planet['turn']) > pl['turn']:
				# make sure they will be cleaned up if currently exists ( removing user from planet )
				if not 'user_id' in planet:
					planet['user_id'] = None
				if not 'name' in planet:
					planet['name'] = None
				cur.execute('update planet set user_id=:user_id, name=:name, turn=:turn WHERE x=:x AND y=:y', planet)
				self.conn.commit()
			elif int(planet['turn']) == pl['turn']:
				if not 'user_id' in planet or planet['user_id'] == '' or int(planet['user_id'])==0:
					planet['user_id'] = pl['user_id']
				if not 'name' in planet or planet['name'] == '':
					planet['name'] = pl['name']
				cur.execute('update planet set user_id=:user_id, name=:name, turn=:turn WHERE x=:x AND y=:y', planet)
				self.conn.commit()
				
		
	def add_action_result(self, action_id, is_ok, return_id = None):
		self.conn.cursor().execute('update requested_action set is_ok=?, return_id=? WHERE action_id=?', (is_ok, return_id, action_id))
		self.conn.commit()
	
	def add_pending_action(self, act_id, table, action, data_filter):
		pass
	
	def command_create_fleet(self, user_id, coord, name):
		self.create_fleet_id -= 1
		self.add_data('fleet', {'user_id':user_id, 'x':coord[0], 'y':coord[1], 'name':name, 'fleet_id':self.create_fleet_id})
		return self.create_fleet_id
		
	def command_move_unit_to_fleet(self, unit_id, fleet_id):
		# find current unit location ( fleet or garrison )
		cur = self.conn.cursor()
		tables = ['fleet_unit', 'garrison_unit']
		for table in tables:
			cur.execute('select * from %s WHERE unit_id=?'%(table,), (unit_id,))
			res = cur.fetchone()
			if res:
				# ok it's here
				cur.execute('delete from %s WHERE unit_id=?'%(table,), (unit_id,))
				self.conn.commit()
				break
		
		#insert it to the fleet
		self.add_data('fleet_unit', {'fleet_id':fleet_id, 'unit_id':unit_id})
		
	def command_build(self, coord, proto_id):
		self.create_fleet_id -= 1
		cur = self.conn.cursor()
		cur.execute('select max(build_order) from garrison_queue_unit WHERE x=? and y=?', coord)
		res = cur.fetchone()
		build_order = 0
		if res and res[0]:
			build_order = int(res[0]) + 1
		self.add_data('garrison_queue_unit', {'x':coord[0], 'y':coord[1], 'proto_id':proto_id, 'unit_id':self.create_fleet_id, 'build_order':build_order})
		return self.create_fleet_id
	
	def command_destroy(self, unit_id):
		self.remove_object('unit', {'unit_id':unit_id})
		self.remove_object('garrison_unit', {'unit_id':unit_id})
		
	def command_move_unit_to_garrison(self, unit_id, coord):
		self.add_data('garrison_unit', {'x':coord[0], 'y':coord[1], 'unit_id':unit_id})
		self.remove_object('fleet_unit', {'unit_id':unit_id})
		
	def command_fleet_jump(self, fleet_id, coord):
		fleet = self.get_object('fleet', {'fleet_id':fleet_id})
		if not fleet:
			return
		
		fleet['from_x'] = fleet['x']
		fleet['from_y'] = fleet['y']
		start_pos = fleet['x'], fleet['y']
		fleet['x'] = coord[0]
		fleet['y'] = coord[1]
		spd, rng = self.get_fleet_speed_range(fleet_id)
		fleet['arrival_turn'] = self.get_user_turn(fleet['user_id']) + math.ceil( util.distance(start_pos, coord) / spd )
		
		self.add_data('flying_fleet', fleet)
		self.remove_object('fleet', {'fleet_id':fleet_id})
		
	def command_fleet_cancel_jump(self, fleet_id):
		fleet = self.get_object('flying_fleet', {'fleet_id':fleet_id})
		if not fleet:
			return
		
		x,y = fleet['from_x'], fleet['from_y']
		#fleet['from_x'] = fleet['x']
		#fleet['from_y'] = fleet['y']
		#start_pos = fleet['x'], fleet['y']
		fleet['x'] = x
		fleet['y'] = y
		
		self.add_data('fleet', fleet)
		self.remove_object('flying_fleet', {'fleet_id':fleet_id})
	
	def keys(self, table):
		return tables[table]
	
	def max_turn(self):
		c = self.conn.cursor()
		c.execute('select max(turn) from user')
		r = c.fetchone()
		return int(r[0])
		
	def add_fleet_unit(self, fleet_id, unit_data):
		self.add_data('fleet_unit', {'fleet_id':fleet_id, 'unit_id':unit_data['unit_id']})
		self.add_data('unit', unit_data)
		
	def add_garrison_unit(self, unit_data):
		self.add_data('garrison_unit', unit_data)
		self.add_data('unit', unit_data)
		
	def normalize_user_fleets(self, user_id):
		cur = self.conn.cursor()
		for fleet in self.get_objects_list('alien_fleet', {'user_id':user_id}):
			cur.execute('delete from alien_unit WHERE fleet_id=%s'%(fleet['fleet_id'],))
			
		cur.execute('delete from alien_fleet WHERE user_id=%s'%(user_id,))
		
		cur.execute('delete from flying_fleet WHERE fleet_id IN (select fleet_id from fleet)')
		
		self.conn.commit()

	def normalize_user_planets(self):
		cur = self.conn.cursor()
		for user in self.iter_objects_list('user'):
			if 'login' in user and user['login']:
				turn = user['turn']
				user_id = user['user_id']
				for planet in self.iter_objects_list('user_planet', {'user_id':user_id}):
					planet['turn'] = turn
					self.update_planet(planet)
		self.conn.commit()
		
	def remove_temporary_fleets(self):
		cur = self.conn.cursor()
			
		cur.execute('delete from fleet WHERE fleet_id < 0')
		cur.execute('delete from flying_fleet WHERE fleet_id < 0')
		cur.execute('delete from fleet_unit WHERE fleet_id < 0')
		self.conn.commit()

	def normalize_fleets(self):
		for u in self.iter_objects_list('user'):
			if 'login' in u and u['login']:
				self.normalize_user_fleets(u['user_id'])
				
	def remove_duplicate_planets(self):
		cur = self.conn.cursor()
		for p in self.iter_objects_list('planet'):
			if 's' in p and p['s'] and p['s'] != 0:
				cur.execute('delete from planet_size WHERE x=:x AND y=:y', p)
			else:
				psize = self.get_object('planet_size', {'x':p['x'], 'y':p['y']})
				if psize:
					cur.execute('update planet set s=:s WHERE x=:x AND y=:y', psize)
		
		self.conn.commit()
		
	def execute(self, table, query, args):
		cur = self.conn.cursor()
		keys = ['%s.%s'%(table, key) for key in tables[table]]
		#print 'exec %s %s %s %s'%(query, ','.join(keys), table, args)
		cur.execute(query%(','.join(keys), table), args)
		res = []
		for r in cur.fetchall():
			res.append( dict(zip(tables[table], r)))
		return res
		
	def get_governers(self, user_id):
		GOVERN_PROTO_ID=13
		res  = self.execute('unit', 'select %s from %s JOIN fleet_unit USING(unit_id) JOIN fleet USING(fleet_id) WHERE unit.proto_id=? AND fleet.user_id=?', (GOVERN_PROTO_ID, user_id ))
		res += self.execute('unit', 'select %s from %s JOIN garrison_unit USING(unit_id) JOIN user_planet USING(x,y) WHERE unit.proto_id=? AND user_planet.user_id=?', (GOVERN_PROTO_ID, user_id ))
		return res
		
	def get_fleet_units(self, fleet_id):
		return self.execute('unit', """select %s from %s JOIN fleet_unit ON fleet_unit.unit_id=unit.unit_id
											WHERE fleet_unit.fleet_id=?""", (fleet_id,))

	def get_garrison_units(self, coord, value_in = None):
		conds = ''
		if value_in:
			conds = ' AND %s IN (%s)'%(value_in[0], ','.join(value_in[1]))
		cur = self.conn.cursor()
		keys = tables['unit']
		cur.execute("""select %s from unit
						JOIN garrison_unit USING(unit_id) WHERE garrison_unit.x = ? AND garrison_unit.y = ? %s"""%(','.join(keys), conds), coord)
		r = []
		for res in cur.fetchall():
			r.append( dict(zip(keys, res)))
		return r
		
	def get_building_queue(self, coord):
		return self.execute('garrison_queue_unit', """select %s from %s
						WHERE x = ? AND y = ? ORDER BY build_order""", coord)
						
	def get_user(self, user_id):
		return self.get_object('user', {'user_id':user_id})
		
	def remove_object(self, table, conds):
		cur = self.conn.cursor()
		s = 'delete from %s WHERE %s'%(table, ' and '.join(['%s=?'%(key_name,) for key_name in conds.keys()]))
		cur.execute(s, tuple(conds.values()))
		self.conn.commit()
		
	def update_object(self, table, conds, new_values):
		cur = self.conn.cursor()
		s = 'update %s set %s WHERE %s'%(table,  ','.join(['%s=?'%(key,) for key in new_values.keys()]), ' and '.join(['%s=?'%(key_name,) for key_name in conds.keys()]))
		cur.execute(s, tuple(new_values.values() + conds.values()))
		self.conn.commit()

	def get_object(self, table, conds):
		cur = self.conn.cursor()
		keys = tables[table]
		s = 'select %s from %s WHERE %s'%(','.join(keys), table, ' and '.join(['%s=?'%(key_name,) for key_name in conds.keys()]))
		cur.execute(s, tuple(conds.values()))
		r = cur.fetchone()
		if not r:
			#print 'empty result'
			return None
		return dict(zip(keys, r))
		
	def get_objects_list(self, table, conds = {}):
		
		objs = []
		for obj in self.iter_objects_list(table, conds):
			objs.append(obj)
		return objs

	def iter_planets(self, rect, owned = False, inhabited = False):
		keys = self.keys('planet')
		s = 'select %s from planet WHERE x BETWEEN ? AND ? AND y BETWEEN ? AND ?'%(','.join(keys),)
		if owned:
			s+=' AND user_id IN (select user_id from user WHERE login IS NOT null)'
		elif inhabited:
			s+=' AND user_id IS NOT NULL'
		
		cur = self.conn.cursor()
		cur.execute(s, rect)
		for r in cur.fetchall():
			yield dict(zip(keys, r))
			
	def ixter_planets(self, rect, owned = False, inhabited = False):
		cur = self.conn.cursor()
		table = 'planet'
		keys = ['x', 'y', 'user_id', 's']
		x0,x1,y0,y1 = rect
		s = 'select %s from planet JOIN planet_size USING(x,y) WHERE x BETWEEN %s AND %s AND y BETWEEN %s AND %s'%(','.join(keys), x0,x1,y0,y1)
		if owned:
			s += ' AND user_id IN (select user_id from user WHERE login != null)'
		elif inhabited:
			s += ' AND not user_id is null'
			
		#print '%s with %s'%(s, rect)
		cur.execute(s)
		for r in cur.fetchall():
			yield dict(zip(keys, r))

	def iter_planets_size(self, rect = None, pos = None, fly_range = None, bigger_first = None, size_min = None, size_max = None):
		cur = self.conn.cursor()
		s = 'select x,y,s from planet_size'
		values = []
		conds = []
		
		if rect:
			rect_cond = 'x >= ? AND x <= ? AND y >= ? AND y <= ?'
			conds.append(rect_cond)
			values += list(rect)
		
		if fly_range:
			dist_condition = '((?-x)*(?-x)+(?-y)*(?-y))<=?'
			conds.append(dist_condition)
			values+=[pos[0], pos[0], pos[1], pos[1], fly_range*fly_range]
		if size_min:
			size_min_cond = 's >= ?'
			conds.append(size_min_cond)
			values.append(size_min)
		if size_max:	
			size_max_cond = 's <= ?'
			conds.append(size_max_cond)
			values.append(size_max)
			
		if conds:
			s+=' WHERE %s'%(' AND '.join(conds),)
			
		if bigger_first:
			s+=' ORDER BY s DESC'
		
		#print s, values
		cur.execute(s, tuple(values))
		for r in cur.fetchall():
			yield dict(zip(['x','y','s'], r))
			
	def iter_objects_list(self, table, conds = {}, rect = None, controlled = None):
		cur = self.conn.cursor()
		s = 'select %s from %s'%(','.join(tables[table]), table,)
		
		conds_str = []

		if conds and len(conds) > 0:
			conds_str += ['%s=%s'%(key_name,value) for key_name,value in conds.items()]
			
		if rect:
			conds_str += ['x between %s AND %s AND y between %s AND %s'%rect]
		if controlled:
			conds_str += ['user_id in (select user_id from user where login is not NULL)']

		if conds_str:
			s+=' WHERE '+' AND '.join(conds_str)
		#print '"%s" with %s'%(s, type(s))
		cur.execute(s)#, tuple(conds.values()))
		for r in cur.fetchall():
			yield dict(zip(tables[table], r))

	def get_fleet_speed_range(self, fleet_id):
		min_speed, min_range = None, None
		for u in self.get_fleet_units(fleet_id):
			proto = self.get_object('proto', {'proto_id':u['proto_id']})
			if not proto:
				continue
			if not min_speed or min_speed < proto['fly_speed']:
				min_speed = proto['fly_speed']
			if not min_range or min_range < proto['fly_range']:
				min_range = proto['fly_range']
		return min_speed, min_range
	
	def iter_open_planets(self, fly_range, pos, dest_pos, exclude_planets = []):
		dist_condition = '((:x0-x)*(:x0-x)+(:y0-y)*(:y0-y))<=:fly_range'
		
		exclude_condition = ''
		if exclude_planets:
			 exclude_condition = ' AND %s'%(' AND '.join(['(x!=%d AND y!=%d)'%(x,y) for x,y in exclude_planets]))
		min_condition = ' ORDER BY ((:x1-x)*(:x1-x)+(:y1-y)*(:y1-y))'
		args = {'x0':pos[0], 'y0':pos[1], 'x1':dest_pos[0], 'y1':dest_pos[1], 'fly_range':fly_range*fly_range}
		cur = self.conn.cursor()
		s = 'select x,y from open_planet WHERE %s%s%s'%(dist_condition, exclude_condition, min_condition)
		#print s, args
		cur.execute(s, args)
		for r in cur.fetchall():
			yield r[0], r[1]

store = Store()

import unittest

class TestStore(unittest.TestCase):
	USER_ID = 3
	USER_DATA = {'user_id':USER_ID, 'login':'testu', 'race_id':22, 'name':u'test_user', 'turn':33, 'money':3, 'resource_main':455, 'resource_secondary':23}
	USER_ID2 = 5
	USER_DATA_OLD = {'user_id':USER_ID, 'login':'testu', 'race_id':22, 'name':u'test_user', 'turn':32, 'money':1, 'resource_main':2, 'resource_secondary':23}
	FLEET = {'fleet_id':34, 'user_id':USER_ID, 'name':'test-flying machines', 'x':12, 'y':987, 'times_spotted':0, 'is_hidden':0}
	FLEET_OLD = {'fleet_id':34, 'user_id':USER_ID, 'name':'test', 'x':112, 'y':987, 'times_spotted':0, 'is_hidden':1}
	PROTO_ID = 9
	
	PLANET = {'x':11, 'y':22, 'user_id':USER_ID, 'name':'my home', 'turn':33}
	PLANET_OLD = {'x':11, 'y':22, 'user_id':USER_ID, 'name':'Users  home', 'turn':12}

	FLEET_UNIT = {'hp':1, 'unit_id':11, 'proto_id':PROTO_ID}
	FLEET_UNIT_OLD = {'hp':2, 'unit_id':11, 'proto_id':PROTO_ID}
	FLEET_UNIT2 = {'hp':2, 'unit_id':12, 'proto_id':PROTO_ID}
	FLEET_UNIT_OTHER = {'hp':2, 'unit_id':1555, 'proto_id':PROTO_ID}
	
	PROTO = {'proto_id':PROTO_ID, 'user_id':USER_ID, 'class':100, 'name':'test class un'}
	PROTO_ACTION = {'proto_id':PROTO_ID, 'proto_action_id':123}
	UNIT = {'unit_id':11, 'hp':3, 'proto_id':PROTO_ID}
	
	def setUp(self):
		self.store = Store()
	
	def test_add_get(self):
		user_id = self.USER_ID
		user_data = self.USER_DATA
		user_none = self.store.get_user(user_id)
		self.assertIsNone(user_none)
		self.store.add_user( user_data)
		
		user = self.store.get_user(user_id)
		self.assertEqual(user, user_data)
		
		user_none = self.store.get_user(user_id+1)
		self.assertIsNone(user_none)
		
		self.assertEqual([], self.store.get_objects_list('user', {'name':u'"test"'}))
		users = self.store.get_objects_list('user')
		self.assertEqual(len(users), 1)
		self.assertEqual(users[0], user_data)
		
	def test_add_planet(self):
		user_id = 3
		user_data = {'user_id':user_id, 'race_id':22, 'name':u'test_user', 'turn':33}
		self.store.add_user(user_data)
		
		user_planet = {'user_id':user_id, 'x':34, 'y':56, 'o':56, 'e':12, 't':90, 's':32, 'corruption':0, 'is_open':1, 'population':4567, 'name':'hw'}
		self.store.add_user_planet(user_planet)
		
		up = extract(user_planet, tables['planet'])
		planet = self.store.get_object('planet', extract(user_planet, ['x', 'y']))
		self.assertEqual(up, planet)
		
		us_pl = self.store.get_object('user_planet', extract(user_planet, ['user_id']))
		u_pl = extract(user_planet, tables['user_planet'])
		self.assertEqual(us_pl, u_pl)
		
		coord = {'x':11, 'y':22}
		
		known_planet = {'x':11, 'y':22, 'o':5, 'e':22, 'm':32, 't':78, 's':99}
		self.store.add_known_planet(known_planet)
		
		known_planet2 = {'name':'test', 'user_id':4, 'x':11, 'y':22, 'turn':21}
		self.store.add_known_planet(known_planet2)
		
		known_open_planet3 = {'user_id':3, 'x':11, 'y':22, 'is_open':1}
		self.store.add_data('open_planet', known_open_planet3)
		
		
		p = self.store.get_object('planet', coord)
		self.assertEqual(p, known_planet2)

		p = self.store.get_object('planet_geo', coord)
		self.assertEqual(p, known_planet)
		
		# add older info
		
		old_info = coord.copy()
		old_info['user_id']=11
		old_info['turn'] = 8
		self.store.add_known_planet(old_info)

		p = self.store.get_object('planet', coord)
		self.assertEqual(p, known_planet2)
		
	def test_units(self):
		fleet = 12
		uts = [{'proto_id':34, 'unit_id':unit_id, 'hp':2} for unit_id in range(1,5)]
		for u in uts:
			self.store.add_fleet_unit( fleet, u )
		
		units = self.store.get_fleet_units( fleet )
		self.assertEqual(units, uts)
	
	def test_x_clear(self):
		self.store.add_user(self.USER_DATA)
		self.assertEqual([], self.store.get_objects_list('fleet', {'user_id':self.USER_ID}))
		self.store.add_data('fleet', self.FLEET )
		self.store.add_fleet_unit(self.FLEET['fleet_id'], self.FLEET_UNIT)
		self.store.add_fleet_unit(self.FLEET['fleet_id'], self.FLEET_UNIT2)
		
		self.store.add_fleet_unit(self.FLEET['fleet_id']+11, self.FLEET_UNIT_OTHER)

		self.assertEqual([self.FLEET], self.store.get_objects_list('fleet', {'user_id':self.USER_ID}))
		self.assertEqual(sorted([self.FLEET_UNIT, self.FLEET_UNIT2]), sorted(self.store.get_fleet_units(self.FLEET['fleet_id'])))

		self.store.clear_user_data(self.USER_ID)
		self.assertEqual([], self.store.get_objects_list('fleet', {'user_id':self.USER_ID}))
		self.assertEqual([self.FLEET_UNIT_OTHER], self.store.get_fleet_units(self.FLEET['fleet_id']+11))
		
	def test_update(self):
		self.store.update_data('user', ['user_id'], self.USER_DATA)
		self.store.update_data('user', ['user_id'], self.USER_DATA_OLD)
		
		user = self.store.get_user(self.USER_ID)
		self.assertEqual(user, self.USER_DATA)
		
		self.store.update_data('planet', ['x', 'y'], self.PLANET_OLD)
		self.assertEqual(self.PLANET_OLD, self.store.get_object('planet', {'x':self.PLANET_OLD['x'], 'y':self.PLANET_OLD['y']}))
		
		self.store.update_data('planet', ['x', 'y'], self.PLANET)
		self.assertEqual(self.PLANET, self.store.get_object('planet', {'x':self.PLANET['x'], 'y':self.PLANET['y']}))
		
		self.store.update_data('planet', ['x', 'y'], self.PLANET_OLD)
		self.assertEqual(self.PLANET, self.store.get_object('planet', {'x':self.PLANET['x'], 'y':self.PLANET['y']}))
	
	def test_get_governers(self):
		self.assertEqual([], self.store.get_governers(3))
		
		

if __name__ == '__main__':
	unittest.main()
