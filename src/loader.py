import wx
import gzip
import httplib
#from tempfile import mkdtemp

from xml.dom import minidom
from objects import Fleet, Planet
import os.path
from request import Request

ALL="all"
ALL_XML=ALL+".xml"
ALL_AR=ALL_XML+".gz"

KNOWN="known_planets"

req = ['all', 'known_planets']

def readPlanet(planet):
	x,y = int(planet.attributes["x"].value), int(planet.attributes["y"].value)
	
	name = ""
	try:
		name = planet.attributes["name"].value
	except KeyError:
		pass
		#name = "N["+str(x)+":"+str(y)+"]"
		
	p = Planet((x,y))
	p.name = name
	if "owner-id" in planet.attributes.keys():
		p.owner = int(planet.attributes["owner-id"].value)
	
	geo = ['o','e','m','t','temperature','s','surface']
	for g in geo:
		if g in planet.attributes.keys():
			p.geo.append(int(planet.attributes[g].value))
		
	return p

def assurePathExist(path):
	if not os.path.exists(path):
		os.mkdir(path)
			
class Loader:
	def __init__(self, db):
		self.config = wx.Config("dclient.conf")
		self.db = db
		
		#self.temp = mkdtemp('dc_lord')
		self.temp = '/tmp/dc_lord'
		assurePathExist(self.temp)
				
		self.pathArch = os.path.join(self.temp, 'arch')
		assurePathExist(self.pathArch)
		
		self.xml = os.path.join(self.temp,'xml')
		assurePathExist(self.xml)
		
	def load(self):
		for file in os.listdir(self.pathArch):
			req = file[:-3]
			self.unpack(os.path.join(self.pathArch, file), os.path.join(self.xml, req))
			if req == ALL:
				self.parseAll()
			elif req == KNOWN:
				self.parseKnown()

	def sync(self):
		user = self.config.Read("/user/login").encode('utf-8')
		password = self.config.Read("/user/password").encode('utf-8')
		
		#self.sent((user, password), 'test.xml')
		# get all request
		self.recv(user, password, ALL, ALL)
		self.recv(user, password, KNOWN, KNOWN)
		return self.load()
	
	def parseKnown(self):
		xml = os.path.join(self.xml, KNOWN)
		xmldoc = minidom.parse(xml)
		nodeIframe = xmldoc.firstChild.getElementsByTagName("iframe")
		planets = nodeIframe[0].firstChild
		for planet in planets.getElementsByTagName("planet"):
			self.db.addPlanet(readPlanet(planet))

	def parseAll(self):
		xml = os.path.join(self.xml, ALL)
		xmldoc = minidom.parse(xml)
		node = xmldoc.firstChild
		#print "turn:",node.attributes["turn"].value
		
		userId = int(node.attributes["id"].value)
		userName = node.attributes["user"].value
		self.db.addPlayer(userId, userName)
		
		main = node.getElementsByTagName("iframe")
		userPlanets = main[0].getElementsByTagName("user-planets")
		planets = userPlanets[0].getElementsByTagName("planet")
		
		#load user planets
		for planet in planets:
			p = readPlanet(planet)
			p.owner = userId
			self.db.addPlanet(p)
		
		userFleets = main[0].getElementsByTagName("fleets")
		fleets = userFleets[0].getElementsByTagName("fleet")
		
		for fleet in fleets:
			x,y = int(fleet.attributes["x"].value), int(fleet.attributes["y"].value)
			fx,fy = int(fleet.attributes["from-x"].value), int(fleet.attributes["from-y"].value)
			flying = (fleet.attributes["in-transit"].value)=="1"
			tta = 0
			if flying:
				tta = int(fleet.attributes["tta"].value)
			
			f=Fleet( (x,y), userId, fleet.attributes["name"].value, (fx,fy), tta)
			f.id = int(fleet.attributes["id"].value)
			
			self.db.addFleet(f)
			
			
		allienFleets = main[0].getElementsByTagName("allien-fleets")
		for fleet in allienFleets[0].getElementsByTagName("allien-fleet"):
			x,y = int(fleet.attributes["x"].value), int(fleet.attributes["y"].value)
			fx,fy=0,0
			if 'from-x' in fleet.attributes.keys():
				fx,fy = int(fleet.attributes["from-x"].value), int(fleet.attributes["from-y"].value)
			#flying = (fleet.attributes["in-transit"].value)=="1"
			#tta = 0
			#if flying:
			#	tta = int(fleet.attributes["tta"].value)
			
			f=Fleet( (x,y), int(fleet.attributes["player-id"].value), fleet.attributes["name"].value, (fx,fy), tta)
			f.id = int(fleet.attributes["fleet-id"].value)
			
			self.db.addFleet(f)
						
			
		players = main[0].getElementsByTagName('diplomacy')
		for p in players[0].getElementsByTagName('rel'):
			self.db.addPlayer(p.attributes['player'].value, p.attributes['name'].value)
			#p.attributes['type'].value
			
		return True

	def unpack(self, fileIn, fileOut):
		f =  gzip.open(fileIn,'rb')
		with open(fileOut, 'wb') as out:
			out.write(f.read())
		
		f.close()
	
	def sent(self, login, out):
		conn = httplib.HTTPConnection('www.the-game.ru')
		conn.set_debuglevel(1)
		r = Request()
		r.fleetMove(83953, (657,312))
		r.planetSetName((665,327), 'nn2')
		b=str(r)
		conn.request('POST', "/frames/perform_x_actions/on/1/asxml/","pwd=%s&login=%s&action=login&xactions=%s"%(login[1],login[0],b))
		r = conn.getresponse()
		if r.status != 200:
			print "Error:",r.status, r.reason
			return

		with open(os.path.join(self.pathArch, out+'.gz'),'w') as f:
			f.write(r.read())

		#don't forget to close http connection	
		conn.close()
		return True		
		
	def recv(self, user, password, outfile, req = 'all'):
		conn = httplib.HTTPConnection('www.the-game.ru')
		conn.set_debuglevel(1)
		conn.request('POST', '/frames/empire_info/on/'+req+'/asxml/', 'pwd='+password+'&login='+user+'&action=login')
		r = conn.getresponse()
		if r.status != 200:
			print "Error:",r.status, r.reason
			return

		with open(os.path.join(self.pathArch, outfile+'.gz'),'w') as f:
			f.write(r.read())

		#don't forget to close http connection	
		conn.close()
		return True

import csv

def planetsFromCSV(file):
	data = csv.reader(open(file,"rb"))
	for row in data:
		print row

