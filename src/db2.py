import os
import os.path
from account import Account

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
				login = fname[:len(ending) ]
				break
		
		if not login in self.accounts:
			self.accounts[login] = Account(None)
		self.accounts[login].load_from_file(file)

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
		
	def getObjects(self, a,b):
		return []

	def is_mult(self, player_id):
		for acc in self.accounts.values():
			if player_id == acc.id:
				return True
		return False

	def getAnything(self):
		for acc in self.accounts.values():
			if acc.hw_pos:
				return acc.hw_pos
		return (1,1)
	
