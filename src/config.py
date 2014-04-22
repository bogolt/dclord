import wx
import platform
import os
import os.path
import ConfigParser
import codecs
import logging
import util
import codecs
import json

log = logging.getLogger('dclord')

class UnicodeConfigParser(ConfigParser.RawConfigParser):
	'big thanks: http://s-c.me/21655/s   http://habrahabr.ru/post/119405/'
	def __init__(self, defaults=None, dict_type=dict):
		ConfigParser.RawConfigParser.__init__(self, defaults, dict_type)

	def write(self, fp):
		"""Fixed for Unicode output"""
		if self._defaults:
			fp.write("[%s]\n" % DEFAULTSECT)
			for (key, value) in self._defaults.items():
				if type(value) is str or type(value) is unicode:
					fp.write("%s = %s\n" % (key, value.decode('utf8').replace('\n', '\n\t')))
				else:
					fp.write("%s = %s\n" % (key, value))
			fp.write("\n")
		for section in self._sections:
			fp.write("[%s]\n" % section)
			for (key, value) in self._sections[section].items():
				if key != "__name__":
					if type(value) is str or type(value) is unicode:
						fp.write("%s = %s\n" %(key, value.decode('utf8').replace('\n','\n\t')))
					else:
						fp.write("%s = %s\n" %(key, value))
		fp.write("\n")

	# This function is needed to override default lower-case conversion
	# of the parameter's names. They will be saved 'as is'.
	def optionxform(self, strOut):
		return strOut


def getOptionsDir():
	conf_dir = 'dclord' if 'Windows' == platform.system() else '.config/dclord'
	return os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), conf_dir)

users = {}
user_id_dict = {}
options = {
		'data':{
			'backup-dir':'backup',
			'path': os.path.join(getOptionsDir(), 'data'),
			'raw-dir':'raw',
			'raw-xml-dir':'raw_xml',
			'images':'img/buildings',
			'geo-size':'image_size_map',
			'known_planets':1,
			'load_known_planets':1,
			'sync_path':''
			},
		'network':{
		  'host':'www.the-game.ru',
		  'debug':2
		 },
		 'user':{'nick':''},
		'map':{
		 'coordinate_color':'#000000',
		 'offset_pos_x':1,
		 'offset_pos_y':1,
		 'cell_size':1,
		 'window_size_x':600,
		 'window_size_y':500,
		 'own_fleet_color':'#dd0000',
		 'own_flying_fleet_color':'#deeeee',
		 'fleet_color':'#dd0ff0',
		 'flying_fleet_color':'#deeeff',
		 'own_fleet_route_color':'#0000ff',
		 'fleet_route_color':'#00ff00',
		 'planet_color':'#0000dd',
		 'planet_inhabited_color':'#aadd00',
		 'planet_owned_color':'#aa2200',
		 'planet_uninhabited_color':'#000000',
		 'planet_selected_user_color':'#fdab00',
		 'planet_route_possible_color':'#ffdd00',
		 'route_test_color':'#dfdd00',
		 'route_found_color':'#00ff00',
		 'route_direct_color':'#ff0000',
		 'draw_geo':0,
		 
		 'comma':0
		 
		 },
		 'window':
			{'width':400,
			'height':500,
			'is_maximized':0,
			'pane-info':'',
			'last':0
			},
		 'filter':
			{
			'inhabited_planets':0,
			'fleets':1
			}
		}

config_file_name = 'dclord2.json'
users_file_name = 'users.cfg'
def loadOptions():
	global options
	global options_default
	
	print 'loading opts from %s'%(getOptionsDir(),)
	path = os.path.join(getOptionsDir(), config_file_name)
	if not os.path.exists(path):
		return
		
	with open( path, 'rt') as f:
		data = json.loads(f.read())
		
	global options
	options.update(data)

def saveOptions():
	path = os.path.join(getOptionsDir(), config_file_name)
	global options
	with open( path, 'wt') as f:
		f.write( json.dumps(options, indent=4) )

def loadAccounts():
	config = UnicodeConfigParser()
	try:
		config.readfp(codecs.open(os.path.join(getOptionsDir(), users_file_name), 'r', 'utf8'))
	except IOError as e:
		print 'Error loading accounts: %s'%(e,)
		return
	
	global users
	global user_id_dict
	for u in config.sections():
		acc = {}
		for k,v in config.items(u):
			acc[k] = v
		if not 'login' in acc:
			continue
		
		print 'loading account %s'%(acc['login'],)
		users[acc['login']] = acc
		if 'id' in acc and acc['id']:
			user_id_dict[int(acc['id'])] = acc

def set_user_id(login, user_id):
	global users
	global user_id_dict
	acc = users[login]
	acc['id'] = user_id
	user_id_dict[int(user_id)] = acc

def saveUsers():
	conf = UnicodeConfigParser()
	global users

	for u,p in users.items():
		conf.add_section(u)
		for k,v in p.items():
			conf.set(u, k, v)

	path = os.path.join(getOptionsDir(), users_file_name)
	util.assureDirExist(getOptionsDir())
	try:
		with open(os.path.join(getOptionsDir(), users_file_name), 'wt') as configfile:
			conf.write(configfile)
	except IOError, err:
		log.error("unable to save users file: %s"%(err,))

def loadAll():
	global options
	#options['data']['path'] = os.path.join(getOptionsDir(), options['data']['dir'])
	if not os.path.exists(options['data']['path']):
		os.makedirs(options['data']['path'])
	loadAccounts()
	loadOptions()
	
def addAccount(login, password):
	global users
	users[login] = {'login':login, 'password':password}
	saveUsers()

def removeAccount(login):
	global users
	del users[login]
	saveUsers()

def accounts():
	global users
	for acc in users.values():
		yield acc

def not_used_setUserId(login, id):
	global users
	global user_id_dict
	if not login in users:
		users[login] = {'login':login}
		
	u = users[login]
	if 'id' in u and int(u['id']) == int(id):
		return
	u['id'] = id
	user_id_dict[int(id)] = users[login]
	log.info('store user id %s for user %s'%(id, login))
	saveUsers()
	
