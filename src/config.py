import wx
import csv
import platform
import os
import os.path
import ConfigParser
import codecs
import logging
import util
import codecs
import json
import time

log = logging.getLogger('dclord')

def getOptionsDir():
	conf_dir = 'dclord' if 'Windows' == platform.system() else '.config/dclord'
	return os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), conf_dir)

users = {}
user_id_dict = {}
options = {
		'data':{
			'backup-dir':'backup',
			'path': None,
			'raw-dir':'raw',
			'raw-xml-dir':'raw_xml',
			'images':'img/buildings',
			'geo-size':'image_size_map',
			'known_planets':1,
			'load_known_planets':1,
			'sync_path':'',
			'sync_key':None
			},
		'network':{
		  'host':'www.the-game.ru',
		  'debug':0
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
		 'planet_uninhabited_color':'#888888',
		 'planet_selected_user_color':'#fdab00',
		 'planet_route_possible_color':'#ffdd00',
		 'route_test_color':'#dfdd00',
		 'route_found_color':'#00ff00',
		 'route_direct_color':'#ff0000',
		 'draw_geo':0,
		 'show_good':0,
		 
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
			'inhabited_planets':0, #only
			'size_planets':1,
			'owned_planets':0,
			'access_planets':0,
			
			#'planet_owner_type':'any', #can be 'owned', 'access', 'ihabited',
			'fleets':1
			}
		}


config_file_name = 'dclord2.json'
users_file_name_old = 'users.cfg'
users_file_name_old2 = users_file_name_old + '.old'
users_file_name = 'users.json'
def loadOptions():
	global options
	global options_default
		
	#print 'loading opts from %s'%(getOptionsDir(),)
	path = os.path.join(getOptionsDir(), config_file_name)
	if not os.path.exists(path):
		return
		
	with open( path, 'rt') as f:
		data = json.loads(f.read())
		
	for k,v in data.iteritems():
		options[k].update(v)
		
	if not options['data']['sync_key']:
		options['data']['sync_key'] = str(time.time())

def saveOptions():
	path = os.path.join(getOptionsDir(), config_file_name)
	global options
	with open( path, 'wt') as f:
		f.write( json.dumps(options, indent=4) )
	
def loadAccounts():

	new_name = os.path.join(getOptionsDir(), users_file_name)
	if not os.path.exists(new_name):
		return
		
	with open(new_name) as f:
		user_list = json.loads(f.read())
		
	global users
	for u in user_list:
		user_id = None
		if 'id' in u:
			user_id = int(u['id'])
			u['id'] = user_id
			user_id_dict[user_id] = u
		if 'login' in u and 'password' in u:
			users[u['login']] = u

def set_user_id(login, user_id):
	global users
	global user_id_dict
	acc = users[login]
	acc['id'] = user_id
	user_id_dict[int(user_id)] = acc

def saveUsers():
	path = os.path.join(getOptionsDir(), users_file_name)
	with open(path, 'wt') as f:
		f.write(json.dumps([user for user in users.itervalues()], indent=4))

def loadAll():
	global options
	
	if not options['data']['path']:
		options['data']['path'] = os.path.join(getOptionsDir(), 'data')

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

def has_user(login):
	return login in users
	
