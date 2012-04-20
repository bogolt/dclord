import wx
import platform
import os
import os.path
import ConfigParser
import logging

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
			'raw-xml-dir':'raw_xml'
			
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
		 'fleet_color':'#dd0000'
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
	with open(path, 'wb') as configfile:
		conf.write(configfile)

def loadAccounts():
	config = ConfigParser.ConfigParser()
	config.read(os.path.join(getOptionsDir(), 'users.cfg'))
	global users
	for u in config.sections():
		acc = {}
		for k,v in config.items(u):
			acc[k] = v
		users[acc['login']] = acc

def loadAll():
	global options
	options['data']['path'] = os.path.join(getOptionsDir(), options['data']['dir'])
	loadAccounts()
	loadOptions()

def accounts():
	global users
	for acc in users.values():
		yield acc
