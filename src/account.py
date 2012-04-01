import logging
import loader
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
		
		self.fleets = {}
		self.prototypes = {}
		self.owned_planets = {}
		self.known_planets = {}
		self.race = None
		
		self.stealth_level = None
		self.scan_strength = None
		self.detect_range = None
		
		if file:
			self.load_from_file(file)
	
	def load_from_file(self, file):
		xmldoc = minidom.parse(file)
		node = xmldoc.firstChild
		
		if load_errors(node.getElementsByTagName("errors")):
			return
		
		main = node.getElementsByTagName("iframe")[0]
		self.load_user_info(main.getElementsByTagName('general-info')[0])
		self.load_planets(main.getElementsByTagName('user-planets')[0])
		self.load_prototypes(main.getElementsByTagName('building-types')[0])
		self.load_fleets(main.getElementsByTagName('user-planets')[0])
		
	def load_xml_known_planets(self, file):
		xmldoc = minidom.parse(file)
		node = xmldoc.firstChild
		
		if load_errors(node.getElementsByTagName("errors")):			
			return
		
		planet_list = node.getElementsByTagName("iframe")[0].getElementsByTagName('known-planets')[0]
		for planet_node in planet_list.getElementsByTagName('planet'):
			planet = KnownPlanet(planet_node)
			self.known_planets[ planet.pos ] = planet

	def load_user_info(self, general_info):
		'load race and basic player info, and id'
		player = general_info.getElementsByTagName('this-player')[0]
		self.id = get_attr(player, 'player-id')
		self.race_id = get_attr(player, 'race-id')
		self.name = get_attr(player, 'name')
		self.login = get_attr(player, 'login')
		self.hw_pos = get_attrs(player, 'homeworldx','homeworldy')

		self.stealth_level = get_attr(node, 'stealth-lvl', float)
		self.scan_strength = get_attr(node, 'scan-strength', float)
		self.detect_range = get_attr(node, 'detect-range')
		
	def load_prototypes(self, prototypes_node):
		for proto_node in prototypes.getElementsByTagName('building_class'):
			proto = proto.Proto(proto_node)
			self.prototypes[proto.id] = proto
	
	def load_planets(self, planet_list):
		'load owned planet list'
		for planet_node in planet_list:
			self.owned_planets.append( planet.OwnedPlanet(planet_node) )
		
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
