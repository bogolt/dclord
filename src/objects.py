class Planet:
	def __init__(self, coord, owner=None, name=None):
		self.coord = coord
		self.geo = []
		self.name = name
		self.owner = owner
		self.ownerName = ''

	def __str__(self):
		return unicode(self).encode('utf-8')
			
	def __unicode__(self):
		return u'%s->%s %s'%(self.owner,self.name,self.geo)

class Fleet:
	# owner None = unknown ( fleet has not arrived yet )	
	def __init__(self, coord, owner=None, name=None, pFrom = (0,0), turnsLeft = 0):
		#print 'fleet creat %s %s %s %s %s'%(coord, owner, name, pFrom, turnsLeft)
		self.coord=coord
		self.id = None
		self.name = name
		self.owner = owner
		self.ownerName = ''
		self.posFrom=pFrom
		self.turnsLeft = turnsLeft
		self.units=[]
			
	def __str__(self):
		return unicode(self).encode('utf-8')

	def __unicode__(self):
		s='fleet '
		if self.name:
			s+=self.name+' '
		s+='on %s '%(self.coord,)
		if self.owner:
			s+=u'by %s '%(self.owner,)
		if self.posFrom:
			s+='from %s'%(self.posFrom,)
		for u in self.units:
			s+=u'\nunit %s'%(u,)
		return s

class Player:
	def __init__(self, id, name='unknown'):
		self.id = id
		self.name=name
		self.fleets=[]
		self.planets={}
		self.bc={}
	def __str__(self):
		return unicode(self).encode('utf-8')
	def __unicode__(self):
		s=self.name
		for p in self.planets.values():
			s+='\n'+unicode(p)
		return s