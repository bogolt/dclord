import logging
import os
import os.path
from account import Account
import planet

log = logging.getLogger('dclord')

import sqlite3


def export_planets_to_csv(pl, path):
	with open(path, 'wt') as f:
		for p in pl.values():
			pass
		
def contains(rect, pos):
	p,s = rect
	if pos[0] < p[0] or pos[1] < p[1]:
		return False
	if pos[0] > p[0] + s[0] or pos[1] > p[1] + s[1]:
		return False
	return True

import csv
import sys

class Db:
	def __init__(self):
		self.accounts = {}
		self.known_planets = {}
		self.conn = sqlite3.connect(":memory:")
		self.cur = self.conn.cursor()
		
		self.cur.execute("""create table if not exists planet(
				x integer(2) not null,
				y integer(2) not null,
				owner_id integer,
				name text,
				o integer(1),
				e integer(1),
				m integer(1),
				t integer(1),
				s integer(1)
				)""")
			
	def load_csv(self):
		data = csv.reader(open('/tmp/dclord/csv/known_planets.csv'))
		
		i = 0
		for row in data:
			#i+=1
			#if i%2 == 0:
			#	continue
			items = row[0].split(';')
			try:
				x = int(items[0])
				y = int(items[1])
				kp = planet.KnownPlanet(None)
				kp.pos = x,y
				kp.geo = {}
				s = -1
				if len(items) > 6:
					s = int(items[6])
					#kp.geo['s'] = int(items[6])
				#self.known_planets[ kp.pos ] = kp
				self.cur.execute('insert or replace into planet(x,y,s) values(:x,:y,:s)', locals())
				self.conn.commit()

			except ValueError:
					print "Could not convert data to an integer."
			except:
					print "Unexpected error:", sys.exc_info()[0]
					
		log.debug('loaded %d known planets'%(len(self.known_planets),))
	
	def knownPlanets(self, area):
		pos,size = area
		x,y = pos
		mx = size[0] + x
		my = size[1] + y
		self.cur.execute("select x,y,s from planet where x>=:x and y>=:y and x<=:mx and y<=:my",locals())
		for x,y,s in self.cur.fetchall():
			#print 'got data %d %d %d'%(x,y,s)
			k = planet.KnownPlanet(None)
			k.pos = int(x),int(y)
			k.geo = {'s':int(s)}
			yield k.pos,k
				
	def load_account(self, file):
		fname = os.path.basename(file)
		
		ext = 'xml'
		suffix_list = ['_all', '_known_planets']
		login = ''
		for suffix in suffix_list:
			ending = suffix + '.' + ext
			if fname.endswith(ending ):
				login = fname[:-len(ending) ]
				break
		
		log.debug('loading file %s as account %s'%(file, login))
		self.accounts.setdefault(login, Account(None)).load_from_file(file)

	def getPlanets(self, rect):
		pl = {}
		for acc in self.accounts.values():
			for pos,p in acc.owned_planets.items():
				if contains(rect, pos) and (not pos in pl):
					pl[pos] = p

		for acc in self.accounts.values():
			for pos,p in acc.known_planets.items():
				if contains(rect, pos) and (not pos in pl):
					pl[pos] = p
					
		return pl.values()

	def getFleets(self, rect, my=True, other=True, static = True, flying=True, include_starting_pos = True):
		fl = {}
		
		src = []
		if my:
			for acc in self.accounts.values():
				if static and my:
					src.append( acc.owned_fleets )
				if flying and my:
					src.append( acc.owned_flying_fleets )

		if other:
			for acc in self.accounts.values():
				if static and other:
					src.append( acc.alien_fleets )
				if flying and other:
					src.append( acc.alien_flying_fleets )
		
		for fleet_src in src:
			for id,fleet in fleet_src.items():
				if id and id in fl:
					continue
				if contains(rect, fleet.pos):
					fl[id] = fleet
					continue
				if fleet.flying and include_starting_pos and contains(rect, fleet.from_pos):
					fl[id] = fleet
					continue
		return fl.values()

	def getStaticFleets(self, rect):
		pl = {}
		for acc in self.accounts.values():
			for id,f in acc.owned_fleets.items():
				#if ((f.from_pos and contains(rect, f.from_pos)) or (f.contains(rect, pos) )) and (not pos in pl):
				if contains(rect, f.pos):# and (not id in pl):
					pl[id] = f

		return pl.values()

	def getFlyingFleets(self, rect):
		pl = {}
		for acc in self.accounts.values():
			for id,f in acc.owned_flying_fleets.items():
				if contains(rect, f.from_pos) or contains(rect, f.pos): # and (not pos in pl):
					pl[id] = f

		return pl.values()
		
	def get_objects(self, pos):
		return self.get_planet(pos), self.getFleets((pos,(0,0)), include_starting_pos = False)

	def get_planet(self, pos):
		for acc in self.accounts.values():
			for p in acc.owned_planets.values():
				if p.pos == pos:
					return p

		#TODO can be returned not most informative here
		for acc in self.accounts.values():
			for p in acc.known_planets.values():
				if p.pos == pos:
					return p
		return None
		
	def is_mult(self, player_id):
		for acc in self.accounts.values():
			if player_id == acc.id:
				return True
		return False

	def get_login(self, user_id):
		if user_id <=0:
			return 'unknown'
		for acc in self.accounts.values():
			if user_id == acc.id:
				return acc.login
		return ''
		
	def get_player_name(self, player_id):
		if player_id <=0:
			return 'unknown'
		for acc in self.accounts.values():
			if player_id == acc.id:
				if not acc.name:
					log.error('wrong name for %d %s'%(player_id, acc.login))
					continue
				return acc.name
			if player_id in acc.known_players:
				if acc.known_players[player_id].name:
					return acc.known_players[player_id].name
		return 'error_id %d'%(player_id,)

	def get_fleet_owner_id(self, fleet_id):
		for acc in self.accounts.values():
			if fleet_id in acc.owned_fleets or fleet_id in acc.owned_flying_fleets:
				return acc.id
		return -1
	
	def getAnything(self):
		
		self.cur.execute("select x,y from planet")
		x,y = self.cur.fetchone()
		return x,y

		for pos in self.known_planets.keys():
			return pos
			
		for acc in self.accounts.values():
			if acc.hw_pos:
				return acc.hw_pos
		return (1,1)
	
	def export_known_planets(self):
		pl = {}
		for acc in self.accounts.values():
			for p in acc.owned_planets.values():
				pl[p.pos] = p
		for acc in self.accounts.values():
			for p in acc.known_planets.values():
				if not p in pl:
					pl[p.pos] = p
		
		export_planets_to_csv(pl, '/tmp/dclord/planets.csv')
	


