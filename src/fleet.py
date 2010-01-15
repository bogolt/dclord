import wx

class Fleet:
	def __init__(self, owner, name, posTo, posFrom, flying):
		self.name = name
		self.owner = owner
		self.pos = posTo
		self.posFrom = posFrom
		self.isFlying = flying
		
		print 'load fleet',name,'belogs to',owner,'flying',flying,'from',posFrom,'to',posTo
	
	def __str__(self):
		s=""
		if self.name:
			s += self.name
		if self.owner:
			s+=" ["+self.owner+"]"
		
		return s
		
		

