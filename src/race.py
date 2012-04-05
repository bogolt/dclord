import logging
from loader import get_attr, get_attrs
from xml.dom import minidom

log = logging.getLogger('dclord')

class Race:
	def __init__(self, node):
		self.id = None
		self.t_opt = None
		self.t_delta = None
		self.nature = None
		self.main = None
		self.second = None
		self.name = None
		
		if node:
			self.load_from_xml(node)
		
	def load_from_xml(self, node):
		self.id = get_attr(node, 'race-id')
		self.t_opt = get_attr(node, 't-optimal', float)
		self.t_delta = get_attr(node, 't-delta', float)
		self.nature = get_attr(node, 'race-nature', str)
		self.main = get_attr(node, 'industry-nature', str)
		self.second = get_attr(node, 'unused-resource', str)
		self.name = get_attr(node, 'race-name', unicode)
		
