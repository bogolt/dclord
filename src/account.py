import logging
import loader
from xml.dom import minidom

log = logging.getLogger('dclord')

class Race:
	def __init__(self, node):
		pass

def get_node(parent, name):
	node_list = parent.getElementsByTagName(name)
	if not node_list:
		

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

	def load_user_info(self, general_info):
		'load race and basic player info, and id'
		player = general_info.getElementsByTagName('this-player')[0]
		self.id = get_attr(player, 'player-id')
		self.race_id = get_attr(player, 'race-id')
		self.name = get_attr(player, 'name')
		self.login = get_attr(player, 'login')
		self.hw_pos = get_attrs(player, 'homeworldx','homeworldy')

	def load_prototypes(self, prototypes):
		for proto_node in self.prototypes:
			self.proto
	def load_planets(self, planet_list):
		'load owned planet list'
		for planet_node in planet_list:
			self.owned_planets.append( planet.OwnedPlanet(planet_node) )
		
	def load_errors(self, err)
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
		
		if main:
			self.parseKnownPlanets(main[0])
			self.parseAll(main[0])
			
		self.stealth_level = get_attr(node, 'stealth-lvl', float)
		self.scan_strength = get_attr(node, 'scan-strength', float)
		self.detect_range = get_attr(node, 'detect-range')

