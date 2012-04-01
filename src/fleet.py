import logging
import unit
from loader import get_attr, get_attrs
from xml.dom import minidom

log = logging.getLogger('dclord')

class FleetBase:
	def __init__(self, id = None, name = None, owner_id = None, pos = None):
		self.id = id
		self.name = name
		self.pos = pos
		self.incoming_opts = None
		self.units = []
		
		self.flying = None
		self.tta = None
		self.from_pos = None

	def load_from_xml(self, node):
		self.name = get_attr(node, 'name', unicode)
		self.pos = get_attrs(node, 'x','y')
		self.tta = get_attr(node, 'tta')
		# don't really need this
		#self.flying = get_attr(node, 'in-transit', bool)
		if self.tta > 0:
			self.flying = True
		
		if self.flying:
			self.from_pos = get_attrs(node,'from-x', 'from-y')

class Fleet(FleetBase):
	def __init__(self, node):
		FleetBase.__init__(self)
		
		self.fly_opts = None
		self.hide_opts = None
		
		if node:
			self.load_from_xml(node)
		
	def load_from_xml(self, node):
		FleetBase.load_from_xml(self, node)
		self.id = get_attr(node, 'id')
		for unit_node in node.getElementsByTagName('u'):
			self.units.append( unit.Unit(unit_node) )
		
class AlienFleet(FleetBase):
	def __init__(self, node):
		FleetBase.__init__(self)
		self.weight = weight
		if node:
			self.load_from_xml(node)
				
	def load_from_xml(self, node):
		FleetBase.load_from_xml(self, node)
		self.id = get_attr(node, 'fleet-id')
		self.weight = get_attr(node, 'sum-weight')
		self.owner_id = get_attr(node, 'player-id')

		for unit_node in node.getElementsByTagName('allien-ship'):
			self.units.append( unit.AlienUnit(unit_node) )
