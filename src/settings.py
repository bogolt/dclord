import wx
import ConfigParser
import os.path
import logging
from zipfile import ZipFile
from tempfile import gettempdir
from loader import AsyncLoader

class UnitImageList:
	def __init__(self, imgDir):
		self.imgList = wx.ImageList(20,20)
		self.imgKeys = {}
		self.dir = imgDir

	def getImageKey(self, proto):
		pKey = (proto.id,proto.color)
		if pKey in self.imgKeys.keys():
			return self.imgKeys[pKey]
		
		pt = ['%s.gif'%(proto.id,),'carps/%s_%s.gif'%(proto.carapace,proto.color)]
		for p in pt: 
			imgPath = os.path.join(self.dir, p)
			if os.path.exists(imgPath):
				key = self.imgList.Add(wx.Image(imgPath).Rescale(20,20).ConvertToBitmap())
				self.imgKeys[pKey] = key
				#print 'key %s %s loaded for class %s, cara %s'%(key, imgPath, proto.id, proto.carapace)
				return key

		# the only bug can happen if static.zip is not downloaded yet, but it will be fixed after
		#  app restart
		print 'not found for %s %s'%(proto.id,proto.color)
		self.imgKeys[pKey] = None
		return None

def assurePathExist(path):
	if not os.path.exists(path):
		os.mkdir(path)

def toDict(pairList):
	d = {}
	for pair in pairList:
		d[pair[0]]=pair[1]
	return d

class Settings:
	def __init__(self, callback):
		self.dir = wx.StandardPaths.Get().GetUserConfigDir() + '/.config/dclord'
		assurePathExist(self.dir)
		self.path = os.path.join(self.dir, 'dclord.cfg')
		self.usersPath = os.path.join(self.dir, 'users.cfg')
		self.callback = callback
		self.panes = ''
		self.users = {} 
		self.debug = False
		self.pathTemp = os.path.join(gettempdir(),'dclord')
		assurePathExist(self.pathTemp)
				
		self.pathArchive = os.path.join(self.pathTemp, 'archive')
		assurePathExist(self.pathArchive)
		
		self.pathXml = os.path.join(self.pathTemp,'xml')
		assurePathExist(self.pathXml)
		
		self.imageList = UnitImageList(os.path.join(self.dir, 'static/img/buildings'))
		
		self.s = {
			'network':{
								'host':'www.the-game.ru',
								'debug':0
			},'update':{
							'disable':0,
							'debug':0,
							'host':'xor.undo.it',
							'user':'dclord_updates',
							'password':'the-game-rules'
			},'map':{
							'bg_color':'#444444',
							'greed_color':'white',
							'fleet_route_color':'white',
							'fleet_color':'white',
							'own_planet_color':'magenta',
							'planet_owner_text_color':'white',
							'inhabited_planet_color':'#8880DD',
							'planet_color':'grey',
							'last_pos_x':-1,
							'last_pos_y':-1,
							'grid_color':'darkgrey',
							'coord_color':'white',
							'add_debug_planets':0
			}, 'log':{
								'log':0
			}
		}
		
		self.load()
		
	def load(self):
		conf = ConfigParser.RawConfigParser()
		conf.read(self.path)

		for s in conf.sections():
			if s in self.s:
				self.s[s].update(conf.items(s))
			else:
				self.s[s] = toDict(conf.items(s))

		#old compatibility code, remove it after everyone using versions prior to 0.1.4 will update
		for k,v in self.s.items():
			if not k.startswith('user_'):
				continue
			self.users[v['login']] = v['password']

		#now remove user_ entries from 
		for k in self.users.keys():
			del self.s['user_%s'%(k,)]

		###################
		###################
		
		us = ConfigParser.RawConfigParser()
		if not us.read(self.usersPath):
			self.saveUsers()
			#and resave basic config to remove old 'user_' entries from it
			self.save()
		else:
			for s in us.sections():
				u = us.get(s, 'login')
				p = us.get(s, 'password')
				self.users[u]=p

		if not os.path.exists(os.path.join(self.dir, 'static')):
			self.getStatic()

	def unpackStatic(self):
		staticArchive = os.path.join(self.dir, 'static.zip')
		if not os.path.exists(staticArchive):
			return False
		z = ZipFile(staticArchive, 'r')
		#TODO: dangerous func ( can copy file to system dir )
		z.extractall(os.path.join(self.dir, 'static'))
		return True

	def getStatic(self):
		if self.unpackStatic():
			return
		
		al = AsyncLoader(self.callback, self)
		al.recvFile('/static/static.zip', os.path.join(self.dir, 'static.zip'))
		al.start()
	
	def saveUsers(self):
		conf = ConfigParser.RawConfigParser()

		for u,p in self.users.items():
			conf.add_section(u)
			conf.set(u, 'login', u)
			conf.set(u, 'password', p)

		with open(self.usersPath, 'wb') as configfile:
			conf.write(configfile)
					
	def save(self):
		conf = ConfigParser.RawConfigParser()
		
		for sect,s in self.s.items():
			conf.add_section(sect)
			for k,v in s.items():
				conf.set(sect, k, v)

		with open(self.path, 'wb') as configfile:
			conf.write(configfile)
