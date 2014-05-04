import sqlite3
import logging
import sys, traceback
import serialization

def to_pos(a,b):
	return int(a),int(b)
	
def to_str_list(lst):
	return [str(x) for x in lst]


log = logging.getLogger('dclord')

KEYS_PLANET = ('x','y','o','e','m','t','s','owner_id', 'name')
KEYS_USER_PLANET = ('x','y','corruption','population','owner_id','is_open')
KEYS_OPEN_PLANET = ('x','y','user_id')
KEYS_FLEET = ('id', 'x','y','owner_id', 'is_hidden','name','weight')
KEYS_FLYING_FLEET = ('id', 'x','y','in_transit', 'owner_id','from_x','from_y','weight', 'arrival_turn','is_hidden')
KEYS_FLYING_ALIEN_FLEET = ('x','y','user_id','from_x','from_y','weight', 'arrival_turn','is_hidden')
KEYS_UNIT = ('id', 'hp', 'class', 'fleet_id', 'x', 'y')
KEYS_GARRISON_QUEUE_UNIT = ('id', 'class', 'x', 'y')
KEYS_ALIEN_UNIT = ('id', 'carapace','color','weight','fleet_id')
KEYS_USER = ('id', 'name', 'race_id', 'login','turn')
KEYS_HW = ('hw_x', 'hw_y', 'player_id')
KEYS_RACE = ('id', 'temperature_delta',  'temperature_optimal',  'resource_nature',  'population_growth', 'resource_main', 'resource_secondary', 'modifier_fly', 'modifier_build_war', 'modifier_build_peace', 'modifier_science', 'modifier_stealth', 'modifier_detection', 'modifier_mining', 'modifier_price', 'name')
KEYS_PLAYER = ('player_id', 'name')
KEYS_PROTO = ('owner_id', 'fly_speed', 'aim_bomb', 'color', 'build_speed', 'require_people', 'carapace', 'fly_range', 'id', 'class', 'cost_second', 'cost_main', 'cost_money', 'is_transportable', 'require_tech_level', 'support_second', 'name', 'stealth_level', 'bonus_s', 'bonus_m', 'bonus_o', 'max_count', 'bonus_e', 'support_main', 'weight', 'damage_laser', 'is_ground_unit', 'is_serial', 'aim_laser', 'is_spaceship', 'transport_capacity', 'is_offensive', 'detect_range', 'damage_bomb', 'bonus_production', 'description', 'scan_strength', 'hp', 'defence_laser', 'defence_bomb', 'carrier_capacity', 'laser_number', 'is_building', 'cost_people', 'bomb_number', 'is_war')
KEYS_PROTO_ACTION = ('id', 'type', 'proto_id', 'proto_owner_id', 'max_count', "cost_people", "cost_main", "cost_money", "cost_second", "planet_can_be")
KEYS_DIPLOMACY = ('owner_id', 'player_id', 'status')

UNSPECIFIED =-1
ENEMY   = 0
NEUTRAL = 1

class Db:
	PLANET = 'planet'
	USER_PLANET = 'user_planet'
	OPEN_PLANET = 'open_planet'
	USER = 'user'
	PLAYER = 'player'
	HW = 'hw'
	FLEET = 'fleet'
	UNIT = 'unit'
	ALIEN_UNIT = 'alien_unit'
	FLYING_FLEET = 'flying_fleet'
	FLYING_ALIEN_FLEET = 'flying_alien_fleet'
	#ALIEN_FLEET = 'alien_fleet'
	GARRISON_QUEUE_UNIT = 'garrison_queue_unit'
	PROTO = 'proto'
	PROTO_ACTION = 'proto_action'
	RACE = 'race'
	DIP = 'dip'
	PLANET_SIZE ='planet_size'
	
	table_keys = {PLANET:KEYS_PLANET, OPEN_PLANET:KEYS_OPEN_PLANET, USER: KEYS_USER, PLAYER:KEYS_PLAYER, HW:KEYS_HW, FLEET:KEYS_FLEET, UNIT:KEYS_UNIT,
	 ALIEN_UNIT:KEYS_ALIEN_UNIT, FLYING_FLEET:KEYS_FLYING_FLEET, FLYING_ALIEN_FLEET:KEYS_FLYING_ALIEN_FLEET, 
	 GARRISON_QUEUE_UNIT:KEYS_GARRISON_QUEUE_UNIT, PROTO:KEYS_PROTO, PROTO_ACTION:KEYS_PROTO_ACTION, RACE:KEYS_RACE, DIP: KEYS_DIPLOMACY
	 , PLANET_SIZE : ('x','y', 's', 'image'), USER_PLANET:KEYS_USER_PLANET}
	 
	table_keys_serialize = table_keys.copy()
	del table_keys_serialize[PLANET_SIZE]
	
	def __init__(self, dbpath=":memory:"):
		self.conn = sqlite3.connect(dbpath)
		self.turns = {}
		self.max_turn = 0
		self.pending_actions = {}
						
		self.cur = self.conn.cursor()
			
		self.has_turn = [Db.PLANET, Db.USER_PLANET, Db.FLEET, Db.FLYING_FLEET, Db.FLYING_ALIEN_FLEET, Db.ALIEN_UNIT]
		#self.has_coord_keys = [Db.PLANET,  Db.FLYING_ALIEN_FLEET, Db.GARRISON_UNIT, Db.GARRISON_QUEUE_UNIT]
		
		for table, keys in self.table_keys.iteritems():
			if table in self.has_turn:
				self.table_keys[table] = tuple(list(keys)+['turn'])
				#keys = tuple(

		for table, keys in self.table_keys.iteritems():
			print '%s %s'%(table, keys)

		
		# table Db.FLYING_ALIEN_FLEET has no primary key
		self.primary_keys = {Db.USER:['id'], Db.OPEN_PLANET:['x','y', 'user_id'], Db.RACE:['id'], Db.PLAYER: ['player_id'],
		 Db.PLANET:['x','y'], Db.DIP:['owner_id', 'player_id'], Db.HW:['player_id'], Db.FLEET:['id'], Db.FLYING_FLEET:['id'], 
		 Db.UNIT:['id'],Db.GARRISON_QUEUE_UNIT:['id'],Db.ALIEN_UNIT:['id']
		 ,Db.PROTO:['id'], Db.PROTO_ACTION:['id'], Db.PLANET_SIZE:['x','y']}
		 
		 
		self.prepare()

	
	def set_turn(self, turn):
		self.max_turn = turn
		
	def prepare(self):
		self.cur = self.conn.cursor()
		cur = self.cur
		cur.execute("""create table if not exists %s(
				id integer PRIMARY KEY,
				name text not null,
				race_id integer not null,
				login text,
				turn integer default 0
				)"""%(Db.USER,))
				
		# each user may have it's own list of open planets ( consider Mobile Portal here )
		cur.execute("""create table if not exists %s(
				x integer(2) not null,
				y integer(2) not null,
				user_id integer not null,
				PRIMARY KEY (x, y, user_id))"""%(Db.OPEN_PLANET,))
				
		cur.execute("""create table if not exists %s(
				id integer PRIMARY KEY,
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
				)"""%(Db.RACE,))
				
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
				
		cur.execute("""create table if not exists %s(
				player_id integer PRIMARY KEY,
				name text,
				race_id integer
				)"""%(Db.PLAYER, ))

		#TODO; delete is_open field ( after several versions, when noone has it anymore )
		cur.execute("""create table if not exists %s(
				x integer(2) not null,
				y integer(2) not null,
				o integer(1),
				e integer(1),
				m integer(1),
				t integer(1),
				s integer(1),
				owner_id integer,
				name text,
				is_open integer(1),
				turn integer default 0,
				PRIMARY KEY (x, y))"""%(self.PLANET,))

		cur.execute("""create table if not exists %s(
				x integer(2) not null,
				y integer(2) not null,
				corruption integer(1),
				population integer,
				owner_id integer,
				is_open integer(1),
				turn integer default 0,
				PRIMARY KEY (x, y))"""%(self.USER_PLANET,))

				
		#what if approaching unknown fleet does not have an id?
		#id integer primary key,
		
		cur.execute("""create table if not exists %s(
				owner_id integer,
				player_id integer,
				status integer(1),
				PRIMARY KEY(owner_id, player_id)		
				)"""%(Db.DIP,))
		
		cur.execute("""create table if not exists %s(
				player_id integer PRIMARY KEY,
				hw_x integer(2),
				hw_y integer(2)
				)"""%(Db.HW,))
		
		cur.execute("""create table if not exists %s(
				id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				owner_id integer,
				name text,
				weight integer,
				is_hidden integer(1) default 0,
				times_spotted integer(1),
				turn integer(2) default 0
				)"""%(self.FLEET,))

		cur.execute("""create table if not exists %s(
				id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				owner_id integer,
				name text,
				from_x integer(2),
				from_y integer(2),
				arrival_turn integer(2),
				weight integer,
				is_hidden integer(1),
				times_spotted integer(1),
				in_transit integer(1),
				turn integer default 0
				)"""%(self.FLYING_FLEET, ))
						
		cur.execute("""create table if not exists %s(
				x integer(2) not null,
				y integer(2) not null,
				user_id interger,
				from_x integer(2),
				from_y integer(2),
				arrival_turn integer(2),
				weight integer,
				is_hidden integer(1),
				turn integer default 0
				)"""%(self.FLYING_ALIEN_FLEET,))
				
		
		cur.execute("""create table if not exists %s(
				id integer PRIMARY KEY,
				fleet_id integer default 0,
				class integer not null,
				hp integer not null,
				x integer(2),
				y integer(2)
				)"""%(self.UNIT,))
				
		
		cur.execute("""create table if not exists %s(
				id integer PRIMARY KEY,
				fleet_id integer not null,
				carapace integer not null,
				color integer(1),
				weight integer,
				class integer,
				turn integer default 0
				)"""%(self.ALIEN_UNIT,))
		
	
		cur.execute("""create table if not exists %s(
				id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				class integer not null,
				done integer
				)"""%(self.GARRISON_QUEUE_UNIT,))
		
		cur.execute("""create table if not exists %s(
				id integer PRIMARY KEY,
				owner_id integer not null,
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
				)"""%(Db.PROTO,))
				
		cur.execute("""create table if not exists %s(
				id integer primary key,
				type integer not null,
				proto_id integer not null,
				proto_owner_id integer not null,
				max_count integer,
				cost_people integer,
				cost_main integer,
				cost_second integer,
				cost_money integer,
				planet_can_be text
				)"""%(Db.PROTO_ACTION,))
		
		self.conn.commit()		
			
	def addObject(self, table_name, data, turn_n = None):
		keys=tuple(data.keys())
		
		#table_name = '%s_%s'%(table, turn_n) if turn_n else table
		try:
			#if str(table_name) == Db.PLANET:
			#	print 'insert old %s %s'%(table_name, data)
			self.cur.execute('insert or replace into %s%s values(%s)'%(table_name, keys,','.join('?'*len(keys))),tuple(data.values()))
			self.conn.commit()
		except sqlite3.Error, e:
			log.error('Error "%s", when executing: insert or replace into %s%s values%s'%(e, table_name,keys,tuple(data.values())))
			print traceback.format_stack()
	

	def get_objects_list(self, table, flt):
		'get single object from db'
		c = self.select(table, flt)
		rv = []
		for r in c.fetchall():
			rv.append( dict(zip(self.table_keys[table], r)) )
		return rv
	def iter_objects_list(self, table, flt = None, keys = None, join_info = None):
		'get single object from db'
		if not keys:
			keys = self.table_keys[table]
		c = self.select(table, flt, ['%s.%s'%(table, key) for key in keys], join_info)
		for r in c.fetchall():
			yield dict(zip(keys, r))
	
	def iter_join(self, table, table_join, key, key_join):
		c = self.conn.cursor()
		c.execute('select %s from %s JOIN %s ON %s=%s'%(table, table_join, key, key_join))
		keys = self.table_keys[table]
		for r in c.fetchall():
			yield dict(zip(keys, r))
	
	def select(self, table, flt = None, keys = None, join_info = None):
		if not keys:
			keys = self.table_keys[table]
		return self.query(table, 'select %s from'%(','.join(keys),), flt, keys, join_info)
		
	def query(self, table, query_type, flt, keys = None, join_info = None):
		#print 'query %s %s %s %s %s'%(table, query_type, flt, keys, join_info)
		if not keys:
			keys = self.table_keys[table]
			
		c = self.conn.cursor()
		
		suffix = ''
		if join_info:
			table_other = join_info[0]
			key_list = join_info[1]
			#key_my = join_info[1]
			#key_other = join_info[2]
			print 'join %s %s %s'%(table, flt, join_info)
			suffix = ' JOIN %s ON (%s)'%(table_other, ' AND '.join(['%s.%s=%s.%s'%(table, key_my, table_other, key_other) for key_my, key_other in key_list]))
			print suffix
			
		if not flt:
			try:
				c.execute('%s %s%s'%(query_type, table, suffix))
			except sqlite3.OperationalError as e:
				print 'Select %s from %s, error: %s'%(keys, table, e)
				raise

			return c
		
		where_conds = []
		values_dict = {}
		for cond, key_pairs in flt.iteritems():
			if cond == 'between':
				where_conds.append(' and '.join(['%s between :%s and :%s'%(key, key+'1', key+'2') for key in key_pairs]))
				for k,v in key_pairs.iteritems():
					values_dict[k+'1'] = v[0]
					values_dict[k+'2'] = v[1]
			elif cond == 'in':
				
				where_conds.append(' and '.join(['%s in (%s)'%(key, ','.join(to_str_list(value_list))) for key, value_list in key_pairs.iteritems()]))
				#print 'WHERE IN: %s'%(where_conds,)
				#for k,v in key_pairs.iteritems():
				#	values_dict[k+'1'] = v[0]
				#	values_dict[k+'2'] = v[1]
			elif cond == 'not in':
				#print 'check not in %s %s'%(cond, key_pairs)
				where_conds.append(' and '.join(['%s not in (%s)'%(key, ','.join(to_str_list(value_list))) for key, value_list in key_pairs.iteritems()]))
				print 'WHERE COND: %s, filter: %s'%(where_conds, flt)
			else:
				where_conds.append(' and '.join(['%s %s :%s'%(key, cond, key) for key in key_pairs.iterkeys()]))
				values_dict.update(key_pairs)
			
		where_str = ' and '.join(where_conds)
		s = 'select %s from %s%s WHERE %s'%(','.join(keys), table, suffix, where_str)
		#print '"%s" . items: %s'%(s, values_dict)
		try:
			c.execute(s, values_dict)
		except sqlite3.OperationalError as e:
			print 'Select %s with %s, error: %s'%(s, values_dict, e)
			raise
		except sqlite3.ProgrammingError as e:
			print 'Select %s with %s, error: %s'%(s, values_dict, e)
			raise
		return c
		
	def get_object(self, table, flt):
		'get single object from db'
		#self.cur.execute('select %s from %s where %s'%(','.join(data.keys()), table_name, ','.join(['%s=?'%(key,) for key in flt])), tuple(flt.values()))
		try:
			keys = self.table_keys[table]
			#print 'get %s %s'%(table, flt)
			r = self.select(table, flt, keys).fetchone()
		except TypeError as e:
			print 'get object failed: with %s %s, error: %s'%(table, flt, e)
			return None
		if not r:
			return None
		return dict(zip(keys, r))
	
	def smart_update_object(self, table_name, turn, p):
		if not table_name in self.primary_keys:
			return
		if table_name in self.has_turn:
			p['turn'] = turn
			keys = self.primary_keys[table_name]
			if not keys:
				self.set_object(table_name, p)
				return
			#try:
			self.update_object(table_name, {'=':dict(zip(keys, [p[key] for key in keys]))}, p)
			#except:
			#	print 'error in smart_update_object %s %s %s calling with %s'%(table_name, turn, p, {'=':dict(zip(keys, [p[key] for key in keys]))})
			#	raise
		else:
			s = 'insert or replace into %s (%s) values(%s)'%(table_name, ','.join(p.keys()), ','.join('?'*len(p)))
			#if str(table_name) == Db.PLANET:
			#	print 'insert %s %s %s'%(table_name, turn, p)
			self.cur.execute(s, tuple(p.values()))
			self.conn.commit()
			
		#if table_name in [Db.PLANET, Db.FLEET]:
	
	def set_object(self, table, data):
		if table in self.has_turn and not 'turn' in data:
			data['turn'] = self.max_turn
		try:
			self.cur.execute('insert or replace into %s (%s) values(%s)'%(table, ','.join(data.keys()), ','.join([':%s'%(key,) for key in data.keys()])), data)
			self.conn.commit()
		except sqlite3.OperationalError as e:
			print 'Update error: %s, table %s, filter %s, data %s'%(e, table, flt, data)
		
	def update_object(self, table, flt, data):
		if flt and 'turn' in data:
			obj = self.get_object(table, flt)
			if obj:
				t_cur = int(data['turn'])
				t_db = int(obj['turn'])
				if t_cur < t_db:
					return None
				#if t_cur ==  t_db:
		try:
			#if str(table_name) == Db.PLANET:
			#	print 'insert %s %s'%(table,p)
			self.cur.execute('insert or replace into %s (%s) values(%s)'%(table, ','.join(data.keys()), ','.join([':%s'%(key,) for key in data.keys()])), data)
		except sqlite3.OperationalError as e:
			print 'Update error: %s, table %s, filter %s, data %s'%(e, table, flt, data)
			c = self.select(table, {}, data.keys())
			print c.fetchone()
			raise
		self.conn.commit()
		return True
		
	def add_planet(self, turn, data):
		self.update_object(Db.PLANET, {'=':{'x':data['x'], 'y':data['y']}}, data)
	
	def set_planet_geo_size(self, data):
		x = int(data['x'])
		y = int(data['y'])
		self.cur.execute('select s from %s WHERE x=:x and y=:y'%(Db.PLANET,), (x,y))
		r = self.cur.fetchone()
		if r and r[0]:
			return
		s = int(data['s'])
		image = data['img']
		#if s == 0:
		#	return
		#print 'insert planet size %s:%s %s'%(x,y,s)
		s = s * 10
		if s == 0:
			s = 1
		self.cur.execute('insert or replace into planet_size (x,y,image,s) values(:x, :y, :image, :s)', (x,y,image,s))
		self.conn.commit()

	def delete_objects(self, table, flt, join_info = None):
		self.query(table, 'delete from', flt, join_info)
			
	def eraseObject(self, table_name, data, turn_n = None):
		#table_name = '%s_%s'%(table, turn_n) if turn_n else table
		try:
			self.cur.execute('delete from %s WHERE %s'%(table_name, ' AND '.join(data)))
			self.conn.commit()
		except sqlite3.Error, e:
			log.error('Error "%s", when executing: delete from %s WHERE %s'%(e, table_name, ' AND '.join(data)))
			print traceback.format_stack()
			
	def updateObject(self, table_name, flt, values, turn_n = None):
		#table_name = '%s_%s'%(table, turn_n) if turn_n else table
		try:
			self.cur.execute('update %s SET %s WHERE %s'%(table_name, ','.join(['%s=%s'%(k,v) for k,v in values.iteritems()]), ' AND '.join(flt)))
			self.conn.commit()
		except sqlite3.Error, e:
			log.error('Error "%s", when executing: delete from %s WHERE %s'%(e, table_name, ' AND '.join(data)))
			print traceback.format_stack()		
		

	#def getAnything(self):
		#self.cur.execute("select hw_x,hw_y from player where hw_x not null and hw_y not null")
		#r = self.cur.fetchone()
		#if r:
		#	print 'got place %s'%(r,)
		#	return int(r[0]),int(r[1])
	#	return 1,1

	def accounts(self):
		self.cur.execute('select login,name,id from player where login not null')
		for login,name,id in self.cur.fetchall():
			x,y = 1,1
			yield login,name,(int(x),int(y)),int(id)

	def getUserFleets(self, player_id):
		self.cur.execute('select x,y,id,name,arrival_turn,from_x,from_y from fleet where owner_id=:player_id',(player_id,))
		for x,y,id,name,arrival_turn,from_x, from_y in self.cur.fetchall():
			yield to_pos(x,y),id,name,arrival_turn,to_pos(from_x,from_y)

	def knownPlanets(self, area):
		x,y = area[0]
		zx = area[1][0]
		zy = area[1][1]
		self.cur.execute("select x,y,owner_id,name,s from planet")# where x>=:x and y>=:y and x<=:zx and y<=:zy", (x,y,zx,zy))
		for c in self.cur.fetchall():
			yield (int(c[0]),int(c[1])), c[2], c[3], c[4]
			
	def iterUsers(self):
		self.cur.execute('select id,name,race_id from user')
		for r in self.cur:
			yield r
	
	def add_pending_action(self, act_id, table, action_type, data):
		print 'add pending action %s %s %s %s'%(act_id, table, action_type, data)
		self.pending_actions.setdefault(act_id, []).append((table, action_type, data))
		
	def perform_pending_action(self, act_id, return_id = None):
		if act_id not in self.pending_actions:
			print 'action %s not in pending actions: %s'%(act_id, self.pending_actions.keys())
			return
		actions = self.pending_actions[act_id]
		for table, action_type, data in actions:
			if return_id and 'id' in data:
				data['id'] = return_id
				
			if action_type == 'insert':
				print 'exec pending insert %s %s %s'%(table, data, db.max_turn)
				self.addObject(table, data, db.max_turn)
			elif action_type == 'erase':
				print 'exec pending erase %s %s %s'%(table, data, db.max_turn)
				self.eraseObject(table, data, db.max_turn)
			elif action_type == 'update':
				flt, values = data
				print 'exec pending update %s %s %s %s'%(table, flt, values, db.max_turn)
				self.updateObject(table, flt, values, db.max_turn)
				
		
		del self.pending_actions[act_id]
	
	def cancel_pending_action(self, act_id):
		del self.pending_actions[act_id]
		
	def get_action_result(self, action_id):
		self.cur.execute("select return_id, is_ok from requested_action where id=:action_id", (action_id,))
		c = self.cur.fetchone()
		if not c:
			return None
		return int(c[0]), 1==int(c[1])
	
	def clear_action_result(self, user_id):
		self.cur.execute('delete from requested_action where user_id=:user_id', (user_id, ))
		
	
	def get_planet_owner(self, coord):
		x,y = coord
		self.cur.execute('select owner_id from %s_%s where x=:x and y=:y'%(Db.PLANET,), (x,y))
		r = self.cur.fetchone()
		if r and r[0]:
			return int(r[0])
		
		return None
	
	def set_open_planet(self, coord, user_id):
		x,y=coord
		self.cur.execute('insert or replace into %s(x,y,user_id) values(:x, :y, :user_id)'%(Db.OPEN_PLANET,), (x,y,user_id))
		self.conn.commit()

db = Db()	

def set_open_planet(coord, user_id):
	db.set_open_planet(coord, user_id)
	
def open_planets(user_id):
	for planet in items(Db.OPEN_PLANET, ['user_id=%s'%(user_id,)], ('x','y')):
		yield planet

def add_pending_action(act_id, table, action_type, data):
	db.add_pending_action(act_id, table, action_type, data)

def perform_pending_action(act_id, return_id):
	db.perform_pending_action(act_id, return_id)

def cancel_pending_action(self, act_id):
	db.cancel_pending_action(act_id)
	
def setTurn(turn_n):
	global db
	db.max_turn = turn_n

def getTurn():
	global db
	return db.max_turn

def setData(table, data, turn_n = None):
	global db
	#if not turn_n:
	#	print 'turnless %s %s'%(table, data)
	#print 'set data %s %s %s'%(table, data, turn_n)
	db.addObject(table, data, turn_n)

def set_planet_geo_size(data):
	global db
	db.set_planet_geo_size(data)
	
def prepareTurn(_):
	pass

def add_player(player):
	global db
	db.add_player(player)

def items(table_name, flt, keys, _ = None, verbose = False):
	global db
	c = db.conn.cursor()
	#table_name = '%s_%s'%(table, turn_n) if turn_n else table
	ws = ''
	if flt:
		ws = 'WHERE %s'%(' AND '.join(flt),)
	select_items = ','.join(keys) if keys else '*'
	s = 'select %s from %s %s'%(select_items, table_name, ws)
	if verbose:
		log.debug('sql: %s'%(s,))
	try:
		c.execute(s)
	except sqlite3.Error, e:
		print traceback.format_stack()
		log.error('Error %s, when executing: %s\ntable %s, filter: %s'%(e, s, table_name, flt,))
	for r in c:
		yield dict(zip(keys,r))

def itemsDiff(table_name, flt, keys, turn_start, turn_end):
	pass

def users(flt = None, keys = None):
	k = ('id','name','race_id', 'login') if not keys else keys
	for i in items('user', flt, k):
		yield i

def get_user_race(user_id):
	race_id = 0
	for u in users(['id=%s'%(user_id,)], ('race_id',)):
		race_id = int(u['race_id'])
	if race_id == 0:
		raise 'User %s race not found'%(user_id,)
		
	for r in items(Db.RACE, ['id=%s'%(race_id,)], ('id', 'temperature_delta',  'temperature_optimal',  'resource_nature',  'population_growth', 'resource_main', 'resource_secondary', 'modifier_fly', 'modifier_build_war', 'modifier_build_peace', 'modifier_science', 'modifier_stealth', 'modifier_detection', 'modifier_mining', 'modifier_price', 'name')):
		return r
	raise 'Race %s not found for user %s'%(race_id, user_id)
	
def get_planet_growth(user_id, coord):
	race = get_user_race(user_id)
	B1 = float(race['population_growth'])
	B2 = float(race['temperature_optimal'])
	B3 = float(race['temperature_delta'])
	B4 = 1 #governers count
	
	planet = get_planet(coord)
	if not planet or not 'o' in planet:
		return -1
	
	A1 = float(planet['t'])

	nature_value = int(planet[race['resource_nature']])
	main_value = int(planet[race['resource_main']])
	second_value = int(planet[race['resource_secondary']])
	
	A2 = float(nature_value)
	A4 = float(planet['s'])
	
	A5 = 5000 #colony or use 30000 for ark
	
	planet_population_growth = min(1, 2-A5/A4/1000) * min(1, 2-math.fabs(B2-A1)/B3) * A2 * 0.5 * (1+B1/100) / (B4+3)
	return planet_population_growth

def get_user_ids(flt = None):
	ids = []
	for u in items(Db.USER, flt, ('id',)):
		ids.append(u['id'])
	return ids

def players(flt = None, keys = None):
	k = ('player_id','name') if not keys else keys
	for i in items('player', flt, k):
		yield i

def get_player_name(player_id):
	for p in players(['player_id=%s'%(player_id,)]):
		return p['name']
		
	for u in users(['id=%s'%(player_id,)]):
		return u['name']
	
	return '[unknown id %s]'%(player_id,)
		
def alien_players():
	user_ids = get_user_ids()
	for p in players(['player_id not in (%s)'%(','.join([str(item) for item in user_ids]),)]):
		yield p

def planets(turn_n, flt, keys = None):
	k = ('x','y','owner_id','name','o','e','m','t','s') if not keys else keys
	for i in items('planet', flt, k, turn_n):
		yield i

def planets_size(flt):
	for i in items('planet_size', flt, ('x','y','s', 'image')):
		yield i

def get_planet_size(coord):
	serialization.load_geo_size_at(coord)
	for p in planets_size(['x=%s'%(coord[0],), 'y=%s'%(coord[1],)]):
		return p
			
def get_planet(coord):
	return db.get_object(Db.PLANET, {'=':{'x':coord[0], 'y':coord[1]}})
	
	#for pl in planets(getTurn(), ['x=%s'%(coord[0],), 'y=%s'%(coord[1],)]):
	#	return pl
	#return None

def fleets(turn_n, flt, keys = None):
	k = ('id', 'name', 'x','y','owner_id', 'is_hidden') if not keys else keys
	for i in items('fleet', flt, k, turn_n):
		yield i

def flyingFleets(turn_n, flt, keys = None):
	k = ('id', 'x','y','owner_id', 'in_transit', 'from_x', 'from_y', 'is_hidden') if not keys else keys
	for i in items(Db.FLYING_FLEET, flt, k, turn_n):
		yield i
		
def prototypes(flt, keys = None):
	k = ('id', 'class', 'carapace', 'weight', 'color', 'hp', 'name', 'fly_range') if not keys else keys
	for i in items(Db.PROTO, flt, k):
		yield i

def proto_actions(flt, keys = None):
	k = ('id', 'type', 'proto_id', 'proto_owner_id', 'max_count', 'cost_people', 'cost_main', 'cost_second', 'cost_money', 'planet_can_be') if not keys else keys
	for i in items(Db.PROTO_ACTION, flt, k):
		yield i
		
def units(turn_n, flt, keys = None):
	k = ('id', 'fleet_id', 'class', 'hp') if not keys else keys
	for unit in items(Db.UNIT, flt, k, turn_n):
		yield unit

def get_units(turn_n, flt, keys = None):
	us = []
	for u in units(turn_n,flt, keys):
		us.append(u)
	return us

def garrison_units(turn_n, flt, keys = None):
	#k = ('id', 'class', 'hp') if not keys else keys
	for unit in items(Db.GARRISON_UNIT, flt, k, turn_n):
		yield unit
						
def alienUnits(turn_n, flt, keys = None):
	k = ('id', 'fleet_id', 'class', 'carapace', 'color', 'weight') if not keys else keys
	for unit in items(Db.ALIEN_UNIT, flt, k, turn_n):
		yield unit

def get_unit_prototype(turn_n, unit_id):
	for unit in units(turn_n, ['id=%s'%(unit_id,)]):
		return get_prototype(unit['class'])
			
def get_prototype(bc, keys = None):
	for proto in prototypes(['id=%s'%(bc,),], keys):
		return proto

def get_units_class(turn_n, flt):
	cls = []
	print 'class with filter %s'%(flt,)
	for proto in prototypes(flt):
		print 'got proto %s'%(proto,)
		cls.append( proto['id'] )
	return cls

def get_action_result(action_id):
	return db.get_action_result(action_id)

def clear_action_result(user_id):
	db.clear_action_result(user_id)

def nextFleetTempId():
	return 0

def getUserName(user_id):
	for name in users(['id=%d'%(int(user_id),)], ('name',)):
		return name['name']
	
	for name in players(getTurn(), ['player_id=%d'%(int(user_id),)], ('name',)):
		return name['name']
		
	return '<? %d>'%(user_id,)

def getUserHw(user_id, turn_n = None):
	t = turn_n if turn_n else getTurn()
	for u in items('hw', ['player_id=%s'%(user_id,)], ('hw_x', 'hw_y'), t):
		return int(u['hw_x']), int(u['hw_y'])
	print 'hw for user %s turn %s not found'%(user_id, t)
	return 550,550

def setSqlValues(data):
	d = {}
	for k,v in data.items():
		print '%s="%s" ( %s )'%(k,v,type(v))
		if not v:
			v = 'NULL'		
		elif isinstance(v, str) or isinstance(v, unicode):
			if v=='':
				v='NULL'
			else:
				v = "'%s'"%(v,)
		d[k]=v
	return d
			
def updateRow(table, conditions, data):
	global db
	c = db.conn.cursor()
	#d = setSqlValues(data)
	keys = []
	values = []
	for k,v in data.iteritems():
		if not v or v=='':
			continue
		keys.append(k)
		values.append(v)
		
	s = ', '.join( ['%s=?'%(p,) for p in keys] )
	tf = 'update %s SET %s WHERE %s'%(table, s, ' AND '.join(conditions))
	#print '%s'%(tf,)
	c.execute(tf, tuple(values)) #'update %s SET %s WHERE %s'%(table, , ' AND '.join(conditions))

def setPlanetInfo(data):
	x,y = data['x'],data['y']
	conditions = ['x=%s'%(x,),'y=%s'%(y,)]
	found = False
	for p in planets(conditions):
		updateRow('planet', conditions, data)
		found = True
	if not found:
		setData('planet', data)
	

def smartUpdate(table, conds, data, turn_n = None):
	for item in items(table, conds, data.keys(), turn_n):
		return
	setData(table, data, turn_n)
	

def joinInfo(old, new_info):
	joined = new_info.copy()
	for k,v in old.iteritems():
		if not k in joined:
			joined[k] = v
			continue
		composed_value = joined[k]
		if not composed_value or composed_value == '':
			joined[k] = v
	return joined

def setPlanet(data, turn_n = None):
	conds = ['x=%s'%(data['x'],), 'y=%s'%(data['y'],)]
	pl = {}
	for planet in planets(turn_n, conds):
		pl = planet
		break
		
	if not pl:
		setData('planet', data, turn_n)
		return
	
	if pl == data:
		return
	
	joinedData = joinInfo(data, pl)
	if joinedData != pl:
		return updateRow(Db.PLANET, conds, joinedData)

def all_ownedUnits(turn_n, coord):
	conds = ['x=%s'%(coord[0],), 'y=%s'%(coord[1],)]
	for fl in fleets(turn_n, conds):
		for unit in units(turn_n, ['fleet_id=%d'%(fl['id'],)]):
			yield fl,unit
			
def all_alienUnits(turn_n, coord):
	conds = ['x=%s'%(coord[0],), 'y=%s'%(coord[1],)]
	for fl in fleets(turn_n, conds):
		for unit in alienUnits(turn_n, ['fleet_id=%d'%(fl['id'],)]):
			yield fl,unit

def has_any_buildings(turn_n, coord, buildings):
	for gu in garrison_units(turn_n, ['x=%s'%(coord[0],), 'y=%s'%(coord[1],), 'class in (%s)'%(','.join([str(bid) for bid in buildings]),)]):
		return True
	return False

def has_all_buildings(turn_n, coord, buildings):
	for bid in buildings:
		is_found = False
		for gu in garrison_units(turn_n, ['x=%s'%(coord[0],), 'y=%s'%(coord[1],), 'class=%s'%(bid,)]):
			is_found = True
			break
		if not is_found:
			return False
	return True

def is_planet(coord):
	planet_size = get_planet_size(coord)
	return planet_size and planet_size != 11

def eraseObject(table, data, turn_n = None):
	db.eraseObject(table, data, turn_n)

def get_fleet_speed_range(fleet_id):
	fleet = None
	for f in fleets(getTurn(), ['id=%s'%(fleet_id,)]):
		fleet = f
		break
	if not fleet:
		return None,None
		
	min_speed = 99999
	min_range = 99999
	for u in units(getTurn(), ['fleet_id=%s'%(fleet_id,)]):
		proto = get_prototype(u['class'], ('is_spaceship', 'fly_speed', 'fly_range'))
		if int(proto['is_spaceship'])!=1:
			continue
			
		speed = float(proto['fly_speed'])
		rnge = float(proto['fly_range'])
		min_speed = min(speed, min_speed)
		min_range = min(rnge, min_range)
		
	return min_speed, min_range

def filter_coord(coord):
	return ['x=%s'%(coord[0],), 'y=%s'%(coord[1],)]
