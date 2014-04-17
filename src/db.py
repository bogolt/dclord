import sqlite3
import logging
import sys, traceback
import serialization

def to_pos(a,b):
	return int(a),int(b)

log = logging.getLogger('dclord')

class Db:
	PLANET = 'planet'
	USER = 'user'
	FLEET = 'fleet'
	UNIT = 'unit'
	ALIEN_UNIT = 'alien_unit'
	FLYING_FLEET = 'flying_fleet'
	FLYING_ALIEN_FLEET = 'flying_alien_fleet'
	#ALIEN_FLEET = 'alien_fleet'
	GARRISON_UNIT = 'garrison_unit'
	GARRISON_QUEUE_UNIT = 'garrison_queue_unit'
	
	def __init__(self, dbpath=":memory:"):
		self.conn = sqlite3.connect(dbpath)
		self.turns = {}
		self.max_turn = 0
		self.pending_actions = {}
				
		self.cur = self.conn.cursor()

	
	def close(self):
		self.conn.close()
		self.max_turn = 0
		
		self.init()

	def init(self, turn_n):
		self.cur = self.conn.cursor()
		cur = self.cur
		
		turn_n = int(turn_n)
		
		self.max_turn = max(self.max_turn, turn_n)
		
		log.info('db init turn %s'%(turn_n,))
		
		# check if turn is known and catched
		if turn_n in self.turns and self.turns[turn_n]:
			log.info('turn %s is alredy known to db'%(turn_n,))
			return
			
		# set turn exists
		self.turns[turn_n] = True
		log.info('creating tables for turn %s, max turn is %s'%(turn_n, self.max_turn))
		
		cur.execute("""create table if not exists %s_%s(
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
				PRIMARY KEY (x, y))"""%(self.PLANET, turn_n))
				
		cur.execute("""create table if not exists planet_size(
				x integer(2) not null,
				y integer(2) not null,
				s integer(1),
				image integer(1),
				PRIMARY KEY (x, y))""")
		
		# each user may have it's own list of open planets ( consider Mobile Portal here )
		cur.execute("""create table if not exists open_planets(
				x integer(2) not null,
				y integer(2) not null,
				user_id integer not null,
				PRIMARY KEY (x, y, user_id))""")

		cur.execute("""create table if not exists user(
				id integer PRIMARY KEY,
				name text not null,
				race_id integer not null,
				login text
				)""")
				
				
		cur.execute("""create table if not exists requested_action(
				id integer PRIMARY KEY,
				user_id integer not null,
				return_id integer default 0,
				is_ok integer default 0
				)""")
				
		#what if approaching unknown fleet does not have an id?
		#id integer primary key,

		cur.execute("""create table if not exists player_%s(
				player_id integer PRIMARY KEY,
				name text,
				race_id integer
				)"""%(turn_n,))
		
		cur.execute("""create table if not exists dip_%s(
				owner_id integer,
				player_id integer,
				status integer(1)				
				)"""%(turn_n,))
		
		cur.execute("""create table if not exists hw_%s(
				player_id integer PRIMARY KEY,
				hw_x integer(2),
				hw_y integer(2)
				)"""%(turn_n,))
		
		cur.execute("""create table if not exists %s_%s(
				id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				owner_id integer,
				name text,
				weight integer,
				is_hidden integer(1) default 0,
				times_spotted integer(1),
				turn integer(2)
				)"""%(self.FLEET, turn_n))

		cur.execute("""create table if not exists %s_%s(
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
				in_transit integer(1)
				)"""%(self.FLYING_FLEET, turn_n))
						
		cur.execute("""create table if not exists %s_%s(
				x integer(2) not null,
				y integer(2) not null,
				user_id interger,
				from_x integer(2),
				from_y integer(2),
				arrival_turn integer(2),
				weight integer,
				is_hidden integer(1)
				)"""%(self.FLYING_ALIEN_FLEET, turn_n))
				
		
		cur.execute("""create table if not exists %s_%s(
				id integer PRIMARY KEY,
				fleet_id integer not null,
				class integer not null,
				hp integer not null
				)"""%(self.UNIT, turn_n))
				
		
		cur.execute("""create table if not exists %s_%s(
				id integer PRIMARY KEY,
				fleet_id integer not null,
				carapace integer not null,
				color integer(1),
				weight integer,
				class integer
				)"""%(self.ALIEN_UNIT, turn_n))

	
		cur.execute("""create table if not exists %s_%s(
				id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				class integer not null,
				hp integer not null
				)"""%(self.GARRISON_UNIT, turn_n))
		
	
		cur.execute("""create table if not exists %s_%s(
				id integer PRIMARY KEY,
				x integer(2) not null,
				y integer(2) not null,
				class integer not null,
				done integer
				)"""%(self.GARRISON_QUEUE_UNIT, turn_n))
		
		cur.execute("""create table if not exists proto(
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
				)""")
				
		cur.execute("""create table if not exists proto_action(
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
				)""")
		
	def addObject(self, table, data, turn_n = None):
		keys=tuple(data.keys())
		
		table_name = '%s_%s'%(table, turn_n) if turn_n else table
		try:
			self.cur.execute('insert or replace into %s%s values(%s)'%(table_name, keys,','.join('?'*len(keys))),tuple(data.values()))
			self.conn.commit()
		except sqlite3.Error, e:
			log.error('Error "%s", when executing: insert or replace into %s%s values%s'%(e, table_name,keys,tuple(data.values())))
			print traceback.format_stack()
	
	def set_planet_geo_size(self, data):
		x = int(data['x'])
		y = int(data['y'])
		self.cur.execute('select s from planet_%s WHERE x=:x and y=:y'%(self.max_turn,), (x,y))
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

	def eraseObject(self, table, data, turn_n = None):
		table_name = '%s_%s'%(table, turn_n) if turn_n else table
		try:
			self.cur.execute('delete from %s WHERE %s'%(table_name, ' AND '.join(data)))
			self.conn.commit()
		except sqlite3.Error, e:
			log.error('Error "%s", when executing: delete from %s WHERE %s'%(e, table_name, ' AND '.join(data)))
			print traceback.format_stack()
			
	def updateObject(self, table, flt, values, turn_n = None):
		table_name = '%s_%s'%(table, turn_n) if turn_n else table
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
	
	def getAreaPlanets(self, leftTop=(0,0), size=(1000,1000)):
		cx,cy=leftTop
		zx=cx+size[0]
		zy=cy+size[1]
		cur = self.cur
		cur.execute("select x,y,owner_id,name,s from planet where x>=:cx and y>=:cy and x<=:zx and y<=:zy", (cx,cy,zx,zy))
		pl = {}
		for c in cur.fetchall():
			coord = (c[0], c[1])
			p = Planet(coord, self.getPlayer(c[2]), c[3])
			if c[4]:
				p.geo['s']=c[4]
			pl[coord] = p
		
		self.cur.execute("select x,y,garrison_unit.id,garrison_unit.class,garrison_unit.hp from user_planet,garrison_unit on garrison_unit.garrison_id=user_planet.id where x>=:cx and y>=:cy and x<=:zx and y<=:zy", (cx,cy,zx,zy))
		for r in self.cur.fetchall():
			u = Unit(r[2], self.getProto(r[3]), r[4])
			pl[(r[0],r[1])].units[u.id] = u
					
		return pl

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
			print 'got user %s'%(r,)
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
		self.cur.execute('select owner_id from planet_%s where x=:x and y=:y'%self.max_turn, (x,y))
		r = self.cur.fetchone()
		if r and r[0]:
			return int(r[0])
		
		return None
	
	def set_open_planet(self, coord, user_id):
		x,y=coord
		self.cur.execute('insert or replace into open_planets (x,y,user_id) values(:x, :y, :user_id)', (x,y,user_id))
		self.conn.commit()

db = Db()	

def set_open_planet(coord, user_id):
	db.set_open_planet(coord, user_id)
	
def open_planets(user_id):
	for planet in items('open_planets', ['user_id=%s'%(user_id,)], ('x','y')):
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
	
def prepareTurn(turn_n):
	global db
	db.init(turn_n)

def add_player(player):
	global db
	db.add_player(player)

def items(table, flt, keys, turn_n = None, verbose = False):
	global db
	c = db.conn.cursor()
	table_name = '%s_%s'%(table, turn_n) if turn_n else table
	ws = ''
	if flt:
		ws = 'WHERE %s'%(' AND '.join(flt),)
	s = 'select %s from %s %s'%(','.join(keys), table_name, ws)
	if verbose:
		log.debug('sql: %s'%(s,))
	try:
		c.execute(s)
	except sqlite3.Error, e:
		print traceback.format_stack()
		log.error('Error %s, when executing: %s\ntable %s, filter: %s, turn %s'%(e, s, table, flt, turn_n))
	for r in c:
		yield dict(zip(keys,r))

def itemsDiff(table_name, flt, keys, turn_start, turn_end):
	pass

def users(flt = None, keys = None):
	k = ('id','name','race_id') if not keys else keys
	for i in items('user', flt, k):
		yield i

def players(turn_n, flt = None, keys = None):
	k = ('player_id','name') if not keys else keys
	for i in items('player', flt, k, turn_n):
		yield i

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
	for pl in planets(getTurn(), ['x=%s'%(coord[0],), 'y=%s'%(coord[1],)]):
		return pl
	return None

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
	for i in items('proto', flt, k):
		yield i

def proto_actions(flt, keys = None):
	k = ('id', 'type', 'proto_id', 'proto_owner_id', 'max_count', 'cost_people', 'cost_main', 'cost_second', 'cost_money', 'planet_can_be') if not keys else keys
	for i in items('proto_action', flt, k):
		yield i
		
def units(turn_n, flt, keys = None):
	k = ('id', 'fleet_id', 'class', 'hp') if not keys else keys
	for unit in items('unit', flt, k, turn_n):
		yield unit

def get_units(turn_n, flt, keys = None):
	us = []
	for u in units(turn_n,flt, keys):
		us.append(u)
	return us

def garrison_units(turn_n, flt, keys = None):
	k = ('id', 'class', 'hp') if not keys else keys
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
		return updateRow('planet_%s'%(turn_n,), conds, joinedData)

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
