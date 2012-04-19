import wx
import platform
import os
import os.path
import ConfigParser

def getOptionsDir():
	conf_dir = 'dclord' if 'Windows' == platform.system() else '.config/dclord'
	return os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), conf_dir)

users = {}
options = {
		'data':{
			'dir':'data',
			'path':os.path.join(getOptionsDir(), 'data'),
			'raw-dir':'raw',
			'raw-xml-dir':'raw_xml'
			
			},
		'network':{
		  'host':'www.the-game.ru',
		  'debug':2
		 },
		'map':{
		 'last_pos':'(3,5)'
		 }
		}

def loadOptions():
	config = ConfigParser.ConfigParser()
	config.read(os.path.join(getOptionsDir(), 'dclord.cfg'))
	global options
	for s in config.sections():
		opt = {}
		for k,v in config.items(s):
			opt[k] = v
		options.setdefault(s, {}).update(opt)

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
	loadAccounts()
	loadOptions()

def accounts():
	global users
	for acc in users.values():
		yield acc
