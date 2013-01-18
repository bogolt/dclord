import sqlite3
#from objects import Planet, Fleet, Unit, Player, Proto
import logging
import sys, traceback

def to_pos(a,b):
	return int(a),int(b)

log = logging.getLogger('dclord')

class Db:
	PLANET = 'planet'
	USER = 'user'
	FLEET = 'fleet'
	UNIT = 'unit'
	ALIENT_UNIT = 'alien_unit'
	INCOMING_FLEET = 'incoming_fleet'
	GARRISON_UNIT = 'garrison_unit'
	GARRISON_QUEUE_UNIT = 'garrison_queue_unit'
	
	def __init__(self, dbpath=":memory:"):
		self.conn = sqlite3.connect(dbpath)
		self.turns = {}
		self.max_turn = 0
				
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

		cur.execute("""create table if not exists user(
				id integer primary key,
				name text not null,
				race_id integer not null,
				login text
				)""")
				
		#what if approaching unknown fleet does not have an id?
		#id integer primary key,

		cur.execute("""create table if not exists player_%s(
				player_id integer primary key,
				name text,
				race_id integer
				)"""%(turn_n,))
		
		cur.execute("""create table if not exists dip_%s(
				owner_id integer,
				player_id integer,
				status integer(1)				
				)"""%(turn_n,))
		
		cur.execute("""create table if not exists hw_%s(
				player_id integer primary key,
				hw_x integer(2),
				hw_y integer(2)
				)"""%(turn_n,))
		
		cur.execute("""create table if not exists %s_%s(
				id integer primary key,
				x integer(2) not null,
				y integer(2) not null,
				owner_id integer,
				name text,
				weight integer,
				is_hidden integer(1),
				times_spotted integer(1),
				turn integer(2)
				)"""%(self.FLEET, turn_n))

		
		cur.execute("""create table if not exists %s_%s(
				id integer,
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
				turn integer(2),
				temp_id integer
				)"""%(self.INCOMING_FLEET, turn_n))
				
		
		cur.execute("""create table if not exists %s_%s(
				id integer primary key,
				fleet_id integer not null,
				class integer not null,
				hp integer not null
				)"""%(self.UNIT, turn_n))
				
		
		cur.execute("""create table if not exists %s_%s(
				id integer primary key,
				fleet_id integer not null,
				carapace integer not null,
				color integer(1),
				weight integer,
				class integer
				)"""%(self.ALIENT_UNIT, turn_n))

	
		cur.execute("""create table if not exists %s_%s(
				id integer primary key,
				x integer(2) not null,
				y integer(2) not null,
				class integer not null,
				hp integer not null
				)"""%(self.GARRISON_UNIT, turn_n))
		
	
		cur.execute("""create table if not exists %s_%s(
				id integer primary key,
				x integer(2) not null,
				y integer(2) not null,
				class integer not null,
				done integer
				)"""%(self.GARRISON_QUEUE_UNIT, turn_n))
		
		cur.execute("""create table if not exists proto(
				id integer,
				owner_id integer,
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
				id integer,
				proto_id integer,
				proto_owner_id integer,
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
			

db = Db()	

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
		log.error('Error %s, when executing: %s'%(e, s))
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

def fleets(turn_n, flt, keys = None):
	k = ('id', 'x','y','owner_id', 'is_hidden') if not keys else keys
	for i in items('fleet', flt, k, turn_n):
		yield i

def flyingFleets(turn_n, flt, keys = None):
	k = ('id', 'temp_id', 'x','y','owner_id', 'from_x', 'from_y', 'is_hidden') if not keys else keys
	for i in items('incoming_fleet', flt, k, turn_n):
		yield i
		
def prototypes(flt, keys = None):
	k = ('id', 'class', 'carapace', 'weight', 'color', 'hp', 'name') if not keys else keys
	for i in items('proto', flt, k):
		yield i
		
def units(turn_n, flt, keys = None):
	k = ('id', 'fleet_id', 'class', 'hp') if not keys else keys
	for unit in items('unit', flt, k, turn_n):
		yield unit
				
def alienUnits(turn_n, flt, keys = None):
	k = ('id', 'fleet_id', 'class', 'carapace', 'color', 'weight') if not keys else keys
	for unit in items(Db.ALIENT_UNIT, flt, k, turn_n):
		yield unit
		
def nextFleetTempId():
	return 0

def getUserName(user_id):
	for name in users(['id=%d'%(int(user_id),)], ('name',)):
		return name['name']
		
	for name in users():
		print 'user %s'%(name,)
	return '<unknown>'

def getUserHw(user_id, turn_n):
	for u in items('hw', ['player_id=%s'%(user_id,)], ('hw_x', 'hw_y'), turn_n):
		return int(u['hw_x']), int(u['hw_y'])
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
