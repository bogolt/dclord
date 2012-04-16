import sqlite3
#from objects import Planet, Fleet, Unit, Player, Proto
import logging

def to_pos(a,b):
	return int(a),int(b)

class Db:
	def __init__(self, dbpath=":memory:"):
		self.conn = sqlite3.connect(dbpath)
		self.cur = self.conn.cursor()
		
		self.planet = {}
		self.fleet = {}
		self.player = {}
		self.proto = {}
		self.preloadArea = None
		
		cur = self.cur

		cur.execute("""create table if not exists planet(
				x integer not null,
				y integer not null,
				o integer(1),
				e integer(1),
				m integer(1),
				t integer(1),
				s integer(1),
				owner_id integer,
				name text,
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
				from_x integer,
				from_y integer,
				arrival_turn integer(2),
				weight integer,
				is_hidden integer(1),
				times_spotted integer(1)
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
				id integer primary key,
				carapace integer,
				weight integer,
				color integer(1) default 0
				)""")
		
	def addObject(self, object, data):
		keys=tuple(data.keys())
		#print 'insert into %s%s values%s'%(object,keys,tuple(data.values()))
		self.cur.execute('insert or replace into %s%s values(%s)'%(object,keys,','.join('?'*len(keys))),tuple(data.values()))
		self.conn.commit()
			
	def isCached(self, pos):
		if not self.preloadArea:
			return False
		lt,rb = self.preloadArea 
		return pos[0] >= lt[0] and pos[1] >= lt[1] and pos[0] <= rb[0] and pos[1] <= rb[1] 
	
	def getPlanet(self, x,y):
		c = x,y
		if c in self.planet.keys():
			return self.planet[c]
		
		if self.isCached(c):
			return None

		self.cur.execute("select x,y,owner_id,name from planet where x=:x and y=:y",(x,y))
		r = self.cur.fetchone()
		if not r:
			return None
		return Planet((r[0],r[1]), self.getPlayer(r[2]), r[3])
		
	def getUserPlanetId(self, x, y):
		self.cur.execute("select id from user_planet where x=:x and y=:y",(x,y))
		r = self.cur.fetchone()
		if not r:
			return None
		return r[0]
	
	def getFleets(self, x,y):
		c = x,y
		if c in self.fleet.keys():
			return self.fleet[c]
		
		if self.isCached(c):
			return None
		
		self.cur.execute("select owner_id,name,from_x,from_y,tta,id from fleet where (x=:x and y=:y)",(x,y))
		r = self.cur.fetchall()
		if not r:
			return {}
				
		fleets = []
		for f in r:
			posFrom = None
			if f[2] and f[3]:
				posFrom = f[2],f[3]
			fleets.append(Fleet((x,y), f[5], self.getPlayer(f[0]), f[1], posFrom, f[4]))
		return fleets
	
	def getObjects(self, x,y):
		c = x,y
		
		p,f=None,None
		if c in self.planet.keys():
			p = self.planet[c]
		if c in self.fleet.keys():
			f = self.fleet[c]
		
		if p or f:
			return p,f
		
		if self.isCached(c):
			return None,None

		planet = self.getPlanet(x, y)
		fleets = self.getFleets(x, y)
		return planet,fleets
		
	def getNotEmptyCoord(self):
		if self.planet:
			return self.planet[0]
		
		self.cur.execute("select x,y from planet limit 1")
		r = self.cur.fetchone()
		if not r:
			return None
		return r[0],r[1]

	def getPlayerByLogin(self, login):
		p = [p for _,p in self.player.iteritems() if p.login==login]
		if p:
			return p
		#look in db
		self.cur.execute("select id,name,hw_x,hw_y from player where login=:login",(login,))
		r = self.cur.fetchone()
		
		#or should we add empty user to the list ?
		if not r:
			log.error('player (login: %s) not found'%(login,))
			return None
		p = Player(r[0], r[1], login)
		if r[2] and r[3]:
			p.hw = to_pos(r[2],r[3])
		self.player[p.id] = p	
		return p		
			
	def getAccountsList(self):
		self.cur.execute("select name,hw_x,hw_y from player")
		r = self.cur.fetchall()
		plist = []
		for name,x,y in r:
			if x and y:
				hwx = int(x)
				hwy = int(y)
				print 'append %s as %d %d'%(name, hwx, hwy)
				plist.append( (name,(hwx, hwy)))
		return plist		
	
	def getPlayer(self, id):
		if id in self.player.keys():
			return self.player[id] 
		
		self.cur.execute("select name,hw_x,hw_y,login from player where id=:id",(id,))
		r = self.cur.fetchone()
		if not r:
			return None
		p = Player(id, r[0], r[3])
		if r[1] and r[2]:
			p.hw = r[1],r[2]
		
		self.player[id] = p
		return p

	#TODO: how will it work for corner coords? -> split into 4 prepares
	def prepare(self, pos, size):
		self.planet.update(self.getAreaPlanets(pos, size))
		self.fleet.update(self.getAreaFleets(pos, size))
		self.preloadArea = pos,(pos[0]+size[0],pos[1]+size[1])

	def getAreaFleets(self, leftTop=(0,0), size=(1000,1000)):
		cx,cy=leftTop
		zx=cx+size[0]
		zy=cy+size[1]
		self.cur.execute("select x,y,id,owner_id,name,from_x,from_y,tta from fleet where (x>=:cx and y>=:cy and x<=:zx and y<=:zy) or (from_x>=:cx and from_y>=:cy and from_x<=:zx and from_y<=:zy)", (cx,cy,zx,zy))
		fl = {}
		for c in self.cur.fetchall():
			coord = (c[0], c[1])
			posFrom = None
			if c[5] and c[6]:
				posFrom = c[5],c[6]
			f = Fleet(coord, c[2], self.getPlayer(c[3]), c[4], posFrom, c[7])
			if coord in fl.keys():
				fl[coord].append(f)
			else:
				fl[coord] = [f]
		ids = []
		for fleet in fl.values():
			ids += [unit.id for unit in fleet]
		st = 'select unit.id,class,hp from unit where fleet_id in (%s)'%(','.join([str(id) for id in ids]),)
		self.cur.execute(st)
		for u in self.cur.fetchall():
			f.units.append(Unit(u[0],self.getProto(u[1]),u[2]))
		
		return fl
	
	def getProto(self, id):
		if id in self.proto.keys():
			return self.proto[id]
		
		self.cur.execute("select carapace,color,weight from proto where id=:id",(id,))
		r = self.cur.fetchone()
		if r:			
			self.proto[id] = Proto(id, r[0], r[1], r[2])
		else:
			self.proto[id] = None
		return self.proto[id]

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

def users():
	global db
	c = db.conn.cursor()
	c.execute('select id,name,hw_x,hw_y,race_id from user')
	for r in c:
		yield r

def planets():
	global db
	c = db.conn.cursor()
	k = ('x','y','owner_id','o','e','m','t','s')
	c.execute('select %s from planet'%(','.join(k),))
	for r in c:
		yield dict(zip(k,r))
