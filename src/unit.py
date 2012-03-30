import logging
import loader
from xml.dom import minidom

class Unit:
	def __init__(self, node = None, id = None, bc = None, hp = None):
		#current HP value
		self.hp = hp
		#building class
		self.bc = bc
		#server unit id
		self.id = id
		#unit level ( obsolete )
		#self.level = None
		
		if node:
			self.load_from_xml(node)
		
	def load_from_xml(self, node):
		self.hp = get_attr(node, 'hp')
		self.bc = get_attr(node, 'bc')
		self.id = get_attr(node, 'id')
		#self.level = get_attr(node, 'lvl')
		
class AlienUnit:
	def __init__(self, node = None, id = None, bc = None, carapase = None, weight = None):
		self.id = id
		self.bc = bc
		self.carapse = carapase
		self.weight = weight
		
		if node:
			self.load_from_xml(node)
				
	def load_from_xml(self, node):
		self.carapse = get_attr(node, 'carpace')
		self.bc = get_attr(node, 'class-id')
		self.id = get_attr(node, 'id')
		self.weight = get_attr(node, 'weight')

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
