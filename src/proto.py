import logging
from loader import get_attr, get_attrs
from xml.dom import minidom

log = logging.getLogger('dclord')

class UnitAction:
	Action_GeoExplore = 1
	#Action_Colonize = 
	def __init__(self, node):
		self.id = None
		self.max_count = None
		self.possible_planet = None
		self.price = None
		
		if node:
			self.load_from_xml(node)
			
	def load_from_xml(self, node):
		self.id = get_attr(node, 'action')
		self.max_count = get_attr(node, 'maxcount')
		self.price = PriceAttr(node)
		self.possible_planet = get_attr(node, 'planet-can-be', str)

# stealth-lvl="0.0000000" 
# scan-strength="0.0000000" 
# detect-range="0" 
class StealthAttr:
	def __init__(self, node):
		self.stealth_level = None
		self.scan_strength = None
		self.detect_range = None
		
		if node:
			self.load_from_xml(node)
	
	def load_from_xml(self, node):
		self.stealth_level = get_attr(node, 'stealth-lvl', float)
		self.scan_strength = get_attr(node, 'scan-strength', float)
		self.detect_range = get_attr(node, 'detect-range', float)

# fly-range="0" 
# transport-capacity="0" 
# fly-speed="0" 
# carrier-capacity="0" 
class FlyAttr:
	def __init__(self, node):
		self.transport_capacity = None
		self.fly_range=None
		self.fly_speed=None
		self.carrier_capacity = None
		
		if node:
			self.load_from_xml(node)
		
	def load_from_xml(self, node):
		self.transport_capacity = get_attr(node, 'transport-capacity')
		self.fly_range = get_attr(node, 'fly-range', float)
		self.fly_speed = get_attr(node, 'fly-speed', float)
		self.carrier_capacity = get_attr(node, 'carrier-capacity')
		
# laser-damage="0" 
# laser-ar="0.00" 
# laser-number="0" 
# bomb-damage="0" 
# bomb-ar="0.00" 
# bomb-number="0" 

class FightAttr:
	def __init__(self, node):
		self.laser_damage = None
		self.laser_aim = None
		self.laser_count = None
		self.bomb_damage = None
		self.bomb_aim = None
		self.bomb_count = None
		
		if node:
			self.load_from_xml(node)
			
	def load_from_xml(self, node):
		self.laser_damange = get_attr(node, 'laser-damage', float)
		self.laser_aim = get_attr(node, 'laser-ar', float)
		self.laser_count = get_attr(node, 'laser-number')
		
		self.bomb_damange = get_attr(node, 'bomb-damage', float)
		self.bomb_aim = get_attr(node, 'bomb-ar', float)
		self.bomb_count = get_attr(node, 'bomb-number')
		

# bonus-e="0" 
# bonus-surface="0" 
# bonus-production="0" 
# bonus-m="20" 
# bonus-o="0" 
class BonusAttr:
	def __init__(self, node):
		self.o = None
		self.e = None
		self.m = None
		self.surface = None
		self.production = None
		
		if node:
			self.load_from_xml(node)
			
	def load_from_xml(self, node):
		self.o = get_attr(node, 'bonus-o')
		self.e = get_attr(node, 'bonus-e')
		self.m = get_attr(node, 'bonus-m')
		self.surface = get_attr(node, 'bonus-surface')
		self.production = get_attr(node, 'bonus-production')

#  cost-main="102.7" 
#  cost-second="25.675" 
#   cost-money="0" 
#   cost-pepl="0" 
class PriceAttr: 
	def __init__(self, node):
		self.main = None
		self.second = None
		self.money = None
		self.people = None
		
		if node:
			self.load_from_xml(node)
			
	def load_from_xml(self, node):
		self.main = get_attr(node, 'cost-main', float)
		self.second = get_attr(node, 'cost-second', float)
		self.money = get_attr(node, 'cost-money', float)
		self.people = get_attr(node, 'cost-pepl')

# maxcount="0" 
# req-tehn-level="0" 
#   build-speed="2500" 
class BuildAttr:
	def __init__(self, node):
		self.max_count = None
		self.require_tech_level = None
		self.build_speed = None
		
		if node:
			self.load_from_xml(node)
			
	def load_from_xml(self, node):
		self.max_count = get_attr(node, 'maxcount')
		self.require_tech_level = get_attr(node, 'req-tehn-level')
		self.build_speed = get_attr(node, 'build-speed')
		

# bomb-dr="0.0000000"
# laser-dr="0.0000000" 

# support-second="0" 
# support-main="1.027" 
 
# serial="1" 
# carapace="0" 
# building-id="1" 
# class="100" 
 
# is-war="0" 
# is-transportable="0" 
# is-ground-unit="0" 
# offensive="0" 
# is-building="1" 
# is-space-ship="0" 

# hit-points="150"
# weight="0" 
# color="0" 
# requires-pepl="5000" 

class Proto:
	def __init__(self, node = None):
		self.id = None
		self.building_class = None
		self.name = None
		self.description = None
		self.carapace = None
		self.weight = None
		self.color = None
		
		self.is_war = None
		self.is_transportable = None
		self.is_ground = None
		self.is_offensive = None
		self.is_building = None
		self.is_space_ship = None
		
		self.hp = None
		self.requires_people = None
		
		self.support_main = None
		self.support_second = None
		
		self.damage_resistance_bomb = None
		self.damage_resistance_laser = None
		
		self.actions = {}
			
		if node:
			self.load_from_xml(node)
			
	def load_from_xml(self, node):
		self.id = get_attr(node, 'building-id')
		self.building_class = get_attr(node, 'class')
		self.carapace = get_attr(node, 'carapace')
		self.serial = get_attr(node, 'serial')
		self.color = get_attr(node, 'color')
		
		self.name = get_attr(node, 'name', unicode)
		self.description = get_attr(node, 'description', unicode)
		
		self.is_war = get_attr(node, 'is-war', bool)
		self.is_transportable = get_attr(node, 'is-transportable', bool)
		self.is_ground = get_attr(node, 'is-ground-unit', bool)
		self.is_offensive = get_attr(node, 'offensive', bool)
		self.is_building = get_attr(node, 'is-building', bool)
		self.is_space_ship = get_attr(node, 'is-space-ship', bool)
		
		self.hp = get_attr(node, 'hit-points')
		self.requires_people = get_attr(node, 'requires-pepl')
		
		self.support_main = get_attr(node, 'support-main', float)
		self.support_second = get_attr(node, 'support-second', float)
		
		self.damage_resistance_bomb = get_attr(node, 'bomb-dr', float)
		self.damage_resistance_laser = get_attr(node, 'laser-dr', float)
		
		self.fly = FlyAttr(node)
		self.bonus = BonusAttr(node)
		self.build = BuildAttr(node)
		self.price =  PriceAttr(node)
		self.stealth = StealthAttr(node)
		
		actions = node.getElementsByTagName('actions')
		if actions:
			for action_node in actions[0].getElementsByTagName('act'):
				action = UnitAction(action_node)
				#print 'loading actin %d of bc %d'%(action.id, self.id)
				self.actions[action.id] = action
	
	def can_explore_geo(self):
		return UnitAction.Action_GeoExplore in self.actions
