import logging
from loader import get_attr, get_attrs
from xml.dom import minidom

log = logging.getLogger('dclord')

class Player:
	def __init__(self, node):
		self.id = None
		self.name = None
		self.dip_status = None
		
		if node:
			self.load_from_xml(node)
		
	def load_from_xml(self, node):
		self.id = get_attr(node, 'player')
		self.name = get_attr(node, 'name', unicode)
		self.dip_status = get_attr(node, 'type')
