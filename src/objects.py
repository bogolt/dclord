class Proto:
	def __init__(self, id, carapace, color=0, weight=None, name = None):
		self.id = id
		self.name = name
		self.carapace = carapace
		self.weight = weight
		self.color = color

class Unit:
	def __init__(self, id, proto, hp=None):
		self.id = id
		self.proto = proto
		self.hp = hp
		self.quantity = 1		

class BuildingUnit(Unit):
	def __init__(self, id, proto, done=None):
		Unit.__init__(self, id, proto)
		self.done = done


class Fleet:
	# owner None = unknown ( fleet has not arrived yet )	
	def __init__(self, coord, id, owner=None, name=None, pFrom = (0,0), turnsLeft = 0):
		self.coord=coord
		self.id = id
		self.name = name
		self.owner = owner
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
			
class Planet:
	def __init__(self, coord, owner=None, name=None):
		self.coord = coord
		self.geo = {}
		self.name = name
		self.owner = owner
		self.units = {}#id->unit
		
	def garrison(self):
		uc = {}
		for u in self.units.values():
			if u.proto.id in uc:
				uc[u.proto.id].quantity+=1
			else:
				uc[u.proto.id] = u
				
		for u in uc.values():
			yield u

	def __str__(self):
		return unicode(self).encode('utf-8')
			
	def __unicode__(self):
		return u'%s->%s %s'%(self.owner,self.name,self.geo)

class Player:
	def __init__(self, id, name=None, login = None):
		self.id = id
		self.name = name
		self.login = login
		self.fleets=[]
		self.planets={}
		self.bc={}
		self.hw = (0,0)
		
	def __str__(self):
		return unicode(self).encode('utf-8')
	def __unicode__(self):
		return self.name
