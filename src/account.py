import logging
from loader import get_attr, get_attrs
import planet
import proto
import fleet
import unit
from xml.dom import minidom

log = logging.getLogger('dclord')

class Race:
	def __init__(self, node):
		pass

class Account:
	def __init__(self, file):
		self.name = None
		self.login = None
		self.id = None
		self.race_id = None
		self.hw_pos = None
		
		self.owned_fleets = {}
		self.owned_flying_fleets={}
		self.alien_fleets = {}
		self.prototypes = {}
		self.owned_planets = {}
		self.known_planets = {}
		self.race = None
		
		if file:
			self.load_from_file(file)
	
	def load_from_file(self, file):
		xmldoc = minidom.parse(file)
		node = xmldoc.firstChild
		
		if self.load_errors(node.getElementsByTagName("errors")):
			return
		
		main = node.getElementsByTagName("iframe")[0]
		self.load_user_info(main.getElementsByTagName('general-info')[0])
		self.load_planets(main.getElementsByTagName('user-planets')[0])
		self.load_garrisons(main.getElementsByTagName('harrisons')[0])
		self.load_prototypes(main.getElementsByTagName('building-types')[0])
		self.load_fleets(main.getElementsByTagName('fleets')[0])
		
	def load_xml_known_planets(self, file):
		xmldoc = minidom.parse(file)
		node = xmldoc.firstChild
		
		if self.load_errors(node.getElementsByTagName("errors")):			
			return
		
		planet_list = node.getElementsByTagName("iframe")[0].getElementsByTagName('known-planets')[0]
		for planet_node in planet_list.getElementsByTagName('planet'):
			pl = planet.KnownPlanet(planet_node)
			self.known_planets[ pl.pos ] = pl

	def load_user_info(self, general_info):
		'load race and basic player info, and id'
		player = general_info.getElementsByTagName('this-player')[0]
		self.id = get_attr(player, 'player-id')
		self.race_id = get_attr(player, 'race-id')
		self.name = get_attr(player, 'name', unicode)
		self.login = get_attr(player, 'login', unicode)
		self.hw_pos = get_attrs(player, 'homeworldx','homeworldy')
		
	def load_prototypes(self, prototypes_node):
		for proto_node in prototypes_node.getElementsByTagName('building_class'):
			pr = proto.Proto(proto_node)
			self.prototypes[pr.id] = pr
	
	def load_garrisons(self, node):
		for garrison_node in node.getElementsByTagName('harrison'):
			pos = get_attrs(garrison_node, 'x', 'y')
			self.owned_planets[pos].load_garrison_from_xml(garrison_node)
		
	def load_fleets(self, node):
		for fleet_node in node.getElementsByTagName('fleet'):
			#print 'loading fleet from %s'%(fleet_node,)
			f = fleet.Fleet(fleet_node)
			if f.flying:
				self.owned_flying_fleets[f.id] = f
			else:
				self.owned_fleets[f.id] = f
	
	def load_planets(self, planet_list):
		'load owned planet list'
		for planet_node in planet_list.getElementsByTagName('planet'):
			pl = planet.OwnedPlanet(planet_node)
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
		
