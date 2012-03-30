import logging
import loader
from xml.dom import minidom

class FleetBase:
	def __init__(self, id = None, name = None, owner_id = None, pos = None):
		self.id = id
		self.name = name
		self.pos = pos
		self.incoming_opts = None
		self.units = []
		
		self.fly_opts = None
		self.fly_from = None

	def load_from_xml(self, node):
		self.name = get_attr(node, 'name', str)
		self.pos = get_attrs(node, 'x','y')
		self.fly_opts = get_attrs(node, 'in-transit', 'tta')
		if self.fly_opts[1]:
			self.fly_from = get_attrs(node,'from-x', 'from-y')

class Fleet(FleetBase):
	def __init__(self, id = None, name = None, owner_id = None, pos = None):
		FleetBase.__init__(id, name, owner_id, pos)
		
		self.fly_opts = None
		self.hide_opts = None
		
	def load_from_xml(self, node):
		self.id = get_attr(node, 'id')
		FleetBase.load_from_xml(node)
		for unit_node in node.getElementsByTagName('u'):
			self.units.append( Unit(unit_node) )
		
class AlienFleet(FleetBase):
	def __init__(self, id = None, pos = None, name = None, weight = None, owner_id = None):
		FleetBase.__init__(id, name, owner_id, pos)
		self.weight = weight
				
	def load_from_xml(self, node):
		FleetBase.load_from_xml(node)
		self.id = get_attr(node, 'fleet-id')
		self.weight = get_attr(node, 'sum-weight')
		self.owner_id = get_attr(node, 'player-id')

		for unit_node in node.getElementsByTagName('allien-ship'):
			self.units.append( AlienUnit(unit_node) )
