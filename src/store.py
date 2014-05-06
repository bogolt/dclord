import sqlite3
import logging
import sys, traceback

def to_pos(a,b):
	return int(a),int(b)
	
def to_str_list(lst):
	return [str(x) for x in lst]


log = logging.getLogger('dclord')

tables = {'planet':['x', 'y', 'user_id', 'name', 'turn'],
		'planet_geo':['x','y', 'o','e','m','t','s'],
		'open_planet':['x','y','user_id'], #open planets for specified user-id
		'user_planet':['x','y','user_id', 'corruption', 'population', 'is_open'],
		'fleet':['x','y','user_id','fleet_id','name', 'times_spotted', 'is_hidden'],
		'alien_fleet':['x','y','user_id','fleet_id','name', 'is_hidden', 'turn'],
		'flying_fleet':['x','y','user_id','fleet_id','name', 'from_x', 'from_y', 'arrival_turn'],
		'flying_alien_fleet':['x','y','user_id','from_x', 'from_y', 'arrival_turn', 'weight'], #user_id who spot fleet, no primary key, no fleet user owner
		'unit':['unit_id', 'hp', 'proto_id'],
		'fleet_unit':['unit_id', 'fleet_id'],
		'garrison_unit':['unit_id', 'x', 'y'],
		'garrison_queue_unit':['unit_id', 'x', 'y', 'bc', 'done', 'build_order'],
		'alien_unit':['fleet_id', 'unit_id', 'weight', 'carapace','color'],
		'user':['user_id', 'name', 'login', 'race_id', 'turn'], # owned users have not empty login, turn of last info loading from server
		'race':['race_id', 'temperature_delta',  'temperature_optimal',  'resource_nature',  'population_growth', 'resource_main', 'resource_secondary', 'modifier_fly', 'modifier_build_war', 'modifier_build_peace', 'modifier_science', 'modifier_stealth', 'modifier_detection', 'modifier_mining', 'modifier_price', 'name'],
		'diplomacy':['user_id', 'other_user_id', 'relation'], #dip relation from user to other_user
		'proto':['proto_id', 'user_id', 'fly_speed', 'aim_bomb', 'color', 'build_speed', 'require_people', 'carapace', 'fly_range', 'class', 'cost_second', 'cost_main', 'cost_money', 'is_transportable', 'require_tech_level', 'support_second', 'name', 'stealth_level', 'bonus_s', 'bonus_m', 'bonus_o', 'max_count', 'bonus_e', 'support_main', 'weight', 'damage_laser', 'is_ground_unit', 'is_serial', 'aim_laser', 'is_spaceship', 'transport_capacity', 'is_offensive', 'detect_range', 'damage_bomb', 'bonus_production', 'description', 'scan_strength', 'hp', 'defence_laser', 'defence_bomb', 'carrier_capacity', 'laser_number', 'is_building', 'cost_people', 'bomb_number', 'is_war'],
		'proto_action':['type', 'proto_id', 'max_count', "cost_people", "cost_main", "cost_money", "cost_second", "planet_can_be"],
		'hw':['x','y', 'user_id']
}

DIP_RELATION_UNSPECIFIED = -1
DIP_RELATION_ENEMY = 0
DIP_RELATION_NEUTRAL = 1
DIP_RELATION_ALLY = 2
DIP_RELATION_VASSAL = 3
DIP_RELATION_LORD = 4

def extract(d, key_list):
	r = {}
	for key, value in d.iteritems():
		if key in key_list:
			r[key] = value
	return r

class Store:
	def __init__(self):
		self.conn = sqlite3.connect(':memory:')
		self.create_tables()
	
	def create_tables(self):
		cur = self.conn.cursor()
		cur.execute("""create table if not exists user(
				user_id integer PRIMARY KEY,
				name text not null,
				race_id integer not null,
				login text,
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
				id integer PRIMARY KEY,
				user_id integer not null,
				return_id integer default 0,
				is_ok integer default 0
				)""")

		cur.execute("""create table if not exists planet(
				x integer(2) not null,
				y integer(2) not null,
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
						
		cur.execute("""create table if not exists flying_alien_fleet(
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
				unit_id integer,
				fleet_id integer,
				PRIMARY KEY(unit_id, fleet_id))""")

		cur.execute("""create table if not exists garrison_unit(
				unit_id integer,
				x integer(2),
				y integer(2),
				PRIMARY KEY(unit_id, x, y))""")
				
		
		cur.execute("""create table if not exists alien_unit(
				unit_id integer PRIMARY KEY,
				fleet_id integer not null,
				carapace integer not null,
				color integer(1),
				weight integer,
				bc integer
				)""")
		
	
		cur.execute("""create table if not exists garrison_queue_unit(
				unit_id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				bc integer not null,
				done integer,
				build_order integer
				)""")
		
		cur.execute("""create table if not exists proto(
				proto_id integer PRIMARY KEY,
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
				stealth_level real
				)""")
				
		cur.execute("""create table if not exists proto_action(
				proto_action_id integer primary key,
				type integer not null,
				proto_id integer not null,
				max_count integer,
				cost_people integer,
				cost_main integer,
				cost_second integer,
				cost_money integer,
				planet_can_be text
				)""")
		
		self.conn.commit()		
		
	def clear_user_data(self, user_id):
		'clear all user-related data'
		cur = self.conn.cursor()
		
		# delete units
		cur.execute("""delete from unit 
						JOIN fleet_unit ON fleet_unit.unit_id=unit.unit_id
						JOIN fleet ON fleet_unit.fleet_id=fleet.fleet_id
						JOIN user ON user.user_id=fleet.fleet_id
											WHERE user.user_id=?""", (user_id,))
											
		cur.execute("""delete from unit
						JOIN garrison_unit ON unit.unit_id=garrison_unit.unit_id
						JOIN user_planet ON user_planet.x = garrison_unit.x AND user_planet.y = garrison_unit.y
											WHERE user_planet.user_id=?""", (user_id,))

		# delete units fleets/garrison link
		cur.execute('delete from fleet_unit JOIN fleet ON fleet_unit.fleet_id=fleet.fleet_id JOIN user ON fleet.user_id=user.user_id WHERE user_id=?', user_id)
		cur.execute('delete from garrison_unit JOIN user_planet ON user_planet.x = garrison_unit.x AND user_planet.y = garrison_unit.y WHERE user_id=?', user_id)

		cur.execute('delete from user_planet WHERE user_id=?', user_id)
		cur.execute('delete from fleet WHERE user_id=?', user_id)
		
		
		# mark all user-taken planets as empty
		cur.execute('update planet set user_id=0 WHERE user_id=?', user_id)
		
		# delete all proto actions and prototypes
		cur.execute('delete from proto_action JOIN proto ON proto_action.proto_id=proto.proto_id WHERE proto.user_id=?', (user_id,))
		cur.execute('delete from proto WHERE proto.user_id=?', (user_id,))
		
		# delete open planets
		cur.execute('delete from open_planet WHERE user_id=?', (user_id,))
		
		#hw
		cur.execute('delete from hw WHERE user_id=?', (user_id,))
		
		# delete race
		cur.execute('delete from race WHERE user_id=?', user_id)
		
		cur.execute('delete from diplomacy WHERE user_id=?', user_id)
		
		self.conn.commit()
	
	def add_user(self, user_data):
		'add new user'
		self.add_data('user', user_data)
		
	def get_user_turn(self, user_id):
		user = self.get_object('user', {'user_id':user_id})
		if not user:
			return 0
		return int(user['turn'])
		
	def add_user_planet(self, planet_data):
		planet_data['turn'] = self.get_user_turn(planet_data['user_id'])
		self.add_data('user_planet', planet_data)
		self.add_data('planet', planet_data)
		self.add_data('planet_geo', planet_data)
		self.add_data('open_planet', planet_data)
		
	def add_data(self, table, raw_data):
		cur = self.conn.cursor()
		
		data = extract(raw_data, tables[table])
		
		s = 'insert or replace into %s(%s) values(%s)'%(table, ','.join(data.keys()), ','.join([':%s'%(key_name,) for key_name in data.iterkeys()]))
		#print s
		cur.execute(s, data)
		self.conn.commit()
		
	def get_user(self, user_id):
		return self.get_object('user', {'user_id':user_id})
		
	def get_object(self, table, conds):
		cur = self.conn.cursor()
		s = 'select %s from %s WHERE %s'%(','.join(tables[table]), table, ' and '.join(['%s=?'%(key_name,) for key_name in conds.iterkeys()]))
		#print s
		cur.execute(s, tuple(conds.values()))
		r = cur.fetchone()
		if not r:
			#print 'empty result'
			return None
		#print 'result %s'%(r,)
		return dict(zip(tables[table], r))
		
	def get_objects_list(self, table, conds = {}):
		
		objs = []
		for obj in self.iter_objects_list(table, conds):
			objs.append(obj)
		return objs

	def iter_objects_list(self, table, conds = {}):
		cur = self.conn.cursor()
		s = 'select %s from %s'%(','.join(tables[table]), table,)

		if conds:
			s += ' WHERE %s'%(' and '.join(['%s=?'%(key_name,) for key_name in conds.iterkeys()]),)

		#print '%s with %s'%(s, tuple(conds.values()))
		cur.execute(s, tuple(conds.values()))
		for r in cur.fetchall():
			yield dict(zip(tables['user'], r))

import unittest

class TestStore(unittest.TestCase):
	def setUp(self):
		self.store = Store()
	
	def test_add_get(self):
		user_id = 3
		user_data = {'user_id':user_id, 'race_id':22, 'name':u'test_user', 'login':u'very_sercret', 'turn':33}
		user_none = self.store.get_user(user_id)
		self.assertIsNone(user_none)
		self.store.add_user( user_data)
		
		user = self.store.get_user(user_id)
		self.assertEqual(user, user_data)
		
		user_none = self.store.get_user(user_id+1)
		self.assertIsNone(user_none)
		
		self.assertEqual([], self.store.get_objects_list('user', {'name':u'test'}))
		users = self.store.get_objects_list('user')
		self.assertEqual(len(users), 1)
		self.assertEqual(users[0], user_data)
		
	def test_add_planet(self):
		user_id = 3
		user_data = {'user_id':user_id, 'race_id':22, 'name':u'test_user', 'login':u'very_sercret', 'turn':33}
		self.store.add_user(user_data)
		
		user_planet = {'user_id':user_id, 'x':34, 'y':56, 'o':56, 'e':12, 't':90, 's':32, 'corruption':0, 'population':4567, 'name':'hw'}
		self.store.add_user_planet(user_planet)
		
		up = extract(user_planet, tables['planet'])
		planet = self.store.get_object('planet', extract(user_planet, ['x', 'y']))
		self.assertEqual(up, planet)
		
		

if __name__ == '__main__':
	unittest.main()
