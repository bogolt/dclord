from xml.dom import minidom
from objects import Planet,Fleet,Player
from db import Db

class XmlParser:
	def __init__(self, file):
		self.player=None
		self.db=Db()		
		self.fromXml(file)

	def parseFormdata(self, formdata):
		pass
	def parseGeneral(self, n):
		pass

	def parseOwnerPlanet(self, planet):
		coord = int(planet.attributes["x"].value), int(planet.attributes["y"].value)
		p = Planet(coord, self.player.name, planet.attributes['name'].value)
		geo = []
		for opt in ['o','e','m','temperature','surface']:
			geo.append(int(planet.attributes[opt].value))
		p.geo=tuple(geo)
		return p

	def parseUserPlanets(self, planets):
		for p in planets.getElementsByTagName("planet"):
			pl = self.parseOwnerPlanet(p)
			self.player.planets[pl.coord]=pl

	def parseBuildingTypes(self, build):
		for b in build.getElementsByTagName("building_class"):
			buildId = int(b.attributes['building-id'].value)
			self.player.bc[buildId]=int(b.attributes['class'].value)

	def parseUserFleetUnit(self, u):
		#<u hp="15" lvl="0" bc="36591" id="134881" /> 
		bc = int(u.attributes["bc"].value)
		hp = int(u.attributes["hp"].value)
		return bc, hp, self.player.bc[bc]
	def parseAlienFleetUnit(self, u):
		#<allien-ship id="102397" class-id="32215" carapace="20" weight="433" is-observed="" color="0" /> 
		bc = int(u.attributes["class-id"].value)
		weight = int(u.attributes["weight"].value)
		return bc, weight
	def parseUserFleet(self, fleet):
		x=int(fleet.attributes["x"].value)
		y=int(fleet.attributes["y"].value)
		f = Fleet((x,y), self.player)
		if 'from-x' in fleet.attributes.keys():
			fromx=int(fleet.attributes["from-x"].value)
			fromy=int(fleet.attributes["from-y"].value)
			f.posFrom=fromx,fromy
		f.name=fleet.attributes["name"].value
			
		for u in fleet.getElementsByTagName("u"):
			f.units.append(self.parseUserFleetUnit(u))
		#print f
		return f
	
	def parseAlienFleet(self, fleet):
		x=int(fleet.attributes["x"].value)
		y=int(fleet.attributes["y"].value)
		
		playerId = -1 #unknown player ( fleet is not arrived yet )
		if 'player-id' in fleet.attributes.keys():
			playerId = int(fleet.attributes['player-id'].value)
		f = Fleet((x,y), self.db.getPlayer(playerId))
		if 'from-x' in fleet.attributes.keys():
			fromx=int(fleet.attributes["from-x"].value)
			fromy=int(fleet.attributes["from-y"].value)
			f.posFrom=fromx,fromy
		if 'name' in fleet.attributes.keys():
			f.name=fleet.attributes["name"].value
			
		for u in fleet.getElementsByTagName("allien-ship"):
			f.units.append(self.parseAlienFleetUnit(u))
		print f
		
		return f	
	def parseUserFleets(self, fl):
		for p in fl.getElementsByTagName("fleet"):
			self.player.fleets.append(self.parseUserFleet(p))	
	
	def parseAlienFleets(self, fl):
		for p in fl.getElementsByTagName("allien-fleet"):
			self.parseAlienFleet(p)
	def parsePlayer(self, p):
		self.db.addPlayer(int(p.attributes['player'].value),p.attributes['name'].value)
	def parsePlayers(self, d):
		for p in d.getElementsByTagName("rel"):
			self.parsePlayer(p)
	def parseIframe(self, iframe):

		self.parseUserPlanets(iframe.getElementsByTagName('user-planets')[0])
		self.parsePlayers(iframe.getElementsByTagName('diplomacy')[0])
		self.parseBuildingTypes(iframe.getElementsByTagName('building-types')[0])
		self.parseUserFleets(iframe.getElementsByTagName('fleets')[0])
		self.parseAlienFleets(iframe.getElementsByTagName('allien-fleets')[0])
#	for node in iframe:
#		if node.nodeName=='general-info':
#			parseGeneral(node)
#		elif node.nodeName=='user-planets':
#			parseUserPlanets(node)
#		elif node.nodeName=='fleets':
#			parseFleets(node)
#		elif node.nodeName=='allien-fleets':
#			parseAllienFleets(node)
##		elif node.nodeName=='building-types':
#			parseBuildingTypes(node)
#		elif 'shared-building-types'
#		harrisons
#		fleets
#		shared-fleets
#		allien-fleets
#		diplomacy
#		cargo-moves
#		actions-requested

	def parseDc(self, nodeDc):
		self.player = Player(int(nodeDc.attributes['id'].value), nodeDc.attributes['user'].value)
		self.parseIframe(nodeDc.getElementsByTagName('iframe')[0])
		print self.player
	#	for node in nodeDc:
	#		if node.nodeName == 'formdata':
	#			parseFormdata(node)
	#		elif node.nodeName == 'iframe':
	#			parseIframe(node)

	def fromXml(self, file):
		xmldoc = minidom.parse(file)
		if xmldoc.firstChild.nodeName=='dc':
			self.parseDc(xmldoc.firstChild)
		
	
if __name__ == '__main__':
	x = XmlParser('all.xml')
