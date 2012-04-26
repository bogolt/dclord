import sqlite3
#from objects import Planet, Fleet, Unit, Player, Proto
import logging

def to_pos(a,b):
	return int(a),int(b)

log = logging.getLogger('dclord')

class Db:
	def __init__(self, dbpath=":memory:"):
		self.conn = sqlite3.connect(dbpath)		
		
		self.cur = self.conn.cursor()
		self.cur.execute("""create table if not exists turn(
				n integer not null,
				login text not null
				)""")
				
		self.init()

	def prepareTables(user_login, turn_n):
		self.cur.execute("""create table if not exists planet_%d(
				x integer(2) not null,
				y integer(2) not null,
				owner_id integer,
				name text,
				is_open integer(1)
				)"""%(turn_n,))
				
		self.cur.execute("""create table if not exists fleet_%d(
				id integer primary key,
				x integer(2) not null,
				y integer(2) not null
				)""")

		cur.execute("""create table if not exists flying_fleet(
				id integer,
				x integer(2) not null,
				y integer(2) not null,
				from_x integer(2),
				from_y integer(2),
				arrival_turn integer(2),
				temp_id integer
				)""")
				
		cur.execute("""create table if not exists unit(
				id integer primary key,
				fleet_id integer not null,
				class integer not null,
				hp integer not null
				)""")
				
		cur.execute("""create table if not exists alien_unit(
				id integer primary key,
				fleet_id integer not null,
				carapace integer not null,
				color integer(1),
				weight integer,
				class integer
				)""")

		cur.execute("""create table if not exists garrison_unit(
				id integer primary key,
				x integer(2) not null,
				y integer(2) not null,
				class integer not null,
				hp integer not null
				)""")
		
		cur.execute("""create table if not exists garrison_queue_unit(
				id integer primary key,
				x integer(2) not null,
				y integer(2) not null,
				class integer not null,
				done integer
				)""")
	
	def init(self):
		self.cur = self.conn.cursor()
		cur = self.cur

		cur.execute("""create table if not exists planet(
				x integer(2) not null,
				y integer(2) not null,
				o integer(1),
				e integer(1),
				m integer(1),
				t integer(1),
				s integer(1),
				owner_id integer,
				name text,
				turn integer(2),
				is_open integer(1)
				)""")
		#corruption integer,
		#population integer

		cur.execute("""create table if not exists user(
				id integer primary key,
				name text not null,
				race_id integer not null,
				
				hw_x integer(2),
				hw_y integer(2),
				turn integer,
				login text
				)""")

		cur.execute("""create table if not exists player(
				id integer primary key,
				name text not null,
				race_id integer not null
				)""")
				
		#what if approaching unknown fleet does not have an id?
		#id integer primary key,
		cur.execute("""create table if not exists fleet(
				id integer primary key,
				x integer(2) not null,
				y integer(2) not null,
				owner_id integer,
				name text,
				weight integer,
				is_hidden integer(1),
				times_spotted integer(1),
				turn integer(2)
				)""")

		cur.execute("""create table if not exists incoming_fleet(
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
				)""")
				
		cur.execute("""create table if not exists unit(
				id integer primary key,
				fleet_id integer not null,
				class integer not null,
				hp integer not null
				)""")
				
		cur.execute("""create table if not exists alien_unit(
				id integer primary key,
				fleet_id integer not null,
				carapace integer not null,
				color integer(1),
				weight integer,
				class integer
				)""")

		cur.execute("""create table if not exists garrison_unit(
				id integer primary key,
				x integer(2) not null,
				y integer(2) not null,
				class integer not null,
				hp integer not null
				)""")
		
		cur.execute("""create table if not exists garrison_queue_unit(
				id integer primary key,
				x integer(2) not null,
				y integer(2) not null,
				class integer not null,
				done integer
				)""")
		
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
				
		cur.execute("""create table if not exists proto_actions(
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
		
	def addObject(self, object, data):
		keys=tuple(data.keys())
		
		try:
			self.cur.execute('insert or replace into %s%s values(%s)'%(object,keys,','.join('?'*len(keys))),tuple(data.values()))
			self.conn.commit()
		except sqlite3.Error, e:
			log.error('Error %s, when executing: insert into %s%s values%s'%(e, object,keys,tuple(data.values())))
			

	def getAnything(self):
		self.cur.execute("select hw_x,hw_y from player where hw_x not null and hw_y not null")
		r = self.cur.fetchone()
		if r:
			print 'got place %s'%(r,)
			return int(r[0]),int(r[1])
		return 1,1

	def accounts(self):
		self.cur.execute('select login,name,hw_x,hw_y,id from player where login not null')
		for login,name,x,y,id in self.cur.fetchall():
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
		self.cur.execute('select id,name,hw_x,hw_y,race_id from user')
		for r in self.cur:
			print 'got user %s'%(r,)
			yield r
			

db = Db()

def setData(table, data):
	global db
	db.addObject(table, data)

def add_player(player):
	global db
	db.add_player(player)

def items(table_name, flt, keys):
	global db
	c = db.conn.cursor()
	ws = ''
	if flt:
		ws = 'WHERE %s'%(' AND '.join(flt),)
	c.execute('select %s from %s %s'%(','.join(keys), table_name, ws))
	for r in c:
		yield dict(zip(keys,r))

def users(flt = None, keys = None):
	k = ('id','name','hw_x','hw_y','race_id') if not keys else keys
	for i in items('user', flt, k):
		yield i

def planets(flt, keys = None):
	k = ('x','y','owner_id','o','e','m','t','s') if not keys else keys
	for i in items('planet', flt, k):
		yield i

def fleets(flt, keys = None):
	k = ('id', 'x','y','owner_id', 'is_hidden') if not keys else keys
	for i in items('fleet', flt, k):
		yield i

def flyingFleets(flt, keys = None):
	k = ('id', 'temp_id', 'x','y','owner_id', 'from_x', 'from_y', 'is_hidden') if not keys else keys
	for i in items('incoming_fleet', flt, k):
		yield i

def nextFleetTempId():
	return 0

#d = Db()
#d.prepare('test', 45)
