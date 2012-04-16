import xml.sax
import logging
import db
import serialization
import os
import os.path

log = logging.getLogger('dclord')
h = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
h.setFormatter(formatter)
log.addHandler(h)
log.setLevel(logging.DEBUG)

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

def load_user_data(user_login):
	path = '/tmp/dclord/xml/'
	load_xml(os.path.join(path, user_login+'_all.xml'))
	load_xml(os.path.join(path, user_login+'_known_planets.xml'))


def load_all():
	load_user_data('xarquid')
	load_user_data('bogolt')
	load_user_data('gobbolt')
	load_user_data('overmind')
	load_user_data('ghost_5')
	load_user_data('million')

	serialization.save()
	

serialization.load()

import time
time.sleep(10)
