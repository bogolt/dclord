import sqlite3
from objects import Planet, Fleet

class Db:
	def __init__(self, dbpath=":memory:"):
		self.conn = sqlite3.connect(dbpath)
		self.cur = self.conn.cursor()
		
		cur = self.cur
		cur.execute("""create table if not exists planet(
				x integer not null,
				y integer not null,
				owner_id integer,
				name text,
				geo integer(5)
				)""")

		cur.execute("""create table if not exists player(
				id integer primary key,
				name text not null
				)""")
		
		#what if approaching unnknown fleet does not have an id?
		#id integer primary key,
		cur.execute("""create table if not exists fleet(
				id,
				x integer not null,
				y integer not null,
				owner_id integer,
				name text,
				from_x integer,
				from_y integer,
				turns_left integer
				total_mass integer
				units_count integer
				)""")

	def addPlayer(self, id, name):
		self.cur.execute('insert into player(id,name) values(?,?)', (id, name))
		self.conn.commit()
		
	def addPlanet(self, planet):
		self.cur.execute('insert into planet(x,y,name,owner_id) values(?,?,?,?)', (planet.coord[0], planet.coord[1], planet.name, planet.owner))
		self.conn.commit()

	def addFleet(self, fleet):
		self.cur.execute('insert into fleet(id,x,y,owner_id, name, from_x, from_y, turns_left) values(?,?,?,?,?,?,?,?)', (fleet.id, fleet.coord[0], fleet.coord[1], fleet.owner, fleet.name, fleet.posFrom[0], fleet.posFrom[1], fleet.turnsLeft))
		self.conn.commit()
		
	def getFleets(self, leftTop=(0,0), size=(1000,1000)):
		cx,cy=leftTop
		zx=cx+size[0]
		zy=cy+size[1]
		cur = self.cur
		cur.execute("select x,y,owner_id,name,from_x,from_y,turns_left from fleet where x>=:cx and y>=:cy and x<=:zx and y<=:zy", (cx,cy,zx,zy))
		pl = {}
		for c in cur.fetchall():
			coord = (c[0], c[1])
			p = Fleet(coord, c[2], c[3], (c[4], c[5]), c[6])
			if coord in pl:
				pl[coord].append(p)
			else:
				pl[coord] = [p]
				
		return pl

	def getFullFleets(self):
		fs = self.getFleets()
		players = self.getPlayers()
		
		for fleets in fs.values():
			for f in fleets:
				if f.owner:
					f.ownerName = players[f.owner]
			
		return fs
	
	def getPlanets(self, leftTop=(0,0), size=(1000,1000)):
		cx,cy=leftTop
		zx=cx+size[0]
		zy=cy+size[1]
		cur = self.cur
		cur.execute("select x,y,owner_id,name from planet where x>=:cx and y>=:cy and x<=:zx and y<=:zy", (cx,cy,zx,zy))
		pl = {}
		for c in cur.fetchall():
			coord = (c[0], c[1])
			p = Planet(coord, c[2], c[3])
			pl[coord] = p
		
		return pl
	
	def getFullPlanets(self):
		planets = self.getPlanets()
		players = self.getPlayers()
		
		for p in planets.values():
			if p.owner:
				p.ownerName = players[p.owner]
			
		return planets
	
	def getPlayers(self):
		cur = self.cur
		cur.execute("select id,name from player")
		p = {}
		for c in cur.fetchall():
			p[c[0]] = c[1]
		return p
