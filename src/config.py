import wx
import platform
import os
import os.path
import ConfigParser
import logging
import util

log = logging.getLogger('dclord')

def getOptionsDir():
	conf_dir = 'dclord' if 'Windows' == platform.system() else '.config/dclord'
	return os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), conf_dir)
	
users = {}
options = {
		'data':{
			'dir':'data',
			'path':None,
			'raw-dir':'raw',
			'raw-xml-dir':'raw_xml',
			'images':'images/static/img/buildings'
			
			},
		'network':{
		  'host':'www.the-game.ru',
		  'debug':2
		 },
		'map':{
		 'offset_pos_x':3,
		 'offset_pos_y':3,
		 'cell_size':6,
		 'window_size_x':600,
		 'window_size_y':500,
		 'own_fleet_color':'#dd0000',
		 'own_flying_fleet_color':'#de0000',
		 'fleet_color':'#dd0000',
		 'flying_fleet_color':'#de0000',
		 'own_fleet_route_color':'#0000ff',
		 'fleet_route_color':'#00ff00',
		 'own_planet_color':'#bb00dd',
		 'planet_color':'#0000dd',
		 'planet_inhabited_color':'#ff00dd',
		 'planet_uninhabited_color':'#000000'
		 
		 },
		 'window':
			{'width':400,
			'height':500,
			'is_maximized':0
			},
		 'filter':
			{
			'inhabited_planets':1
			}
		}

config_file_name = 'dclord.cfg'
def loadOptions():
	config = ConfigParser.ConfigParser()
	config.read(os.path.join(getOptionsDir(), config_file_name))
	global options
	for s in config.sections():
		opt = {}
		for k,v in config.items(s):
			opt[k] = v
		options.setdefault(s, {}).update(opt)

def saveOptions():
	conf = ConfigParser.RawConfigParser()
	global options
	for name, sect in options.items():
		conf.add_section(name)
		for k,v in sect.items():
			conf.set(name, k, v)
	path = os.path.join(getOptionsDir(), config_file_name)
	util.assureDirExist(getOptionsDir())
	try:
		with open(path, 'wb') as configfile:
			conf.write(configfile)
	except IOError, err:
		log.error("unable to save config file: %s"%(err,))

def loadAccounts():
	config = ConfigParser.ConfigParser()
	config.read(os.path.join(getOptionsDir(), 'users.cfg'))
	global users
	for u in config.sections():
		acc = {}
		for k,v in config.items(u):
			acc[k] = v
		users[acc['login']] = acc

def saveUsers():
	conf = ConfigParser.RawConfigParser()
	global users

	for u,p in users.items():
		conf.add_section(u)
		for k,v in p.items():
			conf.set(u, k, v)
			
	with open(os.path.join(getOptionsDir(), 'users.cfg'), 'wt') as configfile:
		conf.write(configfile)

def loadAll():
	global options
	options['data']['path'] = os.path.join(getOptionsDir(), options['data']['dir'])
	loadAccounts()
	loadOptions()

def accounts():
	global users
	for acc in users.values():
		yield acc

def setUserId(login, id):
	global users
	u = users[login]
	if 'id' in u and int(u['id']) == int(id):
		return
	u['id'] = id
	log.info('store user id %s for user %s'%(id, login))
	saveUsers()
	
