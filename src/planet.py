import wx

class EmptyPlanet:
	def __init__(self, coord, name=None, geo=None):
		self.pos = coord
		self.geo = geo
		self.name = name
		
	def load_from_xml(self, node):
		self.name = get_attr(node, 'name', str)
		self.pos = get_attrs(node, 'x','y')
		self.geo = get_attrs(node, 'o','e','m','t','s')

class OwnedPlanet(EmptyPlanet):
	def __init__(self, pos, name, owner_id):
		EmptyPlanet.__init__(pos, name)
		self.owner_id = owner_id
		self.corruption = None
		self.population = None
		
		self.production = []
		self.buildings = []
		self.garrison = []

	def load_from_xml(self, node):
		self.name = get_attr(node, 'name', str)
		self.pos = get_attrs(node, 'x','y')
		self.geo = get_attrs(node, 'o','e','m','temperature','surface')
		self.corruption = get_attr(node, 'corruption')
		self.population = get_attr(node, 'population')

	def load_garrison_from_xml(self, node):
		pos = get_attrs(node, 'x','y')
		if pos != self.pos:
			log.error('wrong garrison %s for planet %s'%(pos, self.pos))
			return False
		
		for node_unit in node.getElementsByTagName('c-u'):
			self.production.append( Unit(node_unit) )

		for node_unit in node.getElementsByTagName('u'):
			self.garrison.append( Unit(node_unit) )
		

class Planet:
	def __init__(self, coord, owner=None, name=None, geo=[]):
		self.coord = coord
		self.geo = geo
		self.name = name
		self.owner = owner
	
	def __str__(self):
		s=""
		if self.name:
			s += self.name
		if self.owner:
			s+=" ["+self.owner+"]"
		
		return s
		
		

