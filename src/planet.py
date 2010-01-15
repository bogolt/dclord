import wx

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
		
		

