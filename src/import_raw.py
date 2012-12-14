import xml.sax
import logging
import db
import serialization
import os
import os.path
import config
import util

log = logging.getLogger('dclord')

def get_attr(attrs, name, value_type=int):
	if name in attrs.keys():
		return value_type(attrs[name])
	return None

def getAttrs(src, conv):
	d={}
	for attr in src.keys():
		if attr in conv:
			d[conv[attr]]=src[attr]
	return d

#<dc user="" id="" turn="" turn-n="" worldsize="1000" 

def safeRemove(array, keys):
	for key in keys:
		if key in array:
			del array[key]

class XmlHandler(xml.sax.handler.ContentHandler):
	
	NodeDC = 'dc'
	UserInfo = 'this-player'
	UserPlanets = 'user-planets'
	Planet = 'planet'
	Fleet = 'fleet'
	AlienFleet = 'allien-fleet'
	Unit = 'u'
	AlienUnit = 'allien-ship'
	Garrison = 'harrison'
	BuildingClass = 'building_class'
	BuildingClassActionsList = 'actions'
	BuildingClassAction = 'act'
	Iframe = 'iframe'
	PerformAction = 'act'
	
	NotLoggedInError = 'not-logged-in'
	
	def __init__(self):
		xml.sax.handler.ContentHandler.__init__(self)
		self.user = {}
		self.read_level = None
		self.obj_id = None
		self.pos = None
		self.turn = None
		self.iframe = False
		self.parent_attrs = {}
		self.actions = []

	def startElement(self, name, attrs):
		if XmlHandler.NodeDC == name:
			self.user.update( getAttrs(attrs, {'user':'name', 'id':'id', 'turn-n':'turn'}) )
			print 'loaded user %s'%(self.user,)
			if 'turn' in self.user:
				self.turn = int(self.user['turn'])
				db.prepareTurn(self.turn)
				print 'prepare turn %s'%(self.turn,)
				
		elif XmlHandler.NotLoggedInError == name:
			log.error('Not logged in - turn in progress')
		elif XmlHandler.UserInfo == name:
			d = getAttrs(attrs, {'homeworldx':'hw_x', 'homeworldy':'hw_y', 'race-id':'race_id', 'login':"login"})
			self.user.update( d )
			print 'update user %s'%(self.user,)
			db.setData('hw', {'hw_x':d['hw_x'], 'hw_y':d['hw_y'], 'player_id':self.user['id']}, self.turn)
			db.setData('user', {'id':self.user['id'], 'login':d['login'], 'race_id':d['race_id'], 'name':self.user['name']})
			
		elif XmlHandler.UserPlanets == name:
			self.read_level = XmlHandler.UserPlanets
		elif XmlHandler.Planet == name:
			data = getAttrs(attrs, {'x':'x', 'open':'is_open', 'owner-id':'owner_id', 'y':'y', 'name':'name','o':'o','e':'e','m':'m','t':'t','temperature':'t','s':'s','surface':'s', 'age':'age'})
			if XmlHandler.UserPlanets == self.read_level:
				data['owner_id'] = self.user['id']
				#log.info('load owner planet %s'%(data,))
			if 'age' in data:
				#don't need this for now
				#data['turn'] = self.turn - int(data['age'])
				del data['age']
			db.setData('planet', data, self.turn)
		elif XmlHandler.Fleet == name or XmlHandler.AlienFleet == name:
			fleetDict = {'x':'x','y':'y','id':'id','fleet-id':'id','player-id':'owner_id','from-x':'from_x','from-y':'from_y','name':'name', 'tta':'tta', 'turns-till-arrival':'tta', 'hidden':'is_hidden'}
			data = getAttrs(attrs, fleetDict)
			if 'id' in data:
				self.obj_id = int(data['id'])
			else:
				self.obj_id = int(db.nextFleetTempId())
				data['temp_id'] = self.obj_id
			tta = 0
			if 'tta' in data:
				tta = int(data['tta'])
				if tta > 0:
					data['arrival_turn'] = int(self.user['turn'])+tta
				del data['tta']
			if tta == 0:
				safeRemove(data, ['from_x', 'from_y', 'tta'])
			
			if name==XmlHandler.Fleet:
				data['owner_id'] = self.user['id']
			else:
				data['turn'] = self.turn
				
			if tta>0:
				db.setData('incoming_fleet', data, self.turn)
			else:
				db.setData('fleet', data, self.turn)
		elif XmlHandler.Garrison == name:
			self.pos = getAttrs(attrs, {'x':'x', 'y':'y'})
		elif XmlHandler.AlienUnit == name:
			data = getAttrs(attrs, {'class-id':'class', 'id':'id', 'weight':'weight', 'carapace':'carapace', 'color':'color'})
			data['fleet_id'] = self.obj_id
			db.setData('alien_unit', data, self.turn)
		elif XmlHandler.Unit == name:
			data = getAttrs(attrs, {'bc':'class', 'id':'id', 'hp':'hp'})
			if self.obj_id:
				data['fleet_id'] = self.obj_id
				db.setData('unit', data, self.turn)
			elif self.pos:
				data.update(self.pos)
				db.setData('garrison_unit', data, self.turn)
		elif XmlHandler.BuildingClass == name:			
			data = getAttrs(attrs, {'name':'name', 'description':'description', 'is-war':"is_war", 'support-second':"support_second", 'bomb-dr':"defence_bomb", 'transport-capacity':"transport_capacity", 'is-transportable':"is_transportable", 'bomb-number':"bomb_number", 'fly-range':"fly_range", 'bonus-m':"bonus_m", 'is-ground-unit':"is_ground_unit", 'weight':"weight", 'scan-strength':"scan_strength", 'laser-dr':"defence_laser", 'laser-ar':"aim_laser", 'serial':"is_serial", 'carapace':"carapace", 'bonus-surface':"bonus_s", 'laser-damage':"damage_laser", 'offensive':"is_offensive", 'is-building':"is_building", 'is-space-ship':"is_spaceship", 'build-speed':"build_speed", 'detect-range':"detect_range", 'maxcount':"max_count", 'class':"class", 'cost-main':"cost_main", 'stealth-lvl':"stealth_level", 'bonus-o':"bonus_o", 'requires-pepl':"require_people", 'bomb-damage':"damage_bomb", 'bomb-ar':"aim_bomb", 'cost-money':"cost_money", 'req-tehn-level':"require_tech_level", 'color':"color", 'fly-speed':"fly_speed", 'support-main':"support_main", 'building-id':"id", 'bonus-e':"bonus_e", 'carrier-capacity':"carrier_capacity", 'bonus-production':"bonus_production", 'laser-number':"laser_number", 'cost-pepl':"cost_people", 'cost-second':"cost_second", 'hit-points':"hp"})
			data['owner_id'] = self.user['id']
			self.parent_attrs = data
			db.setData('proto',data)
			
			#if 'name' in data:
			#	#log.info('specific data: %s'%(data,))
		elif XmlHandler.BuildingClassAction == name and self.parent_attrs:
			data = getAttrs(attrs, {'action':'id', 'maxcount':'max_count', 'cost-pepl':"cost_people", 'cost-main':"cost_main", 'cost-money':"cost_money", 'cost-second':"cost_second", 'planet-can-be':"planet_can_be"})
			data['proto_id'] = self.parent_attrs['id']
			data['proto_owner_id'] = self.user['id']
			#db.setData('proto_action',data)
		elif XmlHandler.Iframe == name:
			self.iframe = True
		elif XmlHandler.PerformAction == name and self.iframe and False:
			data = getAttrs(attrs, {'id':'id', 'result':'result', 'return-id':'return-id'})
			act_id = data['id']
			result = data['result']=='ok'
			ret_id = data['return-id']
			
			if result:
				self.actions.append( (act_id, ret_id) )
			
	def endElement(self, name):
		if name==XmlHandler.UserInfo:
			pass
			#db.setData('user', self.user)
		elif name==XmlHandler.Fleet or name==XmlHandler.AlienFleet:
			self.obj_id = None
		elif name == XmlHandler.BuildingClass:
			self.parent_attrs = {}
		elif XmlHandler.Garrison == name:
			self.pos = None
		elif XmlHandler.Iframe == name:
			self.iframe = False
		elif XmlHandler.NodeDC:
			if self.actions:
				wx.PostEvent(cb, event.ActionsReply(attr1=self.user, attr2=self.actions))
			
def load_xml(path):
	p = xml.sax.make_parser()
	p.setContentHandler(XmlHandler())
	p.parse( open(path) )

def processRawData(path):
	log.debug('processing raw data %s'%(path,))
	xml_dir = os.path.join(util.getTempDir(), config.options['data']['raw-xml-dir'])
	util.assureDirExist(xml_dir)
	base = os.path.basename(path)
	xml_path = os.path.join(xml_dir, base[:-3])
	util.unpack(path, xml_path)
	load_xml(xml_path)

def processAllUnpacked():
	xml_dir = os.path.join(util.getTempDir(), config.options['data']['raw-xml-dir'])
	util.assureDirClean(xml_dir)
	log.debug('processing all found data at %s'%(xml_dir,))
	at_least_one = False
	try:
		for file in os.listdir(xml_dir):
			if not file.endswith('.xml'):
				continue
			log.debug('loading %s'%(file,))
			load_xml( os.path.join(xml_dir, file) )
			at_least_one = True
		if at_least_one:
			serialization.save()
	except OSError, e:
		log.error('unable to load raw data: %s'%(e,))
