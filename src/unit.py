import logging
from loader import get_attr, get_attrs
from xml.dom import minidom

log = logging.getLogger('dclord')

class Unit:
	def __init__(self, node = None, id = None, bc = None, hp = None):
		#current HP value
		self.hp = hp
		#building class
		self.bc = bc
		#server unit id
		self.id = id
		
		self.proto = None
		#unit level ( obsolete )
		#self.level = None
		
		self.fleet_id = None
		
		if node:
			self.load_from_xml(node)
		
	def load_from_xml(self, node):
		self.hp = get_attr(node, 'hp')
		self.bc = get_attr(node, 'bc')
		self.id = get_attr(node, 'id')
		#self.level = get_attr(node, 'lvl')
	
	def save(self, node):
		set_attr(node, 'hp', self.hp)
		set_attr(node, 'bc', self.bc)
		set_attr(node, 'id', self.id)
		
	def load(self, node):
		return self.load_from_xml(node)
		
	def diff(self, prev):
		hp,bc = None,None
		if self.hp != prev.hp:
			hp = self.hp
		if self.bc != prev.bc:
			bc = self.bc
		if hp or bc:
			return Unit(None, self.id, bc, hp)
		return None
		
class AlienUnit:
	def __init__(self, node = None, id = None, bc = None, carapase = None, weight = None):
		self.id = id
		self.bc = bc
		self.carapace = carapase
		self.weight = weight
		self.color = None
		
		if node:
			self.load_from_xml(node)
				
	def load_from_xml(self, node):
		self.carapace = get_attr(node, 'carapace')
		self.bc = get_attr(node, 'class-id')
		self.id = get_attr(node, 'id')
		self.weight = get_attr(node, 'weight')
		self.color = get_attr(node, 'color')

	def load(self, node):
		return self.load_from_xml(node)
		
	def save(self, node):
		set_attr(node, 'carapase', self.carapase)
		set_attr(node, 'class-id', self.bc)
		set_attr(node, 'id', self.id)
		set_attr(node, 'weight', self.weight)

class Production:
	def __init__(self, node = None):
		self.done = None
		self.order = None
		
		self.unit = None
		
		if node:
			self.load_from_xml(node)
		
	def load_from_xml(self, node):
		self.done = get_attr(node, 'done')
		self.order = get_attr(node, 'inproc-order')
		self.unit = Unit(node)
