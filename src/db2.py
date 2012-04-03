import logging
import os
import os.path
from account import Account

log = logging.getLogger('dclord')

def contains(rect, pos):
	p,s = rect
	if pos[0] < p[0] or pos[1] < p[1]:
		return False
	if pos[0] > p[0] + s[0] or pos[1] > p[1] + s[1]:
		return False
	return True

class Db:
	def __init__(self):
		self.accounts = {}
	
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
		

	def getAnything(self):
		for acc in self.accounts.values():
			if acc.hw_pos:
				return acc.hw_pos
		return (1,1)
	
