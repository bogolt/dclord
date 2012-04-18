import wx
import platform
import os
import os.path
import ConfigParser

accs = {}
options = {}

def getOptionsDir():
	conf_dir = 'dclord' if 'Windows' == platform.system() else '.config/dclord'
	return os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), conf_dir)

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
	global accs
	for u in config.sections():
		acc = {}
		for k,v in config.items(u):
			acc[k] = v
		accs[acc['login']] = acc

def loadAll():
	loadAccounts()
	loadOptions()

def accounts():
	global accs
	for acc in accs.values():
		yield acc
