import xml.sax
import logging
import db
import serialization
import os
import os.path
import config
import util

log = logging.getLogger('dclord')
#h = logging.StreamHandler()
#formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
#h.setFormatter(formatter)
#log.addHandler(h)
#log.setLevel(logging.DEBUG)

def getAttrs(src, conv):
	d={}
	for attr in src.keys():
		if attr in conv:
			d[conv[attr]]=src[attr]
	return d

#<dc user="" id="" turn="" turn-n="" worldsize="1000" 

class XmlHandler(xml.sax.handler.ContentHandler):
	
	NodeDC = 'dc'
	UserInfo = 'this-player'
	UserPlanets = 'user-planets'
	Planet = 'planet'
	
	def __init__(self):
		xml.sax.handler.ContentHandler.__init__(self)
		self.user = {}
		self.read_level = None

	def startElement(self, name, attrs):
		if XmlHandler.NodeDC == name:
			self.user.update( getAttrs(attrs, {'user':'name', 'id':'id', 'turn-n':'turn'}) )
		elif XmlHandler.UserInfo == name:
			self.user.update( getAttrs(attrs, {'homeworldx':'hw_x', 'homeworldy':'hw_y', 'race-id':'race_id', 'login':"login"}) )
		elif XmlHandler.UserPlanets == name:
			self.read_level = XmlHandler.UserPlanets
		elif XmlHandler.Planet == name:
			data = getAttrs(attrs, {'x':'x', 'open':'is_open', 'owner-id':'owner_id', 'y':'y', 'name':'name','o':'o','e':'e','m':'m','t':'t','temperature':'t','s':'s','surface':'s'})
			if XmlHandler.UserPlanets == self.read_level:
				data['owner_id'] = self.user['id']
			db.setData('planet', data)


	def endElement(self, name):
		if name==XmlHandler.UserInfo:
			db.setData('user', self.user)

def load_xml(path):
	p = xml.sax.make_parser()
	p.setContentHandler(XmlHandler())
	p.parse( open(path) )

def processRawData(path):
	log.debug('processing raw data %s'%(path,))
	xml_dir = os.path.join(config.options['data']['path'], config.options['data']['raw-xml-dir'])
	util.assureDirExist(xml_dir)
	base = os.path.basename(path)
	xml_path = os.path.join(xml_dir, base[:-3])
	util.unpack(path, xml_path)
	load_xml(xml_path)

def processAllUnpacked():
	xml_dir = os.path.join(config.options['data']['path'], config.options['data']['raw-xml-dir'])
	log.debug('processing all found data at %s'%(xml_dir,))
	at_least_one = False
	for file in os.listdir(xml_dir):
		if not file.endswith('.xml'):
			continue
		log.debug('loading %s'%(file,))
		load_xml( os.path.join(xml_dir, file) )
		at_least_one = True
	if at_least_one:
		serialization.save()
	
