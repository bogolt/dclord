import logging
from loader import get_attr, get_attrs
import planet
import proto
import fleet
import unit
import player
import race
from xml.dom import minidom

log = logging.getLogger('dclord')

class Account:
	def __init__(self, file):
		self.name = None
		self.login = None
		self.id = None
		self.race_id = None
		self.race = None
		self.hw_pos = None
		
		self.owned_fleets = {}
		self.owned_flying_fleets={}
		self.alien_fleets = {}
		self.alien_flying_fleets = {}
		self.prototypes = {}
		self.owned_planets = {}
		self.known_planets = {}
		self.race = None
		self.known_players = {}
		
		if file:
			self.load_from_file(file)
	
	def load_from_file(self, file):
		xmldoc = minidom.parse(file)
		node = xmldoc.firstChild
		self.id = get_attr(node, 'id')
		
		if self.load_errors(node.getElementsByTagName("errors")):
			return
		
		main = node.getElementsByTagName("iframe")[0]
		
		gen_info = main.getElementsByTagName('general-info')
		if gen_info:
			#print 'loading user info from %s'%(file,)
			self.load_user_info(gen_info[0])
			#load them first, to be able to assign protopes to garrison and fleet units
			self.load_prototypes(main.getElementsByTagName('building-types')[0])
			self.load_planets(main.getElementsByTagName('user-planets')[0])
			self.load_garrisons(main.getElementsByTagName('harrisons')[0])
			self.load_fleets(main.getElementsByTagName('fleets')[0])
			self.load_alien_fleets(main.getElementsByTagName('allien-fleets')[0])
			self.load_known_players(main.getElementsByTagName('diplomacy')[0])
			return
			
		known_planets_node = main.getElementsByTagName('known-planets')
		if known_planets_node:
			#print 'loading known planets from %s'%(file,)
			for planet_node in known_planets_node[0].getElementsByTagName('planet'):
				pl = planet.KnownPlanet(planet_node)
				self.known_planets[ pl.pos ] = pl
			return
		
		log.error('nothing to load from %s'%(file,))

	def load_known_players(self, dip_nodes):
		for dip_node in dip_nodes.getElementsByTagName('rel'):
			p = player.Player(dip_node)
			self.known_players[p.id] = p
		
	def load_user_info(self, general_info):
		'load race and basic player info, and id'
		player = general_info.getElementsByTagName('this-player')[0]
		self.id = get_attr(player, 'player-id')
		self.race_id = get_attr(player, 'race-id')
		self.name = get_attr(player, 'player-name', unicode)
		self.login = get_attr(player, 'login', unicode)
		self.hw_pos = get_attrs(player, 'homeworldx','homeworldy')
		
		self.race = race.Race(general_info.getElementsByTagName('this-player-race')[0])
	
	def load_prototypes(self, prototypes_node):
		for proto_node in prototypes_node.getElementsByTagName('building_class'):
			pr = proto.Proto(proto_node)
			self.prototypes[pr.id] = pr
	
	def load_garrisons(self, node):
		for garrison_node in node.getElementsByTagName('harrison'):
			pos = get_attrs(garrison_node, 'x', 'y')
			self.owned_planets[pos].load_garrison_from_xml(garrison_node)
			for u in self.owned_planets[pos].garrison:
				u.proto = self.prototypes[u.bc]
	
	def load_alien_fleets(self, node):
		for fleet_node in node.getElementsByTagName('allien-fleet'):
			#print 'loading fleet from %s'%(fleet_node,)
			f = fleet.AlienFleet(fleet_node)
			if f.flying:
				self.alien_flying_fleets[f.id] = f
			else:
				self.alien_fleets[f.id] = f
						
	def load_fleets(self, node):
		for fleet_node in node.getElementsByTagName('fleet'):
			#print 'loading fleet from %s'%(fleet_node,)
			f = fleet.Fleet(fleet_node)
			f.set_proto(self.prototypes)
			f.owner_id = self.id
			f.owner = self
			if f.flying:
				self.owned_flying_fleets[f.id] = f
			else:
				self.owned_fleets[f.id] = f
	
	def load_planets(self, planet_list):
		'load owned planet list'
		for planet_node in planet_list.getElementsByTagName('planet'):
			pl = planet.OwnedPlanet(planet_node)
			pl.owner_id = self.id
			self.owned_planets[ pl.pos ] = pl

	def get_planet(self, pos):
		if pos in self.owned_planets:
			return self.owned_planets[pos]
		if pos in self.known_planets:
			return self.known_planets[pos]
		return None

	def get_proto(self, proto_id):
		return self.prototypes[proto_id]
		
	def load_errors(self, err):
		if not err:
			return False
		hasAny = False
		for e in err[0].getElementsByTagName("error"):
			txt = ''
			if e.firstChild:
				txt = e.firstChild.data
			id = get_attr(e, 'id')
			
			#str = 'error %s %s'%(id, txt)
			#if 'user' in e.attributes.keys():
			#	str = '%s %s'%(node.attributes['user'].value,str)
				
			log.error('Error %d: %s'%(id, txt))
			#wx.PostEvent(self.callback, Report(attr1=False, attr2=str))
			hasAny = True
		return hasAny

	def get_type_units(self, proto_id):
		units = []
		fleet_types = [self.owned_fleets, self.owned_flying_fleets]
		for src in fleet_types:
			for f in src.values():
				for un in f.units:
					if un.bc == proto_id:
						units.append(un)
		for p in self.owned_planets.values():
			for un in p.garrison:
				if un.bc == proto_id:
					units.append(un)
		return units
	
	def filter_protos(self, can_fly = True, transportable = False, min_transport_cells = 0 ):
		for pr in self.prototypes.values():
			if ((pr.fly.fly_speed > 0.0001) == can_fly) and (min_transport_cells == 0 or (pr.fly.transport_capacity >= min_transport_cells)):
				yield pr
