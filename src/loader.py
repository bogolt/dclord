import wx
import gzip
import httplib
from threading import Thread
from dcevent import Report, LoaderEvent
import urllib

from xml.dom import minidom

import os.path
import logging

def get_attr(node, name, value_type=int):
	if node.hasAttribute(name):
		return value_type(node.getAttribute(name))
	#print 'Attribute %s not exist in node %s'%(name, node)
	return None

def get_attrs(node, *args):
	l = []
	for arg in args:
		l.append( get_attr(node, arg) )			
	return tuple(l)

log = logging.getLogger('dclord')

#from request import Request
ALL="all"
ALL_XML=ALL+".xml"
ALL_AR=ALL_XML+".gz"

KNOWN="known_planets"

req = ['all', 'known_planets']

def convertDict(src, conv):
	d={}
	for attr in src.keys():
		if attr in conv:
			d[conv[attr]]=src[attr].value
	return d

class Loader:
	def __init__(self, conf, db, callback):
		self.db = db
		self.callback = callback
		self.conf = conf
		
		if 1==self.conf.s['map']['add_debug_planets']:
			self.addDebugPlanets()
			
		#self.loadGalaxySizes()
			
	def addDebugPlanets(self):
		import random
		for x in range(30):
			for y in range(10):
				self.db.addObject('planet', {'x':600+x,'y':300+y,'s':random.randint(1,99)})
				
	def loadFile(self, file):
		bname = os.path.basename(file)
		
		xml = bname[:-3]
		
		xPath = os.path.join(self.conf.pathXml, xml)
		#xml = os.path.join(self.conf.pathArchive, file[:-3])
		#xml = os.path.join(self.xml, req)
		self.unpack(file, xPath)
		self.parse(xPath)
		
	def load(self):
		for file in os.listdir(self.conf.pathXml):
			self.parse(os.path.join(self.conf.pathXml, file))

	def parseKnownPlanets(self, node):
		kp = node.getElementsByTagName('known-planets')
		if not kp:
			return None
		for planet in kp[0].getElementsByTagName('planet'):
			p=convertDict(planet.attributes, {'x':'x', 'y':'y', 'name':'name', 'owner-id':'owner_id','o':'o','e':'e','m':'m','t':'t','temperature':'t','s':'s','surface':'s'})
			self.db.addObject('planet', p)
		
	def parse(self, file):
		xmldoc = minidom.parse(file)
		node = xmldoc.firstChild
				
		main = node.getElementsByTagName("iframe")
		err = node.getElementsByTagName("errors")
		if err:
			hasAny = False
			for e in err[0].getElementsByTagName("error"):
				txt = ''
				if e.firstChild:
					txt = e.firstChild.data
				id = e.attributes['id'].value
				
				str = 'error %s %s'%(id, txt)
				if 'user' in e.attributes.keys():
					str = '%s %s'%(node.attributes['user'].value,str)
					
				wx.PostEvent(self.callback, Report(attr1=False, attr2=str))
				hasAny = True
			if hasAny:
				return False
		
		if main:
			self.parseKnownPlanets(main[0])
			self.parseAll(main[0])
	
	def parseAll(self, node):
		generalInfo = node.getElementsByTagName("general-info")
		if not generalInfo:
			return None
		thisPlayer = generalInfo[0].getElementsByTagName("this-player")[0]

		player = convertDict(thisPlayer.attributes,{'login':'login','player-id':'id', 'player-name':'name',
																								 'homeworldx':'hw_x', 'homeworldy':'hw_y'}) 
		self.db.addObject('player', player)
		
		userPlanets = node.getElementsByTagName("user-planets")
		planets = userPlanets[0].getElementsByTagName("planet")
		
		#load user planets
		for planet in planets:
			p=convertDict(planet.attributes, {'x':'x', 'y':'y', 'name':'name', 'owner-id':'owner_id','o':'o','e':'e','m':'m','t':'t','temperature':'t','s':'s','surface':'s'})
			p['owner_id'] = player['id']
			self.db.addObject('planet', p)
			
			x,y=planet.attributes['x'].value,planet.attributes['y'].value
			up = convertDict(planet.attributes, {'x':'x', 'y':'y', 'corruption':'corruption', 'population':'population'}) 
			self.db.addObject('user_planet', up) 
			
		buildingTypes = node.getElementsByTagName("building-types")[0]
		for bt in buildingTypes.getElementsByTagName("building_class"):
			b = convertDict(bt.attributes, {'color':'color', 'building-id':'id', 'weight':'weight','carapace':'carapace'})
			self.db.addObject('proto', b)
		
		garrisons = node.getElementsByTagName('harrisons')[0]
		for garrison in garrisons.getElementsByTagName('harrison'):
			x,y=garrison.attributes['x'].value,garrison.attributes['y'].value
			garrisonId = self.db.getUserPlanetId(x,y)
			for queueUnit in garrison.getElementsByTagName('c-u'):
				cu = convertDict(queueUnit.attributes, {'done':'done', 'bc':'class','id':'id'})
				cu['garrison_id']=garrisonId
				self.db.addObject('garrison_queue_unit', cu)
			for unit in garrison.getElementsByTagName('u'):
				u = convertDict(unit.attributes, {'hp':'hp', 'bc':'class','id':'id'})
				u['garrison_id']=garrisonId
				self.db.addObject('garrison_unit', u)
				
		userFleets = node.getElementsByTagName("fleets")
		fleets = userFleets[0].getElementsByTagName("fleet")

		fleetDict = {'x':'x','y':'y','id':'id','fleet-id':'id','player-id':'owner_id','from-x':'from_x','from-y':'from_y','tta':'tta','turns-till-arrival':'tta','name':'name'}		
		for fleet in fleets:
			f = convertDict(fleet.attributes, fleetDict)
			f['owner_id'] = player['id']
			self.db.addObject('fleet',f)
			
			for unit in fleet.getElementsByTagName("u"):
				udict = {'hp':'hp', 'bc':'class','id':'id'}
				u = convertDict(unit.attributes, udict)
				u['fleet_id'] = f['id']
				self.db.addObject('unit', u)
			
		allienFleets = node.getElementsByTagName("allien-fleets")
		for fleet in allienFleets[0].getElementsByTagName("allien-fleet"):
			f = convertDict(fleet.attributes, fleetDict)
			self.db.addObject('fleet',f)
			
			for unit in fleet.getElementsByTagName('allien-ship'):
				u = convertDict(unit.attributes, {'id':'id','class-id':'class'})#,'carapace':'carapace','weight':'weight'})
				try:
					u['fleet_id']=f['id']
				except KeyError:
					log.error('fleet not found %s'%(f,))
					continue
				self.db.addObject('unit',u)
				p = convertDict(unit.attributes, {'class-id':'id', 'carapace':'carapace','weight':'weight'})
				self.db.addObject('proto',p)

		players = node.getElementsByTagName('diplomacy')
		for player in players[0].getElementsByTagName('rel'):
			d = convertDict(player.attributes, {'player':'id', 'name':'name'})
			if not self.db.getPlayer(d['id']):
				self.db.addObject('player', d)
			
		return True

	def unpack(self, fileIn, fileOut):
		f =  gzip.open(fileIn,'rb')
		with open(fileOut, 'wb') as out:
			out.write(f.read())
		
		f.close()
		
	def loadGalaxySizes(self):		
		with open(os.path.join(self.conf.dir, 'img_size.txt'), 'rb') as f:
			for line in f:
				for i,s in enumerate(line):
					self.db.addObject('planet', {'x':l,'y':i,'s':s*10})

class AsyncLoader(Thread):
	def __init__(self, cb, conf):
		Thread.__init__(self)
		self.cb = cb
		self.args = []
		self.conf = conf
		
	def run(self):
		log.info('async loader started')
		for arg in self.args:
			self.query(arg)
		wx.PostEvent(self.cb, LoaderEvent(attr1=True, attr2=None))
		
	def query(self, args):
		log.info('async-loader executing query %s'%(args,))
		conn = httplib.HTTPConnection(self.conf.s['network']['host'])
		conn.set_debuglevel(int(self.conf.s['network']['debug']))
		conn.request(args['query_type'], args['query'], args['opts'])
		r = conn.getresponse()
		if r.status != 200:
			wx.PostEvent(self.cb, Report(attr1=False, attr2='%s failed: %s'%(args['outpath'],r.reason)))
			return False

		log.info('req, ok, reading body')
		with open(args['outpath'],'wb') as f:
			f.write(r.read())

		log.info('response read, closing connection')
		#don't forget to close http connection
		conn.close()
		wx.PostEvent(self.cb, LoaderEvent(attr1=False, attr2=args['outpath']))
		return True
	
	def recvUserInfo(self, loginInfo, req, outdir):
		q = '/frames/empire_info/on/%s/asxml/'%(req,)
		o = 'login=%s&pwd=%s&action=login'%(urllib.quote(loginInfo[0]).encode('utf-8'),urllib.quote(loginInfo[1]).encode('utf-8')) 
		
		self.queueQuery(query=q, opts=o, query_type='POST', outpath=os.path.join(outdir, '%s_%s.xml.gz'%(loginInfo[0], req)))
		
	def recvActionsReply(self, loginInfo, actions, outdir):
		q = '/frames/perform_x_actions/on/1/asxml/'
		o = 'login=%s&pwd=%s&action=login&xactions=%s'%(loginInfo[0], loginInfo[1], actions)
		#o = 'login=%s&pwd=%s&action=login&xactions=%s'%(urllib.quote(loginInfo[0]).encode('utf-8'),urllib.quote(loginInfo[1]).encode('utf-8'),urllib.quote(actions).encode('utf-8'))
		
		self.queueQuery(query=q, opts=o, query_type='POST', outpath=os.path.join(outdir, '%s_%s.xml.gz'%(loginInfo[0], 'xactions')))
	
	def recvFile(self, q, out):		
		self.queueQuery(query=q, opts=None, query_type='GET', outpath=out)	
	
	def queueQuery(self, *opts, **kvo):
		self.args.append(kvo)

import csv

def planetsFromCSV(file):
	data = csv.reader(open(file,"rb"))
	for row in data:
		print row
