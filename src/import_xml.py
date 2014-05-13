import xml.sax
import store
import os
import util
import shutil
import logging
import config

log = logging.getLogger('dclord')

def get_coord(obj):
	x = obj['x']
	y = obj['y']
	if type(x) is int:
		return x,y
	return int(x), int(y)

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

def safeRemove(array, keys):
	for key in keys:
		if key in array:
			del array[key]

class XmlHandler(xml.sax.handler.ContentHandler):
	
	NotLoggedInError = 'not-logged-in'
	
	StatusOk = 0
	StatusTurnInProgress = 1
	StatusAuthError = 2
	StatusError = 3
	
	def __init__(self, db = None):
		xml.sax.handler.ContentHandler.__init__(self)

		self.user_id = 0
		self.user = {}
		self.parent = None
		self.error_code = 0
		self.error_text = ''
		self.parent_id = 0
		self.parent_coord = None
		self.store = db if db else store.store
		#self.data_type = None
		
	def startElement(self, name, attrs):
		if 'dc' == name:
			self.user = getAttrs(attrs, {'user':'name', 'id':'user_id', 'turn-n':'turn', 'main-res':'resource_main', 'second-res':'resource_secondary', 'money':'money'})
			self.user_id = int(self.user['user_id'])

			
			args = attrs['this-url'].split('/')
			if args:
				self.user['request'] = args[-1]
				#self.data_type = 
			
			# all info read, erase everything related to this user
			if attrs['this-url'].endswith('/all/'):
				self.store.clear_user_data(self.user_id)
				
		elif 'errors' == name:
			self.parent = name
		elif 'error' == name and self.parent == 'errors':
			error_code = int(attrs['id'])
		elif 'this-player'==name:
			
			self.user['race_id'] = attrs['race-id']
			# save login ( will be used later, to link user data with it's config info )
			self.user['login'] = attrs['login']
			self.store.add_user(self.user)

			d = getAttrs(attrs, {'homeworldx':'x', 'homeworldy':'y'})
			d['user_id'] = self.user_id
			self.store.add_data('hw', d)
			
		elif 'this-player-race' == name:
			d = getAttrs(attrs, {
				'race-id':'race_id',
				't-delta':'temperature_delta', 
				't-optimal':'temperature_optimal', 
				'race-nature':'resource_nature', 
				'bonus-multiply':'population_growth',
				'industry-nature': 'resource_main',
				'unused-resource': 'resource_secondary',
				'bonus-speed': 'modifier_fly',
				'bonus-build-war': 'modifier_build_war',
				'bonus-build-peace': 'modifier_build_peace',
				'bonus-iq': 'modifier_science',
				#'bonus-surface': 'modifier_surface',
				'bonus-stealth': 'modifier_stealth',
				'bonus-detectors': 'modifier_detection',
				'bonus-mining': 'modifier_mining',
				'bonus-price': 'modifier_price',
				#'bonus-ground-units': 'modifier_build_ground',
				#'bonus-space-units': 'modifier_build_space',
				'race-name':'name'
					})
			d['user_id'] = self.user_id
			self.store.add_data('race', d)
		
		elif 'user-planets' == name:
			self.parent = 'user-planets'
		elif 'planet' == name:
			
			if 'user-planets' == self.parent:
				data = getAttrs(attrs, {'x':'x', 'y':'y', 'name':'name','o':'o','e':'e','m':'m','t':'t','temperature':'t','s':'s','surface':'s', 'corruption':'corruption', 'population':'population'})
				if 'hidden' in attrs:
					data['is_open'] = not int(attrs['hidden'])
				data['user_id'] = self.user_id
				self.store.add_user_planet(data)
			else:
				# ok, this is known planet
				data = getAttrs(attrs, {'x':'x', 'y':'y', 'owner-id':'user_id', 'name':'name','o':'o','e':'e','m':'m','t':'t','s':'s','turn':'turn'})
				save_load.load_geo_size_at((int(data['x']), int(data['y'])))
				self.store.update_planet(data)
				
				if 'open' in attrs and 1==int(attrs['open']):
					# do not care about planet
					data['user_id'] = self.user_id
					self.store.add_open_planet(data)
					
		elif 'fleets' == name:
			self.parent = 'fleets'
		elif 'allien-fleets' == name:
			self.parent = 'allien-fleets'
		elif name in ['fleet', 'allien-fleet']:
			fleetDict = {'x':'x','y':'y','id':'fleet_id','in-transit':'in_transit','fleet-id':'fleet_id','player-id':'user_id','from-x':'from_x','from-y':'from_y','name':'name', 'tta':'tta', 'turns-till-arrival':'tta', 'hidden':'is_hidden'}
			data = getAttrs(attrs, fleetDict)
			self.parent_id = data['fleet_id'] if 'fleet_id' in data else 0
			table = 'fleet'
			if 'in_transit' in data and 1==int(data['in_transit']):
				table = 'flying_fleet'
				
			if 'tta' in data:
				data['arrival_turn'] = int(self.user['turn']) + int(data['tta'])

			if 'fleet' == name:
				#ok, this is ours fleet
				data['user_id']=self.user_id
				
				self.store.add_data(table, data)
			elif 'allien-fleet' == name:
				self.store.add_data('alien_'+table, data)
				
		elif 'u' == name:
			data = getAttrs(attrs, {'bc':'proto_id', 'id':'unit_id', 'hp':'hp'})
			
			if self.parent == 'fleets':
				self.store.add_fleet_unit(self.parent_id, data)
			elif self.parent == 'harrison':
				data['x'], data['y'] = self.parent_coord
				self.store.add_garrison_unit(data)
		elif 'c-u' == name:
			data = getAttrs(attrs, {'bc':'proto_id', 'id':'unit_id', 'hp':'hp', 'done':'done', 'inproc-order':'build_order'})
			data['x'] = self.parent_coord[0]
			data['y'] = self.parent_coord[1]
			self.store.add_data('garrison_queue_unit', data)
		elif 'allien-ship' == name:
			data = getAttrs(attrs, {'class-id':'class', 'id':'unit_id', 'weight':'weight', 'carapace':'carapace', 'color':'color'})
			data['fleet_id'] = self.parent_id
			self.store.add_data('alien_unit', data)
		elif 'harrison' == name:
			self.parent_coord = int(attrs['x']), int(attrs['y'])
			self.parent = name
		elif 'building_class' == name:
			data = getAttrs(attrs, {'building-id':"proto_id", 'name':'name', 'description':'description', 'is-war':"is_war", 'support-second':"support_second", 'bomb-dr':"defence_bomb", 'transport-capacity':"transport_capacity", 'is-transportable':"is_transportable", 'bomb-number':"bomb_number", 'fly-range':"fly_range", 'bonus-m':"bonus_m", 'is-ground-unit':"is_ground_unit", 'weight':"weight", 'scan-strength':"scan_strength", 'laser-dr':"defence_laser", 'laser-ar':"aim_laser", 'serial':"is_serial", 'carapace':"carapace", 'bonus-surface':"bonus_s", 'laser-damage':"damage_laser", 'offensive':"is_offensive", 'is-building':"is_building", 'is-space-ship':"is_spaceship", 'build-speed':"build_speed", 'detect-range':"detect_range", 'maxcount':"max_count", 'class':"class", 'cost-main':"cost_main", 'stealth-lvl':"stealth_level", 'bonus-o':"bonus_o", 'requires-pepl':"require_people", 'bomb-damage':"damage_bomb", 'bomb-ar':"aim_bomb", 'cost-money':"cost_money", 'req-tehn-level':"require_tech_level", 'color':"color", 'fly-speed':"fly_speed", 'support-main':"support_main", 'bonus-e':"bonus_e", 'carrier-capacity':"carrier_capacity", 'bonus-production':"bonus_production", 'laser-number':"laser_number", 'cost-pepl':"cost_people", 'cost-second':"cost_second", 'hit-points':"hp"})
			data['user_id'] = self.user_id
			self.parent_id = data['proto_id']
			self.parent = name
			self.store.add_data('proto', data)
		elif 'actions-requested' == name:
			self.parent = name
		elif 'act' and self.parent == 'building_class':
			data = getAttrs(attrs, {'action':'proto_action_id', 'maxcount':'max_count', 'cost-pepl':"cost_people", 'cost-main':"cost_main", 'cost-money':"cost_money", 'cost-second':"cost_second", 'planet-can-be':"planet_can_be"})
			data['proto_id'] = self.parent_id
			self.store.add_data('proto_action', data)
		elif 'rel' == name:
			data = getAttrs(attrs, {'player':'other_user_id', 'name':'name', 'type':'relation'})
			self.store.add_user_info(data['other_user_id'], data['name'])
			data['user_id'] = self.user_id
			self.store.add_data('diplomacy', data)
		elif 'act' == name and not self.parent:
			ret_id = attrs['return-id'] if 'return-id' in attrs else None
			self.store.add_action_result(attrs['id'], unicode(attrs['result'])==u'ok', ret_id)
				
	def endElement(self, name):
		if name in ['user-planets', 'fleets', 'allien-fleets', 'harrison', 'building_class', 'actions-requested']:
			self.parent = None
			self.parent_id = 0
			self.parent_coord = None
			
def load_xml(path):
	print 'load xml %s'%(path)
	p = xml.sax.make_parser()
	handler = XmlHandler()
	p.setContentHandler(handler)
	p.parse( open(path) )
	return handler.user

def processRawData(path):
	log.debug('processing raw data %s'%(path,))
	xml_dir = os.path.join(util.getTempDir(), config.options['data']['raw-xml-dir'])
	util.assureDirExist(xml_dir)
	base = os.path.basename(path)
	xml_path = os.path.join(xml_dir, base[:-3])
	util.unpack(path, xml_path)
	return load_xml(xml_path)

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
			p = os.path.join(xml_dir, file)
			load_xml( p )
			at_least_one = True
		if at_least_one:
			save_load.save()
	except OSError, e:
		log.error('unable to load raw data: %s'%(e,))



import unittest
import save_load

class TestXmlImport(unittest.TestCase):
	def setUp(self):
		pass

	def test_import_xml(self):
		
		user = load_xml('/tmp/dclord/raw_xml/niki_all.xml')
		user_id = user['user_id']
		load_xml('/tmp/dclord/raw_xml/niki_known_planets.xml')
		
		#save_load.save_user_data(user_id, '/tmp/dclord/out/')
		save_load.save_data('/tmp/dclord/out/')
		
		
		
		#print store.store.get_governers(user_id)
		
if __name__ == '__main__':
	unittest.main()
